#encoding=utf-8
#just a placeholder

"""
[] 根据temp/address_daily里的数据汇总到经纬度-地址对应表：经纬度只需查询新增地址
[] 根据number里的数据清理出每日数据
    3.1 - 3.17
    3.17 - 3.25
    3.26 - 今 @s
[] 根据number里的数据清理出区数据
    3.1 - 3.17 by @kf
    3.17 - 3.25
    3.26 - 今 @s
[]
"""
import codecs
import re
from os import listdir

def find_patterns(text, location_pattern, match_pattern, line_number, allow_skip = 0):
    if location_pattern != '':
        line_number = skip_lines(text, location_pattern, line_number)
    values = re.findall(match_pattern, text[line_number])
    if allow_skip:
        if len(values) > 0:
            values = values[0]
        else:
            values = ''
    else:
        values = values[0]
#    print(text[line_number])
    return line_number, values

def skip_lines(text, location_pattern, line_number):
    backup_line_number = line_number
    try:
        while len(re.findall(location_pattern, text[line_number]))==0:
            line_number += 1
    except:
        line_number = backup_line_number
    return line_number

def cleaning_patients(text, text2):
    pass

def get_numbers(f, file):
    """
    ('时间', '确诊', '无症状', '无症状转确诊', '管控内确诊', '管控内无症状',\
        '确诊密接', '无症状密接', '本土医学观察中无症状', '本土在院治疗中', '治愈出院', '重症', '死亡', '解除医学观察\n')    """
    ALLOW_SKIP = 1
    print(f'reading {file}')
    text = f.readlines()
    line_number = 0
    line_number = skip_lines(text, '市卫健委', line_number) #跳到第一行
    line_number, (patients, nosymptom) = find_patterns(text, '市卫健委', '新增本土新冠肺炎确诊病例(\d+)[例|]和无症状感染者(\d+)例', line_number)  #其中本土无症状感染者102例，境外输入性无症状感染者8例。
    line_number, nosymptom_to_patient = find_patterns(text, '', '(\d+)例确诊病例为此前无症状感染者转归', line_number, ALLOW_SKIP)  #其中本土无症状感染者102例，境外输入性无症状感染者8例。
    line_number, (patient_findallin_control, nosymptom_findallin_control) = find_patterns(text, '', '(\d+)例确诊病例和(\d+)例无症状感染者在隔离管控中', line_number)
    #stage = ['patient', 'cleaning_patient', 'patient_close', 'nosymptom', 'cleaninng_nosymptom', 'nosymptom_close', 'end1', 'end2', 'end3']
    line_number = skip_lines(text, '新增本土新冠肺炎确诊病例', line_number) #确诊
    line_number = skip_lines(text, '病例(\d+)', line_number) #清理病人
    while len(re.findall('密切接触者', text[line_number]))==0: #在密接之前持续清理
        cleaning_patients(text[line_number], '确诊')
        line_number += 1
    line_number, patient_close = find_patterns(text, '', '已追踪到以上病例在本市的密切接触者(\d+)', line_number, ALLOW_SKIP) #已追踪到以上病例在本市的密切接触者53人
    line_number = skip_lines(text, '新增本土无症状', line_number) #无症状
    while len(re.findall('密切接触者', text[line_number]))==0: #在密接之前持续清理
        cleaning_patients(text[line_number], '无症状')
        line_number += 1
    line_number, nosymptom_close = find_patterns(text, '', '已追踪到以上无症状感染者在本市的密切接触者(\d+)', line_number, ALLOW_SKIP) #已追踪到以上病例在本市的密切接触者53人
    line_number, leave_nosymptom_control = find_patterns(text, '解除医学观察', '本土无症状感染者(\d+)', line_number, ALLOW_SKIP)  #其中本土无症状感染者102例，境外输入性无症状感染者8例。
    line_number, heal = find_patterns(text, '在院治疗', '治愈出院(\d+)', line_number)  #累计本土确诊707例，治愈出院476例，在院治疗224例，死亡7例。
    line_number, in_hospital = find_patterns(text, '', '在院治疗(\d+)', line_number)  #累计本土确诊707例，治愈出院476例，在院治疗224例，死亡7例。
    line_number, serious = find_patterns(text, '', '重症(\d+)', line_number, ALLOW_SKIP)  #累计本土确诊707例，治愈出院476例，在院治疗224例，死亡7例。
    line_number, dead = find_patterns(text, '', '死亡(\d+)', line_number, ALLOW_SKIP)  #累计本土确诊707例，治愈出院476例，在院治疗224例，死亡7例。
    line_number, (i, nosymptom_control) = find_patterns(text, '尚在医学观察中的', '尚在医学观察中的无症状感染者(\d+)例，其中本土无症状感染者(\d+)', line_number)  #尚在医学观察中的无症状感染者8711例，其中本土无症状感染者8674
    result = (file, patients, nosymptom, nosymptom_to_patient, patient_findallin_control, nosymptom_findallin_control,\
            patient_close, nosymptom_close, nosymptom_control, in_hospital, heal, serious, dead, leave_nosymptom_control)
    print(result)
    return result

if __name__ == '__main__':
    dir = 'data/number/'
    data_file = 'data/use/macro_data.csv'
    begin = 20220325
    filelist = listdir(dir)
    w = codecs.open(data_file, mode = 'w', encoding='utf_8')
    w.write(",".join(('时间', '确诊', '无症状', '无症状转确诊', '管控内确诊', '管控内无症状',\
            '确诊密接', '无症状密接', '本土医学观察中无症状', '本土在院治疗中', '治愈出院', '重症', '死亡', '解除医学观察\n')))
    for file in filelist:
        if file.find('.') > 0 or int(file) < begin:
            continue
        f = codecs.open(dir + file, mode = 'r', encoding='utf_8')
        result = get_numbers(f, file)
        w.write(",".join(result) + '\n')
    w.close()
