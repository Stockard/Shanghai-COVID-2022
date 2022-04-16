# -*- coding: utf-8 -*-
# zhulongfei
import math
import pandas as pd

x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626  # π
a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 偏心率平方

from_address = ''
to_address = ''

class Lnglat_transform():
    def __init__(self, service_app=None):
        # self.api_key = api_key
        self.service_app = service_app

    def lnglat_batch_map(self,lnglat_df):
        # 批量进行经纬度的转换
        if self.service_app is None or self.service_app == 'gaode':
            # 默认高德：将gcj02坐标转换成wgs84坐标
            wgs_df = pd.DataFrame(map(lambda x, y: self.gcj02_to_wgs84(x, y), lnglat_df['gcj02_lng'], lnglat_df['gcj02_lat']),
                                  columns=['wgs84_lng', 'wgs84_lat'])
        gps_df = pd.concat([lnglat_df, wgs_df], axis=1)
        return gps_df

    def gcj02_to_bd09(self, lng, lat):
        """
        火星坐标系(GCJ-02)转百度坐标系(BD-09)
        谷歌、高德——>百度
        :param lng:火星坐标经度
        :param lat:火星坐标纬度
        :return:
        """
        z = math.sqrt(lng * lng + lat * lat) + 0.00002 * math.sin(lat * x_pi)
        theta = math.atan2(lat, lng) + 0.000003 * math.cos(lng * x_pi)
        bd_lng = z * math.cos(theta) + 0.0065
        bd_lat = z * math.sin(theta) + 0.006
        return [bd_lng, bd_lat]

    def bd09_to_gcj02(self, bd_lon, bd_lat):
        """
        百度坐标系(BD-09)转火星坐标系(GCJ-02)
        百度——>谷歌、高德
        :param bd_lat:百度坐标纬度
        :param bd_lon:百度坐标经度
        :return:转换后的坐标列表形式
        """
        x = bd_lon - 0.0065
        y = bd_lat - 0.006
        z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
        theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
        gg_lng = z * math.cos(theta)
        gg_lat = z * math.sin(theta)
        return [gg_lng, gg_lat]

    def wgs84_to_gcj02(self, lng, lat):
        """
        WGS84转GCJ02(火星坐标系)
        :param lng:WGS84坐标系的经度
        :param lat:WGS84坐标系的纬度
        :return:
        """
        if self.out_of_china(lng, lat):  # 判断是否在国内
            return [lng, lat]
        dlat = self._transformlat(lng - 105.0, lat - 35.0)
        dlng = self._transformlng(lng - 105.0, lat - 35.0)
        radlat = lat / 180.0 * pi
        magic = math.sin(radlat)
        magic = 1 - ee * magic * magic
        sqrtmagic = math.sqrt(magic)
        dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
        dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
        mglat = lat + dlat
        mglng = lng + dlng
        return [mglng, mglat]

    def gcj02_to_wgs84(self, lng, lat):
        """
        GCJ02(火星坐标系)转GPS84
        :param lng:火星坐标系的经度
        :param lat:火星坐标系纬度
        :return:
        """
        if self.out_of_china(lng, lat):
            return [lng, lat]
        dlat = self._transformlat(lng - 105.0, lat - 35.0)
        dlng = self._transformlng(lng - 105.0, lat - 35.0)
        radlat = lat / 180.0 * pi
        magic = math.sin(radlat)
        magic = 1 - ee * magic * magic
        sqrtmagic = math.sqrt(magic)
        dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
        dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
        mglat = lat + dlat
        mglng = lng + dlng
        return [lng * 2 - mglng, lat * 2 - mglat]

    def bd09_to_wgs84(self, bd_lon, bd_lat):
        lon, lat = self.bd09_to_gcj02(bd_lon, bd_lat)
        return self.gcj02_to_wgs84(lon, lat)

    def wgs84_to_bd09(self, lon, lat):
        lon, lat = self.wgs84_to_gcj02(lon, lat)
        return self.gcj02_to_bd09(lon, lat)

    def _transformlat(self, lng, lat):
        ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
              0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
        ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
                math.sin(2.0 * lng * pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(lat * pi) + 40.0 *
                math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
        ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
                math.sin(lat * pi / 30.0)) * 2.0 / 3.0
        return ret

    def _transformlng(self, lng, lat):
        ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
              0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
        ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
                math.sin(2.0 * lng * pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(lng * pi) + 40.0 *
                math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
        ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
                math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
        return ret

    def out_of_china(self, lng, lat):
        """
        判断是否在国内，不在国内不做偏移
        :param lng:
        :param lat:
        :return:
        """
        return not (lng > 73.66 and lng < 135.05 and lat > 3.86 and lat < 53.55)


def data_split_to_float(lnglat_df):
    """
    将高德的经纬度数据拆分成两列，然后转变成数字格式
    :param lnglat_df:
    :return:
    """
    lnglat_df['gcj02_lng'] = lnglat_df['经纬度'].map(lambda x: x.split(',')[0])  # 将经纬度数据列分割为gcj02经度和纬度两列
    lnglat_df['gcj02_lat'] = lnglat_df['经纬度'].map(lambda x: x.split(',')[1])
    lnglat_df = lnglat_df.astype({'gcj02_lng': 'float', 'gcj02_lat': 'float'})  # 将经纬度数据从字符串转换为数字格式
    return lnglat_df

def data_concat(gps_df):
    """
    将wgs数据合并成一列
    :param lnglat_df:
    :return:
    """
    gps_df = gps_df.astype({'wgs84_lng': 'string', 'wgs84_lat': 'string'})  # 将经纬度数据从数字转换为字符串，以完成拼接
    # print(gps_df.dtypes)
    gps_df['经纬度(wgs48)'] = gps_df['wgs84_lng'].str.cat([gps_df.wgs84_lat], sep=',')

    return gps_df

if __name__ == '__main__':
    g = Lnglat_transform()  # 这里填写你的高德api的key
#     # 单个经纬度转换
#     lng = 121.578632
#     lat = 31.256695
#     api_key = 'API_KEY'  # 填入你自己的高德api_key 或者其他平台
#     result1 = g.gcj02_to_bd09(lng, lat)
#     result2 = g.bd09_to_gcj02(lng, lat)
#     result3 = g.wgs84_to_gcj02(lng, lat)
#     result4 = g.gcj02_to_wgs84(lng, lat)
#     result5 = g.bd09_to_wgs84(lng, lat)
#     result6 = g.wgs84_to_bd09(lng, lat)
#     print(result1, result2, result3, result4, result5, result6)

    # # 批量经纬度转换，经纬度分两列
    # lnglat_df = pd.read_csv('testdata.csv',encoding='gbk')
    # gps_df = g.lnglat_batch_map(lnglat_df)
    # print(gps_df.head())

    # 批量经纬度转换，经纬度在一列，通过逗号分割
    lnglat_df = pd.read_csv(from_address,encoding='utf-8')
    lnglat_df = data_split_to_float(lnglat_df)
    gps_df = g.lnglat_batch_map(lnglat_df)
    gps_df = data_concat(gps_df)
    gps_df.drop(columns=['gcj02_lng', 'gcj02_lat', 'wgs84_lng', 'wgs84_lat'], inplace=True) #清理掉无用的数据列
#    gps_df.rename(columns={'地址': '地址(高德)','街道': '街道(高德)', '经纬度': '经纬度(gcj02)'}, inplace=True) #重命名数据列，提升可读性
    # print(gps_df.head())
    # print(gps_df.columns)
    gps_df.to_csv(to_address, encoding='utf-8')
