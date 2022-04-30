import pandas as pd

from validate import check_data_integrity
from config import pre_macro_file, temp_macro_file, macro_file
from config import district_details_t2, district_details_t3, district_file
from config import geo_file, geo_add_file, geo_simple_file
from config import address_file, pre_patient_file, pre_patient_sort_file, address_cleaned_file, merge_geo_address_file

#日，区，无症状/确诊，经纬度度数据

def merge_marcro_data():
    #合并市一级数据
    pre_macro = pd.read_csv(pre_macro_file)
    current_macro = pd.read_csv(temp_macro_file)
    #合并
    current_macro = current_macro[current_macro['时间'].apply(lambda x: x not in pre_macro['时间'])]
    macro = pd.concat([pre_macro, current_macro], ignore_index = True)
    values = {"确诊病例": 0, "无症状感染者": 0, "无症状转确诊": 0, "野生确诊":0, "管控内确诊": 0, "管控内无症状": 0, "例行筛查确诊": 0, "例行筛查无症状": 0}
    macro.fillna(value = values, inplace = True)
    macro = macro.astype(pd.Int64Dtype())
    macro.to_csv(macro_file, index = False)

def merge_district_data():
    #区一级数据
    #处理kf的数据为区和闭环管控数据
    #处理district_type_2为区和闭环管控数据
    #处理district_type_3为区和闭环管控数据
    pre_patient = pd.read_csv(pre_patient_file)
    pre_patient.sort_values(by = ['date', 'is_patient','district']).to_csv(pre_patient_sort_file)
    district_t2 = pd.read_csv(district_details_t2)
    district_t3 = pd.read_csv(district_details_t3)

    dis_1 = pre_patient.groupby(['date', 'is_patient', 'district', 'source'], as_index = False).size().rename(columns = {'size':'count'})
    dis_2 = district_t2.groupby(['date', 'is_patient', 'district', 'source'], as_index = False).size().rename(columns = {'size':'count'})
    dis_3 = district_t3[['date', 'is_patient', 'district', 'source','count']]
#    print(dis_1, dis_2, dis_3)

    district = pd.concat([dis_1, dis_2, dis_3], ignore_index = True)
    district.to_csv(district_file, index = False)

def merge_geo_data():
    # 修改Geo程序为爬取增量
    #汇总增量
    geo = pd.read_csv(geo_file)
    geo_simple = pd.read_csv(geo_simple_file)
    geo_add = pd.read_csv(geo_add_file)

    geo_add_simple = geo_add[['district', 'address', 'complete_address', 'gcj02_lng','gcj02_lat','wgs84_lng','wgs84_lat','township']]

    geo = pd.concat([geo, geo_add], ignore_index = True)
    geo.drop_duplicates('address', inplace = True)
    geo.to_csv(geo_file, index = False)
    geo_simple = pd.concat([geo_simple, geo_add_simple], ignore_index = True)
    geo_simple.drop_duplicates('address', inplace = True)
    geo_simple.to_csv(geo_simple_file, index = False)
    #检查地址数据是否缺失（时间，区），区数据加总是否等于市级别 —— 输出到log
    #汇总病例数和地址数据，用于作图
    # + [location], geo features

def merge_address():
    address = pd.read_csv(address_file) #
    pre_address = pd.read_csv(pre_patient_file) #3月18日之前
    address = pd.concat([address, pre_address[['date', 'address', 'district']]])
#    address.drop_duplicates(['date', 'address', 'district'], inplace=True)
    address.to_csv(address_cleaned_file, index = False)

def merge_address_geo():
    address = pd.read_csv(address_cleaned_file)
    geo = pd.read_csv(geo_simple_file)
    complete_address = pd.merge(address, geo)
    complete_address['date_value'] = complete_address.date.apply(
        lambda x: pd.Timestamp(str(x)[:4] + '-' + str(x)[4:6] + '-' + str(x)[6:]))
    complete_address.groupby(['township', 'district']).agg('median')
    complete_address.to_csv(merge_geo_address_file)

if __name__ == '__main__':
    merge_marcro_data()
    merge_district_data()
    merge_geo_data()
    merge_address()
    merge_address_geo()
#    check()
    check_data_integrity()
