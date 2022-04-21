#先处理好旧数据，再加增量数据
#placeholder
#在区没有新增地址时会出问题，但是问题不大，暂时不fix
import pandas as pd
import codecs
from config import address_file, geo_file, address_add_file, pre_address_file

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
    address = pd.read_csv(address_file, encoding = 'utf-8')
    address_extend = pd.read_csv(pre_address_file, encoding = 'utf-8')
    address_series = pd.concat([address, address_extend]).loc[:, ['address', 'district']]
    address_full_list = address_series.address.unique()

    geo = pd.read_csv(geo_file, encoding = 'utf-8')
    geo_full_list = pd.unique(geo.address)

    print(f'--address list unique {len(address_full_list)} full {address_series.shape[0]}--')
    print(f'--geo list unique {len(geo_full_list)} full {geo.shape[0]}--')

    print(address_series)
    address_series.drop_duplicates('address', inplace = True)
    address_series['not_in_geo_list'] = address_series.apply(lambda x: x['address'] not in geo_full_list, axis = 1)
    address_add = address_series.loc[address_series['not_in_geo_list'], ['address', 'district']]
    address_add.to_csv(address_add_file, index = False)
