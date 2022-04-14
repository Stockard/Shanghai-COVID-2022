#encoding=utf-8
#根据目前的地址数据摘取经纬度和街道
#一次性工作
import pandas as pd
from config import first_geo_file, geo_dict

geo = pd.read_csv(first_geo_file, encoding = 'utf-8')
print(f'---total address : {geo.shape[0]}---')
geo.drop_duplicates('address', inplace = True)

geo[['district', 'address', 'complete_address', 'GaoDe_address', \
       'gcj02_lng', 'gcj02_lat', 'wgs84_lng', 'wgs84_lat', 'street_level']].to_csv(geo_dict, encoding = 'utf-8')

print(f'---unique address : {geo.shape[0]}---')
