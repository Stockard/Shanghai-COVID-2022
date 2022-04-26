#encoding=utf-8
#清理上海发布每天发布的地址信息 since 3/19/2022
import codecs
import re
from os import listdir

from config import district_daily_file, address_file, address_dir, number_dir

def parse(f, date_value):
    districts = ['宝山区\n','崇明区\n','奉贤区\n','虹口区\n','黄浦区\n','嘉定区\n','金山区\n','静安区\n','闵行区\n','浦东新区\n','普陀区\n','青浦区\n','松江区\n','徐汇区\n','杨浦区\n','长宁区\n']
    start = '各区信息如下：\n'
    line = '' #默认值
    address_list = []
    district_list = []
    print(f'Begin to parse {date_value}')
    while (line and line != start):
        line = f.readline()
    while True:
        line = f.readline()
        if line in districts:
            district = line[:-1]
            alist, dlist = parse_district(f, district, date_value)
            address_list += alist
            district_list += dlist
        if not line:
            break
    address_list = address_clean(address_list)
    return address_list, district_list

def parse_district(file, district, date_value):
    districts = ['宝山区\n', '崇明区\n', '奉贤区\n', '虹口区\n', '黄浦区\n', '嘉定区\n', '金山区\n', '静安区\n', '闵行区\n', '浦东新区\n', '普陀区\n',
                 '青浦区\n', '松江区\n', '徐汇区\n', '杨浦区\n', '长宁区\n']
    end = '消毒'
    address_list = []
    district_list = []
    line = file.readline()
    while (line == '\n' or line == '（滑动查看更多↓）\n'):
        line = file.readline()
#    if not check_exist(date_value, list_district_exist):
    cases = re.findall('(\d+)例本土确诊病例.*(\d+)例本土无症状感染', line[:-1])
    if len(cases) > 0:
        district_list.append((date_value, cases[0][0], cases[0][1], district))
    while (line and line.find(end) < 0 and line not in districts):
        line = file.readline()
        if line != '\n' and (line.find(end) < 0):
            address_list.append((date_value, line[:-1], district))
#            if not check_exist(date_value, list_address_exist):
    return address_list, district_list

def address_clean(address_list):
    address_list_clean = []
    for date_value, text, district in address_list:
        #处理有些排一起的数据
        quotes = ['，', '、', '。']
        modified_text = text
        for i in quotes:
            modified_text = modified_text.replace(i, ',')
        modified_text = modified_text.split(',')
        for t in modified_text:
            if t != '':
                address_list_clean.append((date_value, t.strip(), district))
    return address_list_clean

def check_exist(date_value, date_list):
    return date_value in date_list

def build_exist_date(file):
    #检查哪些日期已经在了
    date_list = []
    try:
        f = codecs.open(file, mode = 'r', encoding = 'utf-8')
        while True:
            line = f.readline()
            date = line.split(',')[0]
            if date not in date_list:
                date_list.append(date)
            if not line:
                break
        f.close()
    except:
        pass
    return date_list

if __name__ == '__main__':
    districts_writer = codecs.open(district_daily_file, mode = 'w', encoding = 'utf-8')
    address_writer = codecs.open(address_file, mode = 'w', encoding = 'utf-8')
    address_writer.write('date,address,district\n')
    districts_writer.write('date,patient,nosymptom,district\n')
    filelist = listdir(address_dir)
    for file in filelist:
        if '.' in file:
            continue
        print(f'now opeing {file}')
        date_value = file
        f = codecs.open(address_dir + file, mode='r', encoding='utf_8')
        address_list, district_list = parse(f, date_value)
        for i in address_list:
            address_writer.write(",".join(i) + '\n')
        for i in district_list:
            districts_writer.write(",".join(i) + '\n')
        f.close()
    districts_writer.close()
    address_writer.close()
