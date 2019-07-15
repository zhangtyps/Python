#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : xml.py
@Time : 2019/07/12 17:12:49
@Author : zhangtyps
@GitHub : https://github.com/zhangtyps
@Version : 1.0
@Desc : None
'''

# here put the import lib
import os
import xml.etree.ElementTree as ET

with open('E:\\Git\\Python\\xml\\1.xml','r',encoding='utf-8') as f:
    data=f.read()
    
tree=ET.parse(data)
print(tree)