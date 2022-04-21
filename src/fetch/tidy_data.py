#encoding=utf-8
"""
3月17日前的用已经清理完的数据，不另外写程序清理
[ ] 对25号前的每日数据还有bug（不修了）
[x] 4.14开始治愈出院变成累计数
[x] 4.18日汇报增加实际阳性感染
"""
import codecs
import re
from os import listdir
import pandas
from config import address_dir, number_dir
from config import temp_macro_file as macro_file
from config import district_file, address_file, district_details_t2, district_details_t3
from convert_date import get_report_type
from convert_date import convert_date_string_to_excel_ordinal

ALLOW_SKIP= 1

def filter_list():
    #确定到底使用哪些文件
    begin = 20220318 #实际可以从3月25日开始
    file_in_dir = listdir(number_dir)
    file_in_dir.sort()
    file_list = []
    for file in file_in_dir:
        if file.find('.') > 0 or int(file) < begin:
            continue
        if int(file) >= begin:
            file_list.append(file)
    return file_list

def find_patterns(text, match_pattern, allow_skip = 0):
    values = re.findall(match_pattern, text)
    if len(values) > 0:
        values = values[0]
    else:
        values = '0'
    return values

class Cleaning_district_block():
    """
    清理每区病人汇报
    """
    def __init__(self, date, p_or_o, text = ""):
        self.text_list = []
        self.details_list = []
        self.details_title = []
        self.current_line = ''
        self.anchor = 0
        self.date = date
        self.district_details_type = 1 #根据日期决定到时间
        self.p_or_o = p_or_o #病例或无症状感染者
        self.p_or_o_string = self.map_p_or_o(p_or_o) #病例或无症状感染者
        self.set_district_details_type()
        self.add(text)

    def add(self, text):
        #是一个字符串流顺序输入的过程 输入理论上从第一个患者开始到密接结束
        find_source, source = self.get_source(text)
        self.current_line = self.current_line + text.replace('\n', '') #不替换会出bug，在区前面有两个回车，无法识别汇总
        if find_source:
            self.text_list.append(self.current_line)
            self.current_line = ''

    def export(self):
        #输出清理完的district信息
        self.details_list = []
        for line in self.text_list:
            details = self.export_line(line)
            self.details_list += details
#        print(self.export_text()) #debug
        return self.details_list

    def get_district_details_type(self):
        return self.district_details_type

    def export_text(self):
        return self.text_list

    def map_p_or_o(self, p_or_o):
        #string 汇总和分区统一
        s = p_or_o
        if p_or_o == '病例':
            s = '确诊病例'
        return s

    def set_district_details_type(self):
        self.district_details_type = self.get_district_details_type()
        if self.district_details_type == 1:
            self.details_title = [] #不做处理
        elif self.district_details_type == 2:
            self.details_title = ['date', 'is_patient', 'source', 'patient_num', 'sex', 'age', 'district']
        elif self.district_details_type == 3:
            self.details_title = ['date', 'is_patient', 'source', 'patient_num', 'district']

    def get_source(self, text):
        source = ''
        find_source = 0 #find or not
        source_list = ['闭环隔离管控', '风险人群筛查', '此前报告的本土无症状感染']
        for i in source_list:
            if text.find(i) > 0:
                source = i
                find_source = 1
        return find_source, source

    def export_line(self, text):
        details = []
        find_source, source = self.get_source(text)
        if self.district_details_type == 1:
            pass #不做处理
        elif self.district_details_type == 2: #317 - 325公告
            pattern = self.p_or_o + '(\d+)，([男｜女])，(\d+)岁，居住于([\u4e00-\u9fa5]{2})[新区|区]' #0324里出现了个婴儿 无症状感染者58，男，4月龄，居住于嘉定区
            baby_pattern = self.p_or_o + '(\d+)，([男｜女])，\d+月龄，居住于([\u4e00-\u9fa5]{2})[新区|区]' #0324里出现了个婴儿 无症状感染者58，男，4月龄，居住于嘉定区
            patient_string = re.findall(pattern, text)
            baby_string = re.findall(baby_pattern, text)
            if len(patient_string) > 0:
                for s in patient_string:
                    details.append([self.p_or_o_string, source, *s])
            if len(baby_string) > 0:
                for number, sex, district in baby_string: # age = 0
                    details.append([self.p_or_o_string, source, number, sex, '0', district])
        elif self.district_details_type == 3: #0325之后的公告
            first_patient_pattern = self.p_or_o + '(\d+)' #返回第一个患者编号 ugly fix of pudong district
            pattern = self.p_or_o + '(\d+)，居住于[，]{0,1}([\u4e00-\u9fa5]{2})[新区|区]' #会返回患者编号，需要处理才能输出每个区到个数；4月1日数据里多了一个、
            first_patient = re.findall(first_patient_pattern, text)
            if len(first_patient) > 0:
                first_patient = first_patient[0]
            else:
                first_patient = 0
            patient_string = re.findall(pattern, text)
            if len(patient_string) > 0:
                for i in range(len(patient_string)):
                    last_num, district = patient_string[i]
                    if (i == 0):
                        number = int(last_num) - int(first_patient) + 1
                        if number < 0:
                            print(text)
                            print(f'{last_num} {first_patient} {district}')
                    else:
                        number = int(last_num) - int(patient_string[i-1][0])
                    details.append([self.p_or_o_string, source, district, str(number)])
#        print(details, self.report_type)
        return details

    def get_district_details_type(self):
        """3.1 - 3.17 type 1 每个病例有详情
            3.17 - 3.25 type 2 每个病例有年纪和区，3月18号开始单独发布地址
            3.26 - 今 type 3 只有区级别的汇总
        """
        date = self.date
        if int(date) <= 20220317:
            type = 1 #每个病例有详情
        elif int(date) <= 20220325:
            type = 2 #每个病例有年纪和区，3月18号开始单独发布地址
        else:
            type = 3 #只有区级别的汇总
        return type

class Report_parse():
    """
        numbers: patients, nosymptom, nosymptom_to_patient, patient_findallin_control, nosymptom_findallin_control,
        outside_patient, outside_nosymptom,
        patient_close, nosymptom_close,
        nosymptom_control, leave_nosymptom_control, in_hospital, heal, serious, dead
    """
    def __init__(self, date, text_list):
        self.text_list = text_list
        self.date = date
        self.current_line = 0
        self.numbers = ()
        self.flags = dict()
        self.text_list_length = self.text_list.__len__()
        self.district_details_type = 1 #默认
        self.structure()
        self.parse()
        self.check_flags()

    def get_macro_numbers(self):
        return self.numbers

    def get_district_details(self):
        return self.district_details

    def get_district_details_type(self):
        return self.district_details_type

    def structure(self):
        #intialization
        self.first_line = ''
        self.patient_details = '' #cleaning_district_block
        self.patient_details_close_line = ''
        self.nosymptom_details = '' #cleaning_district_block
        self.nosymptom_details_close_line = ''
        self.in_hospital = '' #治疗行
        self.in_control = '' #在院留观
        self.leave_control = '' #解除隔离

        if self.move_block_pointer('市卫健委'): #获得首行
            self.first_line = self.text_list[self.current_line]
        if self.move_block_pointer('新增本土新冠肺炎确诊病例'): #开始处理确诊部分
            if self.move_block_pointer('^病例(\d+)'):
                find_close, close_line = self.find_block_num('病例\d+', reverse=True)
#                print(close_line, self.text_list[close_line])
                self.patient_details = Cleaning_district_block(self.date, '病例') #初始化block
                self.district_details_type = self.patient_details.get_district_details_type() #先放在这里，逻辑有点奇怪
                for i in range(self.current_line, close_line):
                    self.patient_details.add(self.text_list[i])
                if find_close:
                    self.patient_details_close_line = self.text_list[close_line]  #已追踪到以上病例在本市的密切接触者53人
        if self.move_block_pointer('新增本土无症状'):
            #开始处理密接部分
            if self.move_block_pointer('^无症状感染者(\d+)'):
                find_close, close_line = self.find_block_num('无症状感染者(\d+)', reverse=True)
                self.nosymptom_details = Cleaning_district_block(self.date, '无症状感染者') #初始化block
                for i in range(self.current_line, close_line):
                    self.nosymptom_details.add(self.text_list[i])
                if find_close:
                    self.nosymptom_details_close_line = self.text_list[close_line]  #已追踪到以上病例在本市的密切接触者53人
        self.in_hospital = self.get_block('在院治疗') #累计本土确诊707例，治愈出院476例，在院治疗224例，死亡7例。
        self.in_control = self.get_block('尚在医学观察中的') #尚在医学观察中的无症状感染者8711例，其中本土无症状感染者8674
        self.leave_control = self.get_block('解除医学观察') #其中本土无症状感染者102例，境外输入性无症状感染者8例。

    def parse(self):
        numbers_first = self.parse_first_line()
        self.parse_district()
        numbers_second = self.parse_separate_lines()
        outside_patient = str(int(numbers_first[0]) - int(numbers_first[2]) - int(numbers_first[4]))
        outside_nosymptom = str(int(numbers_first[1]) - int(numbers_first[5]))
#        outside_patient = str(int(patients) - int(nosymptom_to_patient) - int(patient_findallin_control))
#        outside_nosymptom = str(int(nosymptom) - int(nosymptom_findallin_control))
        self.numbers = (*numbers_first, outside_patient, outside_nosymptom, *numbers_second)

    def parse_first_line(self):
        patient_outside = "0" # 野生确诊默认为0
        patients, nosymptom, nosymptom_to_patient, patient_findallin_control, nosymptom_findallin_control = [0, 0, 0, 0, 0]
        patients = find_patterns(self.first_line, '新增本土新冠肺炎确诊病例(\d+)[例|]')  #其中本土无症状感染者102例，境外输入性无症状感染者8例。
        nosymptom = find_patterns(self.first_line, '无症状感染者(\d+)例')  #其中本土无症状感染者102例，境外输入性无症状感染者8例。
        nosymptom_to_patient = find_patterns(self.first_line, '(\d+)例确诊病例为此前无症状感染者转归', ALLOW_SKIP)  #其中本土无症状感染者102例，境外输入性无症状感染者8例。
        if nosymptom_to_patient == "0":
            nosymptom_to_patient = find_patterns(self.first_line, '无症状感染者转为确诊病例(\d+)', ALLOW_SKIP)  #其中本土无症状感染者102例，境外输入性无症状感染者8例。
        (patient_findallin_control, nosymptom_findallin_control) = find_patterns(self.first_line, '(\d+)例确诊病例和(\d+)例无症状感染者在隔离管控中')
        return (patients, nosymptom, nosymptom_to_patient, patient_outside, patient_findallin_control, nosymptom_findallin_control)

    def parse_district(self):
        self.district_details = []
        self.district_details += self.patient_details.export()
        self.district_details += self.nosymptom_details.export()

    def parse_separate_lines(self):
        patient_close = find_patterns(self.patient_details_close_line, '密切接触者(\d+)', ALLOW_SKIP)
        nosymptom_close = find_patterns(self.nosymptom_details_close_line, '密切接触者(\d+)', ALLOW_SKIP)
        leave_nosymptom_control = find_patterns(self.leave_control, '本土无症状感染者(\d+)', ALLOW_SKIP)
        nosymptom_control = find_patterns(self.in_control, '本土无症状感染者(\d+)', ALLOW_SKIP)
        if self.in_hospital != "":
            heal = find_patterns(self.in_hospital, '治愈出院(\d+)')
            in_hospital = find_patterns(self.in_hospital, '在院治疗(\d+)')
            serious = find_patterns(self.in_hospital, '重症(\d+)', ALLOW_SKIP)
            dead = find_patterns(self.in_hospital, '死亡(\d+)', ALLOW_SKIP)
        nosymptom_to_patient = 0
        if int(self.date) < 20220414: #治愈出院调整 2022溺爱4月14日后变成累计数
            heal = str(int(heal) - 385)
        return (patient_close, nosymptom_close, \
                nosymptom_control, leave_nosymptom_control, in_hospital, heal, serious, dead)

    def check_flags(self):
        self.flags['first_line'] = self.first_line != ""
        self.flags['patient_details'] = isinstance(self.patient_details, Cleaning_district_block)
        self.flags['nosymptom_details'] = isinstance(self.nosymptom_details, Cleaning_district_block)
        self.flags['in_hospital'] = self.in_hospital != ''
        self.flags['in_control'] = self.in_control != ""
        self.flags['leave_control'] = self.leave_control != ""
        for key, values in self.flags.items():
            if not values:
                print(f'  {key} not found, {self.date}')

    def get_block(self, location_pattern):
        start_line = self.current_line
        find_text, line_num = self.find_block_num(location_pattern)
        if find_text:
            return self.text_list[line_num]
        else:
            return '' #返回空

    def move_block_pointer(self, location_pattern):
        start_pointer = self.current_line
        find_text, line_pointer = self.find_block_num(location_pattern)
        self.current_line = line_pointer
        return find_text

    def find_block_num(self, location_pattern, reverse = False):
        # reverse = find next line without pattern
        start_line = self.current_line
        find_text = 0
        line_num = start_line
        if reverse == True:
            for i in range(start_line, self.text_list_length):
                if ((self.text_list[i] != '\n') and len(re.findall(location_pattern, self.text_list[i])) == 0):
                    find_text = 1
                    line_num = i
                    break
        else:
            for i in range(start_line, self.text_list_length):
                if len(re.findall(location_pattern, self.text_list[i])) > 0:
                    find_text = 1
                    line_num = i
                    break
        return find_text, line_num


def intialization_writers():
    district_f_2 = codecs.open(district_details_t2, mode = 'w', encoding='utf_8')
    district_f_3 = codecs.open(district_details_t3, mode = 'w', encoding='utf_8')
    district_f_2.write(",".join(['date', 'is_patient', 'source', 'number', 'sex', 'age', 'district']) + '\n')
    district_f_3.write(",".join(['date', 'is_patient', 'source', 'district', 'count']) + '\n')
    macro_writer = codecs.open(macro_file, mode = 'w', encoding='utf_8')
    macro_writer.write(",".join(('时间', '确诊病例', '无症状感染者', '无症状转确诊', '野生确诊', '管控内确诊', '管控内无症状',\
            '例行筛查确诊', '例行筛查无症状', \
            '确诊密接', '无症状密接', \
            '本土医学观察中无症状', '解除医学观察', '本土在院治疗中', '治愈出院', '重症', '死亡\n')))
    return district_f_2, district_f_3, macro_writer

def district_writer(district_list, date, report_type):
    #把分区数据写入文件
    if report_type == 2:
        writer = district_f_2
    elif report_type == 3:
        writer = district_f_3
    for i in district_list:
        writer.write(date + "," + ",".join(i) + '\n')

def get_numbers(f, date_value):
    """
    return: 市('时间', '确诊病例', '无症状感染者', '无症状转确诊', '野生确诊', '管控内确诊', '管控内无症状',\
        '确诊密接', '无症状密接', '本土医学观察中无症状', '本土在院治疗中', '治愈出院', '重症', '死亡', '解除医学观察\n')    """
    print(f'reading {file}')
    text = f.readlines()
    report = Report_parse(date_value, text)
    district_list = report.get_district_details()
    result = (date_value, *(report.get_macro_numbers()))
    report_type = report.get_district_details_type()
    district_writer(district_list, date_value, report_type)
    return result, district_list

if __name__ == '__main__':
    file_list = filter_list()
    district_f_2, district_f_3, macro_writer = intialization_writers()
    for file in file_list:
        f = codecs.open(number_dir + file, mode = 'r', encoding='utf_8')
        result, district_list = get_numbers(f, file)
        macro_writer.write(",".join(result) + '\n')
        f.close()
    macro_writer.close()
    district_f_2.close()
    district_f_3.close()
