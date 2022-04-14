#placeholder
#[] 根据temp/address_daily里的数据汇总到经纬度-地址对应表：经纬度只需查询新增地址
#先处理好旧数据，再加增量数据
import pandas as pd
import codecs
from config import address_file, geo_file, address_add_file, address_file_extend

def list_compare(master, full):
    add_list = []
    for i in full:
        if i not in master:
            add_list.append(i)
    return add_list

def complete_check():
    #检查地址数据完整性
    #placeholder
    pass

if __name__ == '__main__':
    address_add = codecs.open(address_add_file, mode = 'w', encoding='utf_8')

    address = pd.read_csv(address_file, encoding = 'utf-8')
    address_extend = pd.read_csv(address_file_extend, encoding = 'utf-8')
    address_series = address.address.append(address_extend.address, ignore_index = True)
    address_full_list = address_series.unique()

    geo = pd.read_csv(geo_file, encoding = 'utf-8')
    geo_full_list = pd.unique(geo.address)

    print(f'--address list unique {len(address_full_list)} full {address_series.shape[0]}--')
    print(f'--geo list unique {len(geo_full_list)} full {geo.shape[0]}--')

    address_add_list = list_compare(geo_full_list, address_full_list)
    address_add.write('address\n')
    for i in address_add_list:
        address_add.write(i)
        address_add.write('\n')
    address_add.close()
