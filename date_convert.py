#http://www.cpearson.com/excel/datetime.htm
#https://stackoverflow.com/questions/9574793/how-to-convert-a-python-datetime-datetime-to-excel-serial-date-number
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
