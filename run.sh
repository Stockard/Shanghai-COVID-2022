#!/bin/bash
#chmod +x ./run.sh  #使脚本具有执行权限
python crawl_official.py
python extract_address.py
python tidy_address.py
python tidy_data.py
python gen_geo.py
python conbind.py
