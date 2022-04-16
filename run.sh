#!/bin/bash

python src/fetch/crawl_official.py
python src/fetch/extract_address.py
python src/fetch/tidy_address.py
python src/fetch/tidy_data.py
python src/fetch/fetch_geo.py
python src/fetch/combine.py


#chmod +x ./run.sh  #使脚本具有执行权限
#run crawl_official.py 抓取上海卫健委的报告并保存在 data/raw 里，卫健委每天发布两条公告，一条地址，一条汇总数据公告
#汇总数据公告可以抓到，但因为地址公告是微信文章，抓不下来。接下来需要手动打开已经建立的 data/raw/最新的日期 文件，手动去网站直接全文复制地址公告里面并保存（注意等网页完全加载完毕），目前无法全自动主要卡在这
#run extract_address.py 把公告里所有的地址和区级的数据拆出，存在 data/temp 里 #地址在 address_daily.csv, 区级数据在districts_daily.csv
#地址处理
#run tidy_address.py 根据目前的geo字典 data/use/geo.csv ，导出增量地址 data/temp/address_add.csv 。地址有很多重复，只需要更新增量。
#run fetch_geo.py 根据增量地址来跑，并且导出新增geo字典到 temp/geo_add.csv
#合并地址和每日数据, 进行完整性校验, stockard working on it.
#数据处理
#run tidy_data.py 会更新每天的汇总数据到 macro_data.csv, 区级的数据还要处理
#数据完整性校验 - working on it
