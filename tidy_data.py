#encoding=utf-8
"""
[x] 根据number里的数据清理出每日数据
    3.1 - 3.17
    3.17 - 3.25
    3.26 - 今 @s
[x] 根据number里的数据清理出区数据
    3.1 - 3.17 by @kf
    3.17 - 3.25
    3.26 - 今 @s
[ ] 还需要把区级别数据写入的判断, 以及清理districts_daily里的数据
[ ] 对25号前的每日数据还有bug（不修了）
"""
import codecs
import re
from os import listdir
import pandas
from config import address_folder, number_folder, macro_file
from config import district_file, address_file
from date_convert import convert_date_string_to_excel_ordinal

def filter_list():
    #确定到底使用哪些文件
    begin = 20220318 #实际可以从3月25日开始
    file_in_dir = listdir(number_folder)
    file_list = []
    for file in file_in_dir:
        if file.find('.') > 0 or int(file) < begin:
            continue
        if int(file) > begin:
            file_list.append(file)
    return file_list

def find_patterns(text, location_pattern, match_pattern, line_num, allow_skip = 0):
    if location_pattern != '':
        line_num = skip_lines(text, location_pattern, line_num)
    values = re.findall(match_pattern, text[line_num])
    if allow_skip:
        if len(values) > 0:
            values = values[0]
        else:
            values = '0'
    else:
        values = values[0]
#    print(text[line_num])
    return line_num, values

def skip_lines(text, location_pattern, line_num):
    backup_line_num = line_num
    try:
        while len(re.findall(location_pattern, text[line_num]))==0:
            line_num += 1
    except:
        line_num = backup_line_num
    return line_num

def cleaning_districts(date_value, text, p = '无症状感染者'):
    """
    3.26 至今
    input: text, 病例/无症状感染者
    output: list of district, source, patient number, district
    3.17-3.25 至今
    output: list of district, source, patient #n, sex, age, district
    """
    source = ['闭环隔离管控', '风险人群筛查', '此前报告的本土无症状感染']
    district_list = []
    for i in source:
        if text.find(i) > 0:
            source = i
    if int(date_value) >= 20220325:
        #0325之后的公告
        pattern = p + '(\d+)，居住于([\u4e00-\u9fa5]{2})[新区|区]'
        patient_string = re.findall(pattern, text)
        if len(patient_string) > 0:
#            print(patient_string)
            for i in range(len(patient_string)):
                last_num, district = patient_string[i]
                if (i == 0):
                    number = int(last_num)
                else:
                    number = int(last_num) - int(patient_string[i-1][0])
            district_list.append((p, district, number))
    elif int(date_value) >= 20220317:
        #317 - 325公告
        pattern = p + '(\d+)，([男｜女])，(\d+)岁，居住于([\u4e00-\u9fa5]{2})[新区|区]'
        patient_string = re.findall(pattern, text)
        if len(patient_string) > 0:
#            print(patient_string)
            for s in patient_string:
                district_list.append((p, *s))
    return district_list

def check_data():
    """
    检查地址的时间方面是否缺失
    """
    address = pandas.read_csv(address_file)
    return True

def get_numbers(f, file):
    """
    return: 市('时间', '确诊', '无症状', '无症状转确诊', '管控内确诊', '管控内无症状',\
        '确诊密接', '无症状密接', '本土医学观察中无症状', '本土在院治疗中', '治愈出院', '重症', '死亡', '解除医学观察\n')    """
    ALLOW_SKIP = 1
    result = 0
    nosymptom_to_patient = '0'
    print(f'reading {file}')
    text = f.readlines()
    district_list = []
    try:
        date_value = file
        line_num = 0
        line_num = skip_lines(text, '市卫健委', line_num) #跳到第一行
        line_num, (patients, nosymptom) = find_patterns(text, '市卫健委', '新增本土新冠肺炎确诊病例(\d+)[例|]和无症状感染者(\d+)例', line_num)  #其中本土无症状感染者102例，境外输入性无症状感染者8例。
        line_num, nosymptom_to_patient = find_patterns(text, '', '(\d+)例确诊病例为此前无症状感染者转归', line_num, ALLOW_SKIP)  #其中本土无症状感染者102例，境外输入性无症状感染者8例。
        line_num, (patient_findallin_control, nosymptom_findallin_control) = find_patterns(text, '', '(\d+)例确诊病例和(\d+)例无症状感染者在隔离管控中', line_num)
        #stage = ['patient', 'cleaning_patient', 'patient_close', 'nosymptom', 'cleaninng_nosymptom', 'nosymptom_close', 'end1', 'end2', 'end3']
        line_num = skip_lines(text, '新增本土新冠肺炎确诊病例', line_num) #确诊
        line_num = skip_lines(text, '病例(\d+)', line_num) #清理病人
        while len(re.findall('密切接触者', text[line_num]))==0: #在密接之前持续清理
            l = cleaning_districts(date_value, text[line_num], '病例')
            if len(l) > 0:
                district_list += l
            line_num += 1
        line_num, patient_close = find_patterns(text, '', '已追踪到以上病例在本市的密切接触者(\d+)', line_num, ALLOW_SKIP) #已追踪到以上病例在本市的密切接触者53人
        line_num = skip_lines(text, '新增本土无症状', line_num) #无症状
        while len(re.findall('密切接触者', text[line_num]))==0: #在密接之前持续清理
            l = cleaning_districts(date_value, text[line_num], '无症状感染者')
            if len(l) > 0:
                district_list += l
            line_num += 1
        line_num, nosymptom_close = find_patterns(text, '', '已追踪到以上无症状感染者在本市的密切接触者(\d+)', line_num, ALLOW_SKIP) #已追踪到以上病例在本市的密切接触者53人
        line_num, leave_nosymptom_control = find_patterns(text, '解除医学观察', '本土无症状感染者(\d+)', line_num, ALLOW_SKIP)  #其中本土无症状感染者102例，境外输入性无症状感染者8例。
        line_num, heal = find_patterns(text, '在院治疗', '治愈出院(\d+)', line_num)  #累计本土确诊707例，治愈出院476例，在院治疗224例，死亡7例。
        line_num, in_hospital = find_patterns(text, '', '在院治疗(\d+)', line_num)  #累计本土确诊707例，治愈出院476例，在院治疗224例，死亡7例。
        line_num, serious = find_patterns(text, '', '重症(\d+)', line_num, ALLOW_SKIP)  #累计本土确诊707例，治愈出院476例，在院治疗224例，死亡7例。
        line_num, dead = find_patterns(text, '', '死亡(\d+)', line_num, ALLOW_SKIP)  #累计本土确诊707例，治愈出院476例，在院治疗224例，死亡7例。
        line_num, nosymptom_control = find_patterns(text, '尚在医学观察中的', '尚在医学观察中的无症状感染者\d+例，其中本土无症状感染者(\d+)', line_num, ALLOW_SKIP)  #尚在医学观察中的无症状感染者8711例，其中本土无症状感染者8674
        #例行筛查确诊	例行筛查无症状
        outside_patient = str(int(patients) - int(nosymptom_to_patient) - int(patient_findallin_control))
        outside_nosymptom = str(int(nosymptom) - int(nosymptom_findallin_control))
        result = (date_value, patients, nosymptom, nosymptom_to_patient, patient_findallin_control, nosymptom_findallin_control,\
                outside_patient, outside_nosymptom, \
                patient_close, nosymptom_close, \
                nosymptom_control, leave_nosymptom_control, in_hospital, heal, serious, dead)
        print(file, result)
    except IndexError as err:
        print(line_num, text[line_num])
        print(err)
        raise
    return result, district_list

if __name__ == '__main__':
    file_list = filter_list()
    w = codecs.open(macro_file, mode = 'w', encoding='utf_8')
    w.write(",".join(('时间', '确诊', '无症状', '无症状转确诊', '管控内确诊', '管控内无症状',\
            '例行筛查确诊', '例行筛查无症状', \
            '确诊密接', '无症状密接', \
            '本土医学观察中无症状', '解除医学观察', '本土在院治疗中', '治愈出院', '重症', '死亡\n')))
    for file in file_list:
        f = codecs.open(number_folder + file, mode = 'r', encoding='utf_8')
        result, district_list = get_numbers(f, file)
        print(district_list)
        w.write(",".join(result) + '\n')
    w.close()
