# by zhulongfei
import requests
import pandas as pd
import csv
import time

from lnglat_transform import Lnglat_transform
from lnglat_transform import data_split_to_float

from config import address_add_file, geo_add_file, geo_add_temp_file
from keys import gaode_ak #高德地图API key，个人唯一，注意保密

# 高德AP需要的信息
URL = 'https://restapi.amap.com/v3/geocode/geo?'
URL_REGEO='https://restapi.amap.com/v3/geocode/regeo'

lis = []

def address_to_geo(data, cnt):

    flag = 0
    timer = 0

    address_writer(0,list)

    for index, row in data.iterrows():
        address = row['address']
        district = row['district']
        timer += 1
        print(str(data.shape[0]) + ': ' + str(timer)) #
        para = {
            'key':gaode_ak,
            'address':address,
            'city':'上海市'
        }
        try:
            req = requests.get(URL, para)
            req = req.json()
        except Exception as e:
            print(e)
            continue
        # print(req)
        if req['infocode'] == '10000':
            try:
                complete_address = req['geocodes'][0]['formatted_address']
                location = req['geocodes'][0]['location']
                #根据获取到的经纬度反向取出街道名称
                para_regeo = {
                    'key': gaode_ak,
                    'location': location
                }
                req_regeo = requests.get(URL_REGEO, para_regeo)
                req_regeo = req_regeo.json()
                #这一部分异常判断的逻辑加上之后会报错，暂时注释掉
                # if req_regeo['infocode'] == '10000':
                #     try:
                #         township = req_regeo['regeocodes']['addressComponent']['township']
                #         return township
                #     except Exception as e:
                #         print(e)
                township = req_regeo['regeocode']['addressComponent']['township']

                d = (district, address, complete_address, location, township)
                lis.append(d)
                flag = flag + 1
            except Exception as e:
                print(e)
            if flag == cnt:
                address_writer(1, lis)
                lis.clear()
                flag = 0
                time.sleep(5)
            else:
                continue
    address_writer(1, lis)

def address_writer(flag, list):
    if flag == 0:
        title_row = ['district', 'address', 'complete_address', '经纬度','street_level']
        # with open('temp2.csv', 'w', newline='')as f:
        with open(geo_add_temp_file, 'w', encoding= 'utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(title_row)
    else:
        with open(geo_add_temp_file, 'a+', encoding= 'utf-8', newline='')as f:
            writer = csv.writer(f)
            writer.writerows(list)

if __name__ == '__main__':
    # 先从高德取出经纬度数据
    data = pd.read_csv(address_add_file, engine='python')  # 导入对应地址的csv文件
    address_to_geo(data, 50)#用于控制单次写入文件的内容不超过500条
    # 将高德经纬度数据转换成wgs标准
    g = Lnglat_transform()
    lnglat_df = pd.read_csv(geo_add_temp_file, encoding='utf-8')
    lnglat_df = data_split_to_float(lnglat_df)
    gps_df = g.lnglat_batch_map(lnglat_df)
#    gps_df = data_concat(gps_df)
    gps_df = gps_df[['district', 'address', 'complete_address', 'gcj02_lng','gcj02_lat','wgs84_lng','wgs84_lat','street_level']]
    gps_df.to_csv(geo_add_file, encoding='utf-8', index = False)
