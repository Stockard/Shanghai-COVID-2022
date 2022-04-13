#encoding=utf-8
#清理上海发布每天发布的地址信息 since 3/19/2022
import codecs
from os import listdir

def phrase(file, date_value):
    districts = ['宝山区\n','崇明区\n','奉贤区\n','虹口区\n','黄浦区\n','嘉定区\n','金山区\n','静安区\n','闵行区\n','浦东新区\n','普陀区\n','青浦区\n','松江区\n','徐汇区\n','杨浦区\n','长宁区\n']
    start = '各区信息如下：\n'
    line = '' #默认值
    print(f'Begin to phrase {date_value}')
    while (line and line != start):
        line = f.readline()
    while True:
        line = f.readline()
        if line in districts:
            district = line[:-1]
            print(f'phrase districts {district, date_value}')
            phrase_district(f, district, date_value)
        if not line:
            break

def phrase_district(file, district, date_value):
    end = '消毒'
    line = file.readline()
    print(line)
    while (line == '\n' or line == '（滑动查看更多↓）\n'):
        line = file.readline()
    districts_daily.write(date_value + "," + line[:-1].strip() + "," + district + '\n')
    while (line and line.find(end) < 0):
        line = file.readline()
        if line != '\n' and (line.find(end) < 0):
            address_write(address_daily, date_value, line[:-1], district)

def address_write(f, date_value, text, district):
    quotes = ['，', '、', '。']
    modified_text = text
    for i in quotes:
        modified_text = modified_text.replace(i, ',')
    modified_text = modified_text.split(',')
    for t in modified_text:
        if t != '':
            f.write(date_value + "," + t.strip() + "," + district + '\n')


if __name__ == '__main__':
    districts_daily = codecs.open('data/temp/districts_daily.txt', mode = 'w', encoding = 'utf-8')
    address_daily = codecs.open('data/temp/address_daily.txt', mode = 'w', encoding = 'utf-8')
    filelist = listdir('data/address')
    for file in filelist:
        if '.' in file:
            continue
        print(f'now opeing {file}')
        date_value = file
        f = codecs.open('data/address/' + file, mode='r', encoding='utf_8')
        phrase(f, date_value)
        f.close()
    districts_daily.close()
    address_daily.close()
