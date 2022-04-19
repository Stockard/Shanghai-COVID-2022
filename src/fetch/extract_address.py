#encoding=utf-8
#清理上海发布每天发布的地址信息 since 3/19/2022
import codecs
import re
from os import listdir

from config import district_file, address_file, address_dir, number_dir

def parse(file, date_value):
    districts = ['宝山区\n','崇明区\n','奉贤区\n','虹口区\n','黄浦区\n','嘉定区\n','金山区\n','静安区\n','闵行区\n','浦东新区\n','普陀区\n','青浦区\n','松江区\n','徐汇区\n','杨浦区\n','长宁区\n']
    start = '各区信息如下：\n'
    line = '' #默认值
    print(f'Begin to parse {date_value}')
    while (line and line != start):
        line = f.readline()
    while True:
        line = f.readline()
        if line in districts:
            district = line[:-1]
#            print(f'parse districts {district, date_value}')
            parse_district(f, district, date_value)
        if not line:
            break

def parse_district(file, district, date_value):
    end = '消毒'
    line = file.readline()
    while (line == '\n' or line == '（滑动查看更多↓）\n'):
        line = file.readline()
#    if not check_exist(date_value, list_district_exist):
    cases = re.findall('(\d+)例本土确诊病例，新增(\d+)例本土无症状感染', line[:-1])
    if len(cases) > 0:
        districts_value.write(date_value + "," + cases[0][0] + ',' + cases[0][1] + "," + district + '\n')
    while (line and line.find(end) < 0):
        line = file.readline()
        if line != '\n' and (line.find(end) < 0):
#            if not check_exist(date_value, list_address_exist):
            address_write(address_value, date_value, line[:-1], district)

def address_write(f, date_value, text, district):
    quotes = ['，', '、', '。']
    modified_text = text
    for i in quotes:
        modified_text = modified_text.replace(i, ',')
    modified_text = modified_text.split(',')
    for t in modified_text:
        if t != '':
            f.write(date_value + "," + t.strip() + "," + district + '\n')

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
    districts_value = codecs.open(district_file, mode = 'w', encoding = 'utf-8')
    address_value = codecs.open(address_file, mode = 'w', encoding = 'utf-8')
    address_value.write('date,address,district\n')
    districts_value.write('date,patient,nosymptom,district\n')
    filelist = listdir(address_dir)
    for file in filelist:
        if '.' in file:
            continue
        print(f'now opeing {file}')
        date_value = file
        f = codecs.open(address_dir + file, mode='r', encoding='utf_8')
        parse(f, date_value)
        f.close()
    districts_value.close()
    address_value.close()
