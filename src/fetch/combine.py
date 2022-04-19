import pandas as pd

from config import pre_macro_file, temp_macro_file, macro_file
from config import pre_patient_file, district_details_t2, district_details_t3, district_file
from config import geo_file, geo_add_file
from config import address_file, pre_patient_file, address_cleaned_file

#日，区，无症状/确诊，维度数据

def merge_marcro_data():
    #合并市一级数据
    pre_macro = pd.read_csv(pre_macro_file)
    current_macro = pd.read_csv(temp_macro_file)
    #合并
    current_macro = current_macro[current_macro['时间'].apply(lambda x: x not in pre_macro['时间'])]
    macro = pd.concat([pre_macro, current_macro], ignore_index = True)
    macro.to_csv(macro_file, index = False)

def merge_district_data():
    #区一级数据
    #处理kf的数据为区和闭环管控数据
    #处理district_type_2为区和闭环管控数据
    #处理district_type_3为区和闭环管控数据
    pre_patient = pd.read_csv(pre_patient_file)
    district_t2 = pd.read_csv(district_details_t2)
    district_t3 = pd.read_csv(district_details_t3)

    dis_1 = pre_patient.groupby(['date', 'is_patient', 'district', 'source'], as_index = False).size().rename(columns = {'size':'count'})
    dis_2 = district_t2.groupby(['date', 'is_patient', 'district', 'source'], as_index = False).size().rename(columns = {'size':'count'})
    dis_3 = district_t3[['date', 'is_patient', 'district', 'source','count']]
    print(dis_1, dis_2, dis_3)

    district = pd.concat([dis_1, dis_2, dis_3], ignore_index = True)
    district.to_csv(district_file, index = False)

def merge_geo_data():
    # 修改Geo程序为爬取增量
    #汇总增量
    geo = pd.read_csv(geo_file)
    geo_add = pd.read_csv(geo_add_file)

    geo = pd.concat([geo, geo_add], ignore_index = True)
    geo.drop_duplicates('address', inplace = True)
    geo.to_csv(geo_file, index = False)
    #检查地址数据是否缺失（时间，区），区数据加总是否等于市级别 —— 输出到log
    #汇总病例数和地址数据，用于作图
    # + [location], geo features

def merge_address():
    address = pd.read_csv(address_file) #
    pre_address = pd.read_csv(pre_patient_file) #3月18日之前
    address = pd.concat([address, pre_address[['date', 'address', 'district']]])
    address.to_csv(address_cleaned_file, index = False)

#先在本地分析街道级别到数据（tableau？）

if __name__ == '__main__':
    merge_marcro_data()
    merge_district_data()
    merge_geo_data()
    merge_address()
