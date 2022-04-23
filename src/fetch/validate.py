import pandas as pd

from config import macro_file, district_file

def check_data_integrity():
    district = pd.read_csv(district_file)
    macro = pd.read_csv(macro_file)
    sum_district = district[['date', 'is_patient', 'count']].groupby(['date', 'is_patient'], as_index = False).sum()
    for is_patient in ['确诊病例', '无症状感染者']: #检验区汇总到市级每日确诊和无症状数据
        for date in sum_district['date'].unique():
            value_in_macro = int(macro[macro['时间'] == date][is_patient])
            value_in_district_agg = int(sum_district[(sum_district['date'] == date) & (sum_district['is_patient'] == is_patient)]['count'])
            try:
                assert(value_in_macro == value_in_district_agg)
            except Exception as e:
                print(value_in_macro, value_in_district_agg)
                print('请检查 %s 数据' % date, e)
    for index, values in macro.iterrows(): #核验确诊数和无症状数分项 主要是3月18日前的
        try:
            assert(values['确诊病例'] == values['无症状转确诊'] + values['管控内确诊'] + values['例行筛查确诊'] + values['野生确诊'])
            assert(values['无症状感染者'] == values['管控内无症状'] + values['例行筛查无症状'])
        except Exception as e:
            print(f'请检查 {values["时间"]} 数据', e)
    #检验区级别几个环节数据 暂时留空

def check():
    #检查是否漏掉了某些病例
    date = 20220324
    num = 1579
    district_t2 = pd.read_csv(district_details_t2)
#    dis_2 = district_t2.groupby(['date', 'is_patient', 'district', 'source'], as_index=False).size().rename(
#        columns={'size': 'count'})
    for i in range(num):
        if district_t2[(district_t2['date'] == date) & (district_t2['number'] == i)].shape[0] != 1:
            print(i)
#    print(dis_2[dis_2['date'] == date])
#    print(sum(dis_2[(dis_2['date'] == date) & (dis_2['is_patient'] == '无症状感染者')]['count']))