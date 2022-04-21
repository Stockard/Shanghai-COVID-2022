import pandas as pd

from config import pre_macro_file, temp_macro_file, macro_file
from config import pre_patient_file, district_details_t2, district_details_t3, district_file
from config import geo_file, geo_add_file
from config import address_file, pre_patient_file, pre_patient_sort_file, address_cleaned_file

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

def check_data_integrity():
    #主要检查区数据
    district = pd.read_csv(district_file)
    macro = pd.read_csv(macro_file)
    sum_district = district[['date', 'is_patient', 'count']].groupby(['date', 'is_patient'], as_index = False).sum()
#    print(sum_district)
    for is_patient in ['确诊病例', '无症状感染者']: #检验每日确诊和无症状数据
        for date in sum_district['date'].unique():
            value_in_macro = int(macro[macro['时间'] == date][is_patient])
            value_in_district_agg = int(sum_district[(sum_district['date'] == date) & (sum_district['is_patient'] == is_patient)]['count'])
            print(value_in_macro, value_in_district_agg, date, is_patient)
            assert(value_in_macro == value_in_district_agg)
    #检验区级别几个环节数据 暂时留空
#先在本地分析街道级别到数据（tableau？）

def check():
    #检查是否漏掉了某些病例
    date = 20220324
    num = 1579
    district_t2 = pd.read_csv(district_details_t2)
    dis_2 = district_t2.groupby(['date', 'is_patient', 'district', 'source'], as_index=False).size().rename(
        columns={'size': 'count'})
    for i in range(num):
        if district_t2[(district_t2['date'] == date) & (district_t2['number'] == i)].shape[0] != 1:
            print(i)
    print(dis_2[dis_2['date'] == date])
    print(sum(dis_2[(dis_2['date'] == date) & (dis_2['is_patient'] == '无症状感染者')]['count']))

if __name__ == '__main__':
    merge_marcro_data()
    merge_district_data()
    merge_geo_data()
    merge_address()
#    check()
    check_data_integrity()
