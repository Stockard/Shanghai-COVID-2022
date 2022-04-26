
from config import *
import codecs
from os import listdir

from crawl_official import crawler_top
from extract_address import parse
#from tidy_address import list_compare, complete_check
from tidy_data import get_numbers, filter_list
from lnglat_transform import Lnglat_transform, data_split_to_float
from fetch_geo import address_to_geo
from combine import *
from validate import check_data_integrity

data_colnames ={
    'address':['地址原始清理', ('date','address','district')],
    'district':['区数据原始清理', ('date','patient','nosymptom','district')],
    'district_details_t2':['第二类报告', ('date', 'is_patient', 'source', 'number', 'sex', 'age', 'district')],
    'district_details_t3': ['第三类报告', ('date', 'is_patient', 'source', 'district', 'count')],
    'macro':['宏观数据',('时间', '确诊病例', '无症状感染者', '无症状转确诊', '野生确诊', '管控内确诊', '管控内无症状',
            '例行筛查确诊', '例行筛查无症状', \
            '确诊密接', '无症状密接', \
            '本土医学观察中无症状', '解除医学观察', '本土在院治疗中', '治愈出院', '重症', '死亡', '重型', '危重型')],
    'district_in_hospital':['区确诊人数',('date', 'district', 'in_hospital')]
}

def writer(file, strings, is_title = 0, batch = 0):
    if is_title:
        m = 'w'
    else:
        m = 'a+'
    if batch == 1:
        with codecs.open(file, mode = m, encoding = 'utf-8') as handler:
            for st in strings:
                if not isinstance(st, str):
                    st = ",".join([str(i) for i in st]) + '\n'
                handler.write(st)
    else:
        if not isinstance(strings, str):
            strings = ",".join([str(i) for i in strings]) + '\n'
        with codecs.open(file, mode = m, encoding = 'utf-8') as handler:
            handler.write(strings)

def openfile(file, mode = 'r'):
    return codecs.open(file, mode = mode, encoding='utf_8')

if __name__ == '__main__':
    #crawl_data
    baseurl = ['https://wsjkw.sh.gov.cn/yqtb/index.html']
    crawler_top(baseurl)
    #exact address
    writer(district_daily_file, data_colnames['district'][1], is_title = 1)
    writer(address_file, data_colnames['address'][1], is_title = 1)
    filelist = listdir(address_dir)
    for file in filelist:
        if '.' in file:
            continue
        print(f'now opeing {file}')
        date_value = file
        handler = openfile(address_dir + file)
        address_list, district_list = parse(handler, date_value)
        handler.close()
        writer(address_file, address_list, batch=1)
        writer(district_daily_file, district_list, batch=1)
    #tidy address
    print('tidy address')
    address = pd.read_csv(address_file, encoding = 'utf-8')
    address_extend = pd.read_csv(pre_address_file, encoding = 'utf-8')
    address_series = pd.concat([address, address_extend]).loc[:, ['address', 'district']]
    address_full_list = address_series.address.unique()
    print(address_full_list)

    geo = pd.read_csv(geo_file, encoding = 'utf-8')
    geo_full_list = pd.unique(geo.address)

    print(f'--address list unique {len(address_full_list)} full {address_series.shape[0]}--')
    print(f'--geo list unique {len(geo_full_list)} full {geo.shape[0]}--')

    print(address_series)
    address_series.drop_duplicates('address', inplace = True)
    address_series['not_in_geo_list'] = address_series.apply(lambda x: x['address'] not in geo_full_list, axis = 1)
    address_add = address_series.loc[address_series['not_in_geo_list'], ['address', 'district']]
    address_add.to_csv(address_add_file, index = False)

    #tidy data
    file_list = filter_list()
    district_writer = {2: district_details_t2, 3:district_details_t3}
    writer(temp_macro_file, data_colnames['macro'][1], is_title = 1)
    writer(district_details_t2, data_colnames['district_details_t2'][1], is_title=1)
    writer(district_details_t3, data_colnames['district_details_t3'][1], is_title=1)
    writer(district_in_hospital_file, data_colnames['district_in_hospital'][1], is_title = 1)
    for file in file_list:
        handler = openfile(number_dir + file)
        date, result, district_list, report_type, district_in_hospital = get_numbers(handler, file)
        handler.close()
        writer(temp_macro_file, result)
        writer(district_in_hospital_file, district_in_hospital, batch=1)
        for i in district_list:
            writer(district_writer[report_type], (date, *i))

    #fetch geo
    data = pd.read_csv(address_add_file, engine='python')  # 导入对应地址的csv文件
    address_to_geo(data, 50)  # 用于控制单次写入文件的内容不超过500条
    # 将高德经纬度数据转换成wgs标准
    URL = 'https://restapi.amap.com/v3/geocode/geo?'
    URL_REGEO = 'https://restapi.amap.com/v3/geocode/regeo'
    lis = []
    g = Lnglat_transform()
    lnglat_df = pd.read_csv(geo_add_temp_file, encoding='utf-8')
    lnglat_df = data_split_to_float(lnglat_df)
    gps_df = g.lnglat_batch_map(lnglat_df)
    #    gps_df = data_concat(gps_df)
    gps_df = gps_df[['district', 'address', 'complete_address', 'gcj02_lng', 'gcj02_lat', 'wgs84_lng', 'wgs84_lat', 'street_level']]
    gps_df.to_csv(geo_add_file, encoding='utf-8', index=False)
    #combine
    merge_marcro_data()
    merge_district_data()
    merge_geo_data()
    merge_address()
    check_data_integrity()
    merge_address_geo()

