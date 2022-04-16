#by 人字拖
#working
import requests
import pandas as pd
import csv
from keys import gaode_ak

data = pd.read_csv('/Users/zhulongfei/Desktop/temp/NCP-shanghai/0410.csv', engine='python')#导入对应地址的csv文件
data = data['完整地址']#选择地址列的数据
lis = []

def gaode(cnt):
    flag = 0
    writerCsv(0,list)
    for i in data:
        para = {
            'key':gaode_ak,
            'address':i,
            'city':'上海市'
        }
        url = 'https://restapi.amap.com/v3/geocode/geo?'
        req = requests.get(url, para)
        req = req.json()
        print(req)
        if req['infocode']=='10000':
            try:
                address = req['geocodes'][0]['formatted_address']
                location = req['geocodes'][0]['location']
                #根据获取到的经纬度反向取出街道名称
                para_regeo = {
                    'key': 'fde8e23ecaf169e22a3a7d2d723bd094',
                    'location': location,
                }
                url = 'https://restapi.amap.com/v3/geocode/regeo?'
                req_regeo = requests.get(url, para_regeo)
                req_regeo = req_regeo.json()
#                print(req_regeo)
                #这一部分异常判断的逻辑加上之后会报错，暂时注释掉
                # if req_regeo['infocode'] == '10000':
                #     try:
                #         township = req_regeo['regeocodes']['addressComponent']['township']
                #         return township
                #     except Exception as e:
                #         print(e)
                # township = 'test'
#                print(address)
#                print(location)
#                print(township)
                township = req_regeo['regeocode']['addressComponent']['township']
                d = (address, location,township)
                lis.append(d)
                flag = flag + 1
            except Exception as e:
                print(e)
            if flag == cnt:
                writerCsv(1, lis)
                lis.clear()
                flag = 0
            else:
                continue
    writerCsv(1, lis)

def writerCsv(flag, list):
    if flag == 0:
        t = ['地址', '经纬度','街道']
        # with open('temp2.csv', 'w', newline='')as f:
        with open('/Users/zhulongfei/Desktop/temp/NCP-shanghai/0410_with_location_township.csv', 'a+', encoding= 'utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(t)
            # writer.writerows(lis)
    else:
        with open('/Users/zhulongfei/Desktop/temp/NCP-shanghai/0410_with_location_township.csv', 'a+', encoding= 'utf-8', newline='')as f:
            writer = csv.writer(f)
            writer.writerows(list)

if __name__ == '__main__':
    #读取该处理的文件，提取地址列
    #读取已处理的文件，提取地址列
    #针对地址列开始运行
    #写入文件
    gaode(500)#用于控制单次写入文件的内容不超过500条
