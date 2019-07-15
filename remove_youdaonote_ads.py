#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : remove_youdaonote_ads.py
@Time : 2019/03/15 17:34:39
@Author : zhangtyps
@GitHub : https://github.com/zhangtyps
@Version : 1.0
@Desc : 一键移出有道云笔记界面广告，暂时没写好……
'''

# here put the import lib
import os, re
import xml.etree.ElementTree as ET

path = r'D:\Program Files (x86)\Youdao\YoudaoNote\theme\build.xml'


#r1 = re.compile(r'.*AdWraperMid .*? bounds="(.*?)"')

with open(path, 'r', encoding='utf-8') as f:
    #f.read()
    data=f.read()
    root=ET.fromstring(data)
    # tree=ET.parse(f)
    # root=tree.getroot()
    #print(data)


print(root)

for element in root.findall('PanelSecond'):
    print(element)

# with open('.\\1.xml','w',encoding='utcf-8')as f:
#     f.write(tree)


#print(r1.match(data).span())