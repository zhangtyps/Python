#!/usr/bin/python
# -*- coding:utf-8 -*-
# 针对老版本zabbix2.4统计无法导出这种情况，利用了百度云AI图片识别，把zabbix里的数据识别出来
# 因为是AI识别，所以这段代码还有很多不稳定的地方，有时候导出表格不正常请重新截一张图试试

from aip import AipOcr
import json,csv,re

#__百度云AI识别模块，注意修改读取的图片名称和位置
""" 你的 APPID AK SK """
APP_ID = ''
API_KEY = ''
SECRET_KEY = ''

client = AipOcr(APP_ID, API_KEY, SECRET_KEY)


""" 读取图片 """
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

#此处需要AI识别图片的名称和位置
image = get_file_content('clipboard.jpg')

""" 调用通用文字识别（高精度版） """
client.basicAccurate(image)

""" 如果有可选参数 """
options = {}
options["detect_direction"] = "false" #是否检测斜方文字
options["probability"] = "true" 

""" 带参数调用通用文字识别（高精度版） """
result = client.basicAccurate(image, options)

# 把获得的result转化为字符串，同时改成大写以后后续replace处理
str1=json.dumps(result)
str1=str1.upper()
str1=str1.replace('G8','GB')
#str1=str1.replace('E','B') 这里替换后面就拿不到words_result键了……

#字符串转换为字典
dict1=json.loads(str1)
#从字典中取words_result键所对应的值
result=dict1['WORDS_RESULT']
#初始化列表
list_result=[]

for temp in result:
    a = dict(temp)['WORDS']
    a=a.replace('E','B')
    list_result.append(a)

# 写入到文件中（测试阶段使用的代码）
# f=open("hello.txt","w+")
# for line in list_result:
#     f.write(line)
#     f.write('\n')
# f.close()

#使用re模块，利用re.split分割
split_icon=r'GB|G|M|MB|B|%'
decide_list=[]
for temp in list_result:
    result=re.split(split_icon,temp)
    decide_list+=result
for temp in decide_list[:]:
    if temp=='':
        decide_list.remove(temp)

# 列表按每3个元素为合并为一个子列表，方便后面写csv文件
list3 = [decide_list[i:i+3] for i in range(0, len(decide_list), 3)]
list3.reverse()

# 关于内存的相关处理(统计CPU把这几行都注释了)
for temp in list3:
    num1=float(temp[0])
    num2=float(temp[1])
    num3=float(temp[2])
    if num1>65:
        temp[0]=('%.2f'% (num1/1000))
    if num2>65:
        temp[1]=('%.2f'% (num2/1000))
    if num3>65:
        temp[2]=('%.2f'% (num3/1000))

# 输出csv
with open("result100.csv","w", newline='') as datacsv:
    csvwriter = csv.writer(datacsv,dialect=("excel"))
    csvwriter.writerow(["min","ave","max"])
    for i in range(len(list3)):
        csvwriter.writerow(list3[i])
