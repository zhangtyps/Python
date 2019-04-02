#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : remove_youdaonote_ads.py
@Time : 2019/03/15 17:34:39
@Author : zhangtyps
@GitHub : https://github.com/zhangtyps
@Version : 1.0
@Desc : 暂时没写好……
'''

# here put the import lib
import os, re,xml

path = r'D:\Program Files (x86)\Youdao\YoudaoNote\theme\build.xml'

r1 = re.compile(r'.*AdWraperMid .*? bounds="(.*?)"')

with open(path, 'r', encoding='utf-8') as f:
    #f.read()
    data = f.read()
    #print(data)
print(len(data))
print(r1.match(data).span())