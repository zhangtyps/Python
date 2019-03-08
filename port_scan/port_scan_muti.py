#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : port_scan.py
@Time : 2019/03/07 09:59:00
@Author : zhangtyps
@GitHub : https://github.com/zhangtyps
@Version : 1.0
@Desc : 端口扫描，读入log文件，写出一个端口扫描的结果
'''

# here put the import lib
import nmap, threading, sys, json, queue


class MyThread(threading.Thread):
    def __init__(self, queue, ip, dict_main):
        threading.Thread.__init__(self)
        self.ip = ip
        self.queue = queue
        self.dict_main = dict_main

    def run(self):
        r = scan_port(self.ip)
        update_port_info(self.ip, r, self.dict_main)
        print('%s checking is over!' % self.ip)
        self.queue.get()
        self.queue.task_done()


#读取文件，获得主机的基本信息，把主机信息依次写入到一个字典中
def read_file_to_dict(path, dict_main):
    with open(path, 'r', encoding='utf-8') as f:
        while 1:
            line = f.readline().split()
            if not line:
                break
            dict_main.update({
                line[2]: {
                    'os':line[0],
                    'name': line[1],
                    'intranet_ip': line[3],
                    'manager': line[4],
                    'group': line[5],
                    'port': {}
                }
            })


#传入一个公网ip地址，然后进行nmap检测，把检测端口的结果调用update_port_info函数写入到结果字典中
def scan_port(ip):
    try:
        nm = nmap.PortScanner()
    except Exception as e:
        print('未正确安装nmap模块及命令：%s' % e)
        sys.exit()
    r_nmap = nm.scan(ip, arguments='-sS -sV -p- -T4')
    try:
        r_port = dict(nm[ip]['tcp'])
    except Exception as e:
        print('%s 无法获得开放的端口号，可能主机不在线或防火墙拦截！' % ip)
        r_port = None
    finally:
        return r_port
    #update_port_info(ip, r_port, dict_main)


def update_port_info(ip, dict_port, dict_main):
    if dict_port is None:
        dict_main[ip]['port'] = None
        return
    for key in dict_port:
        if dict_port[key]['state'] != 'filtered':
            dict_main[ip]['port'][key] = {
                'state': dict_port[key]['state'],
                'product': dict_port[key]['product'],
                'version': dict_port[key]['version']
            }


def output_json_file(dict_main):
    json_str = json.dumps(dict_main, ensure_ascii=False)
    with open('scan_result.json', 'w+', encoding='utf-8') as f:
        f.write(json_str)


def main():
    dict_hostinfo = {}
    #读取文件的路径
    path = 'host_information.log'
    read_file_to_dict(path, dict_hostinfo)

    q = queue.Queue(2)
    list_ip = list(dict_hostinfo.keys())  #所有的ip列表
    for ip in list_ip:
        q.put(ip)
        t = MyThread(q, ip, dict_hostinfo)
        t.start()
    q.join()
    print("all is over!")
    output_json_file(dict_hostinfo)


if __name__ == '__main__':
    main()