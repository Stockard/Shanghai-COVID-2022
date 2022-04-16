#encoding=utf-8
#根据目前的地址数据摘取经纬度和街道
#一次性工作
import pandas as pd
import os

from config import pre_address_file, pre_geo_file, geo_file

geo = pd.read_csv(pre_address_file, encoding = 'utf-8')
print(f'---total address : {geo.shape[0]}---')
geo.drop_duplicates('address', inplace = True)
geo['complete_address'] = geo['GaoDe_address']

geo = geo[['district', 'address', 'complete_address', \
       'gcj02_lng', 'gcj02_lat', 'wgs84_lng', 'wgs84_lat', 'street_level']]
geo.to_csv(pre_geo_file, encoding = 'utf-8', index = False)

print(f'---unique address : {geo.shape[0]}---')

if not os.path.exists(geo_file):
    geo.to_csv(geo_file, encoding = 'utf-8', index = False)
