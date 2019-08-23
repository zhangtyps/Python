#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : remove_youdaonote_ads.py
@Time : 2019/03/15 17:34:39
@Author : zhangtyps
@GitHub : https://github.com/zhangtyps
@Version : 1.0
@Desc : 一键移出有道云笔记界面广告
'''

# here put the import lib
import os, re
import xml.etree.ElementTree as ET

path = r'D:\Program Files (x86)\Youdao\YoudaoNote\theme\build.xml'

#读取xml文件
tree=ET.parse(path)
#获取根节点
root=tree.getroot()

# #遍历根节点下全部tag和属性attrib
# for child in root:
#     print(child.tag,child.attrib)
#     for i in child:
#         print(' '+i.tag,i.attrib)
# '''
# 输出一大堆，不做展示了
# '''

# #遍历指定节点下的tag(findall函数内可带这种写法MainForm/PanelClient/SplitterLeft)
# for child in root.findall('MainForm/'):
#     print(child.tag)
# '''
# 这段输出PanelClient，这个/很好用的
# '''

# 修改指定tag下的属性
# for node in root.findall('MainForm/PanelClient/SplitterLeft/PanelSecond/NotePage/SplitterMid/PanelFirst/AdWraperMid'):
#     print(node.tag,node.attrib)
#     node.set('bounds','0,0,0,0')
#     print(node.tag,node.attrib)

def set_attrib(xml_tag_path,set_tag,set_attrib):
    try:
        for node in root.findall(xml_tag_path):
            node.set(set_tag,set_attrib)
            print(str(node.tag)+" 的值已修改为"+str(node.attrib))
    except Exception as e:
        print('发生了未知错误，错误信息如下：'+e)
        pass
    
#修改xml属性
set_attrib(r'MainForm/PanelClient/SplitterLeft/PanelSecond/NotePage/SplitterMid/PanelFirst/AdWraperMid','bounds','0,0,0,0')
set_attrib(r'control/PanelAd/MiddlePhotoPanel/AdPhoto','Bounds','0,0,0,130')

#重新写入xml文件
tree.write(path, xml_declaration=True)