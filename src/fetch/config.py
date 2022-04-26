#folder
raw_dir = 'data/raw'
temp_dir = 'data/temp'
pre_dir = 'data/precleaning'
use_dir = 'data/use'

#setup
address_dir = "%s/address/" % raw_dir
number_dir = "%s/number/" % raw_dir
district_daily_file = '%s/districts_daily.csv' % temp_dir
address_file =  '%s/address_daily.csv' % temp_dir

#导出数据
temp_macro_file = '%s/macro_data.csv' % temp_dir
geo_add_file = '%s/geo_add.csv' % temp_dir
geo_add_temp_file = '%s/geo_add_temp.csv' % temp_dir
address_add_file = '%s/address_add.csv' % temp_dir

address_cleaned_file = '%s/address.csv' % use_dir
district_in_hospital_file = '%s/shanghai_district_in_hospital_data.csv' % use_dir
district_file = '%s/shanghai_district_data.csv' % use_dir
macro_file = '%s/shanghai_data.csv' % use_dir
geo_file = '%s/geo.csv' % use_dir
merge_geo_address_file = '%s/daily_address_with_geo.csv' % use_dir


#非自动生成数据
pre_macro_file = '%s/macro_0318.csv' % pre_dir
pre_address_file = '%s/patient_address_0306_0317.csv' % pre_dir #从病人地址中来的
pre_patient_file = '%s/patient_0306_0317.csv' % pre_dir
pre_patient_sort_file = '%s/patient_0306_0317_sort.csv' % pre_dir
#retired
pre_address_file = '%s/address_0401_0414.csv' % pre_dir
pre_geo_file = '%s/geo.csv' % pre_dir #use by build_geo_database_temp.py
district_details_t2 = '%s/district_details_2.csv' % temp_dir #0318-0325
district_details_t3 = '%s/district_details_3.csv' % temp_dir #0318-0325
