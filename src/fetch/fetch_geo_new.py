# by zhulongfei
import requests
import pandas as pd
import csv
import time
import math

from lnglat_transform import Lnglat_transform
from lnglat_transform import data_split_to_float

from config import address_add_file, geo_add_file, geo_add_temp_file
from keys import gaode_ak #高德地图API key，个人唯一，注意保密

# 高德AP需要的信息
URL = 'https://restapi.amap.com/v3/geocode/geo?'
URL_REGEO='https://restapi.amap.com/v3/geocode/regeo'

x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626  # π
a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 偏心率平方

lis = []

def gcj02_to_wgs84(lng, lat):
    """
    GCJ02(火星坐标系)转GPS84
    :param lng:火星坐标系的经度
    :param lat:火星坐标系纬度
    :return:
    """
    if out_of_china(lng, lat):
        return [lng, lat]
    dlat = _transformlat(lng - 105.0, lat - 35.0)
    dlng = _transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [lng * 2 - mglng, lat * 2 - mglat]

def _transformlat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
          0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 *
            math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
            math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret

def _transformlng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) + 40.0 *
            math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
            math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret

def out_of_china(lng, lat):
    """
    判断是否在国内，不在国内不做偏移
    :param lng:
    :param lat:
    :return:
    """
    return not (lng > 73.66 and lng < 135.05 and lat > 3.86 and lat < 53.55)

def address_to_geo(data, filename, cnt):

    flag = 0
    timer = 0

    address_writer(0, filename, list)

    for index, row in data.iterrows():
        address = row['address']
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
                [businessareas1, businessareasid1, businessareasloc1] = ['', '', '']
                [businessareas2, businessareasid2, businessareasloc2] = ['', '', '']
                [businessareas3, businessareasid3, businessareasloc3] = ['', '', '']
                [building_type1, building_type2, building_type3] = ['', '', '']
                [neighborhood_type1, neighborhood_type2, neighborhood_type3] = ['', '', '']
                #这一部分异常判断的逻辑加上之后会报错，暂时注释掉
                # if req_regeo['infocode'] == '10000':
                #     try:
                #         township = req_regeo['regeocodes']['addressComponent']['township']
                #         return township
                #     except Exception as e:
                #         print(e)
                district = req_regeo['regeocode']['addressComponent']['district']
                township = req_regeo['regeocode']['addressComponent']['township']
                towncode = req_regeo['regeocode']['addressComponent']['towncode']
                street_number = req_regeo['regeocode']['addressComponent']['streetNumber']['number']
                street = req_regeo['regeocode']['addressComponent']['streetNumber']['street']
                direction = req_regeo['regeocode']['addressComponent']['streetNumber']['direction']
                distance = req_regeo['regeocode']['addressComponent']['streetNumber']['distance']
                businessAreas = req_regeo['regeocode']['addressComponent']['businessAreas']
                if 'name' in businessAreas[0]:
                    businessareas1 = businessAreas[0]['name']
                    businessareasid1 = businessAreas[0]['id']
                    businessareasloc1 = businessAreas[0]['location'].replace(',', '|')
                if len(businessAreas) > 1:
                    businessareas2 = businessAreas[1]['name']
                    businessareasid2 = businessAreas[1]['id']
                    businessareasloc2 = businessAreas[1]['location'].replace(',', '|')
                if len(businessAreas) > 2:
                    businessareas3 = businessAreas[2]['name']
                    businessareasid3 = businessAreas[2]['id']
                    businessareasloc3 = businessAreas[2]['location'].replace(',', '|')
                building = req_regeo['regeocode']['addressComponent']['building']['name']
                building_type = req_regeo['regeocode']['addressComponent']['building']['type']
                neighborhood = req_regeo['regeocode']['addressComponent']['neighborhood']['name']
                neighborhood_type = req_regeo['regeocode']['addressComponent']['neighborhood']['type']
                [gcj02_lng, gcj02_lat] = [float(x) for x in location.split(',')]
                wgs84_lng, wgs84_lat = gcj02_to_wgs84(gcj02_lng, gcj02_lat)

                if len(building_type) > 0:
                    [building_type1, building_type2, building_type3] = building_type.split(';')
                if len(neighborhood_type) > 0:
                    [neighborhood_type1, neighborhood_type2, neighborhood_type3] = neighborhood_type.split(';')

                d = (district, address, complete_address, gcj02_lng, gcj02_lat, wgs84_lng, wgs84_lat, township, towncode, street, \
                street_number, direction, distance, building, building_type, building_type1, building_type2, building_type3, neighborhood, neighborhood_type, \
                neighborhood_type1, neighborhood_type2, neighborhood_type3, \
                businessareas1, businessareas2, businessareas3, businessareasid1, businessareasid2, businessareasid3, \
                businessareasloc1, businessareasloc2, businessareasloc3)
                d = [x if isinstance(x, (str, float)) else '' for x in d]
                lis.append(d)
                flag = flag + 1
            except Exception as e:
                print(e)
            if flag == cnt:
                address_writer(1, filename, lis)
                lis.clear()
                flag = 0
                time.sleep(5)
            else:
                continue
    address_writer(1, filename, lis)


def address_writer(flag, filename, list):
    if flag == 0:
        title_row = ['district', 'address', 'complete_address', 'gcj02_lng','gcj02_lat','wgs84_lng','wgs84_lat','township', 'towncode', \
        'street', 'street_number', 'direction', 'distance', 'building', 'building_type', 'building_type1', 'building_type2', 'building_type3', \
        'neighborhood', 'neighborhood_type', 'neighborhood_type1', 'neighborhood_type2', 'neighborhood_type3',
        'businessareas1', 'businessareas2', 'businessareas3', 'businessareasid1', 'businessareasid2', 'businessareasid3', \
        'businessareasloc1', 'businessareasloc2', 'businessareasloc3']
        # with open('temp2.csv', 'w', newline='')as f:
        with open(filename, 'w', encoding= 'utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(title_row)
    else:
        with open(filename, 'a+', encoding= 'utf-8', newline='')as f:
            writer = csv.writer(f)
            writer.writerows(list)

if __name__ == '__main__':
    # 先从高德取出经纬度数据
    data = pd.read_csv(address_add_file, engine='python')  # 导入对应地址的csv文件
    address_to_geo(data, geo_add_file, 50)#用于控制单次写入文件的内容不超过500条
