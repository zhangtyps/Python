#!/usr/bin/python
# -*- coding:utf-8 -*-
#访问我的GitHub获得最新版的脚本：https://github.com/zhangtyps
#站点一键部署
#version 1.0 

#使用方法：
#1.修改此脚本的变量dir_path的值（要部署的路径位置）
#2.修改svn内网地址
#3.调用脚本时必须要提供一个svn的checkout链接作为参数1
#例如：./svn_co.py https://192.168.1.1/svn/H5/dx_lhj

import sys,os,re

#需要部署代码的上一级目录
dir_path='/data1/www/h5'
#svn的内网IP
svn_ip='10.168.86.63'

#检查参数
if len(sys.argv) != 2:
   print('没有svn地址，或参数过多，python脚本退出')
   sys.exit()

#拿到参数1的url
url=sys.argv[1]

#替换ip为内网
def replace_ip(ip_addr,url):
    r=re.compile(r'\d+\.\d+\.\d+\.\d+')
    return r.sub(ip_addr,url,count=1)

#获取url中的目录名称
def get_name(url):
    r=re.compile(r'(\w+)://(\d+\.\d+\.\d+\.\d+)/(\w+)/(\w+)/(\w+)')
    try:
        name=r.search(url).groups()[4]
    except:
        print('未获取到目录名，是否输入了正确的svn链接？')
        sys.exit()
    return name

#建立目录，操作站点
def main():
    svn_checkout_path=replace_ip(svn_ip,url)
    dir_name=get_name(url)

    #建立目录
    dir_full=os.path.join(dir_path,dir_name)
    if os.path.exists(dir_full):
        print('当前目录已存在同名项目！')
        sys.exit()
    os.makedirs(dir_full)

    #checkout代码
    num1=os.system('svn checkout '+svn_checkout_path+' '+dir_full)
    if num1!=0:
        print('代码checkout失败，请检查svn报错信息')
        sys.exit()
    print('代码checkout成功!')

    #修改目录权限
    num2=os.system('chmod -R 775 '+dir_full)
    num2=os.system('chown -R nginx:nginx '+dir_full)
    if num2!=0:
        print('权限修改失败！执行用户的权限是否不足？')
        sys.exit()
    print('权限修改成功!')
    
    print('---完成部署---')


if __name__=='__main__':
    main()