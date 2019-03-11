#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : 1.py
@Time : 2019/03/11 09:42:43
@Author : zhangtyps
@GitHub : https://github.com/zhangtyps
@Version : 1.0
@Desc : None
'''

# here put the import lib
import json
from port_scan_muti import output_json_file

path = 'port_scan\scan_result.json'


def read_json_from_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        global dict_main
        dict_main = dict(json.loads(f.read()))


def deal_dict(d):
    list_ip=d.keys()
    for ip in list_ip:
        try:
            list_port_tmp=list(d[ip]['port'].keys())
            d[ip]['port']=','.join(list_port_tmp)
            #print(str(list_port_tmp))
        except:
            pass

    
if __name__ == '__main__':
    read_json_from_file(path)
    deal_dict(dict_main)
    output_json_file(dict_main,'port_scan\\result2.json')