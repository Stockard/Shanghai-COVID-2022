#http://www.cpearson.com/excel/datetime.htm
#https://stackoverflow.com/questions/9574793/how-to-convert-a-python-datetime-datetime-to-excel-serial-date-number
# -- 三段不同的时间 --

from datetime import date


def convert_date_string_to_excel_ordinal(date_string) :
    day = int(date_string[-2:])
    month = int(date_string[4:6])
    year = int(date_string[:4])
    offset = 693594
    current = date(year,month,day)
    n = current.toordinal()
    return (n - offset)

def convert_date_to_excel_ordinal(day, month, year) :
    offset = 693594
    current = date(year,month,day)
    n = current.toordinal()
    return (n - offset)

def get_report_type(date):
    """3.1 - 3.17 type 1 每个病例有详情
        3.17 - 3.25 type 2 每个病例有年纪和区，3月18号开始单独发布地址
        3.26 - 今 type 3 只有区级别的汇总
    """
    if int(date) <= 20220317:
        date_type = 1 #每个病例有详情
    elif int(date) <= 20220325:
        date_type = 2 #每个病例有年纪和区，3月18号开始单独发布地址
    else:
        date_type = 3 #只有区级别的汇总
    return date_type
