#!/usr/bin/env python
# -*- coding:utf-8 -*-
#version 0.2
#访问我的GitHub获取最新版的代码：https://github.com/zhangtyps/pylearn

import os

'''需要修改的变量'''
#站点目录地址，目录最后的斜杠可加可不加
website_path='/data1/www/changan_dev'
#研发给的更新文件的路径（一定要按照规定格式写入，例如：/trunk/home/protected/components/QBSolrParams.php）
log_path='./update.log'


def update(list_update):
    #mark_value=0
    #for i in list_update:
    #    mark_value=os.system('svn up '+i)
    #if mark_value!=0:
    #    print('更新任务完毕，但部分更新存在问题，请检查屏幕输出日志！')
    #else:
    #    print('文件全部成功更新！')
    

def sort_log():
    svn_up_list=[]
    update_list=os.popen('cat '+log_path).read().split('\n')
    for i in update_list:
        if i=='':
            continue
        add_path=i.split('trunk/')[1]
        update_path=os.path.join(website_path,add_path)
        if len(update_path)<(len(website_path)+5):
            continue
        svn_up_list.append(update_path)
        #update_path=website_path+add_path
        #update(update_path)
        #print(update_path)
    print('即将更新以下文件：')
    for i in svn_up_list:
        print(i)
    return_value=input('是否确定更新(y/n)?')
    if return_value=='y' or return_value=='yes':
        update(svn_up_list)
    else:
        print('用户取消更新！')
    

if __name__=='__main__':
    sort_log()
