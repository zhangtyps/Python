#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File: mail_point_for_pks.py
@Time: 2023/3/31 10:20
@Author: zhangtyps
@Version: 1.0
@Desc:
通过selenium模拟页面操作，下载指定页面上的表格，用pandas打开表格，不做筛选，输出成list。
使用HTMLTable模块，将pandas输出的list转HTML，转换格式主要用于邮件发送（主要在于htmltable可以遍历数据行，满足特定条件时，行能标记特殊颜色）
第一版selenium+pandas+htmltable的代码，比较渣，基本没用到pandas自带的强大功能。
"""

# here put the import lib
import time, requests, sys, warnings, datetime, uuid, os, re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
from HTMLTable import HTMLTable
from fake_useragent import UserAgent

global df_all, done_count, done_percent


def deal_message_text(mail_uuid, html):
    data = '{"mailId": "' + mail_uuid + '",\
            "sender": "发送人邮箱",\
            "sysName": "发送人中文名",\
            "title": "邮件标题",\
            "recList": ["zhangtyps@abc.com.cn"],\
            "ccList": ["zhangtyps@abc.com.cn"], \
            "content": "' + html + '", \
            "flagPic": false, \
            "flagAttached": false}'
    # print(data)
    return data


def send_to(call_data):
    # 这里的url是邮箱接口地址。如无封装好的邮件接口，可使用其他方式发送邮件（如自建邮件服务器等，通过调用Linux命令发送邮件等）
    url = 'http://xxxx/mail/api/send/singleMailReq'
    data = call_data
    headers = {
        'Content-Type': 'application/json'
    }
    data = str(data).encode('utf-8')

    response = requests.request("POST", url, headers=headers, data=data)
    print(response.text)


def send_to_pingan_robot(call_data):
    # 此url为聊天IM软件的群通知机器人地址
    url = 'https://xxxx.com.cn/openplatform/robotSendMessage?robotId=e22a468665fe460daa3ee9680d3247e3&groupId=11200000044772685'
    data = call_data
    headers = {
        'Content-Type': 'application/json',
        'Cookie': 'f5monweb=2366115870.10275.0000'
    }
    data = str(data).encode('utf-8')
    response = requests.request("POST", url, headers=headers, data=data)
    print(response.text)


def open_browser(download_path):
    ua=UserAgent()
    ops = Options()
    # Linux环境参数
    ops.add_argument('--headless')  # 设置无界面
    ops.add_argument('--no-sandbox')  # root用户下运行代码需添加这一行
    ops.add_argument('--disable-dev-shm-usage')  # 使用/tmp而非/dev/shm
    ops.add_argument('--disable-gpu')  # 禁用gpu加速，规避bug
    ops.add_experimental_option('excludeSwitches', ['enable-automation'])  # 禁止输出日志（存疑）
    # ops.add_experimental_option('excludeSwitches', ['enable-logging'])
    ops.add_experimental_option('prefs', {'download.default_directory': download_path})
    ops.add_argument(
        'user-agent="'+ua.firefox+'"')

    # 启动浏览器
    # driver = webdriver.Chrome(options=ops, executable_path="D:\Software\chromedriver.exe")
    driver = webdriver.Chrome(options=ops)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": '''
                Object.defineProperty(navigator, 'webdriver', {
                get: () => Chrome
                })
                '''
    })
    # 集体配置
    driver.delete_all_cookies()  # 清除浏览器cookie
    driver.set_page_load_timeout(20)  # 页面加载超时时间
    driver.implicitly_wait(10)  # 隐式等待
    return driver


def control_browser(browser, url, path):
    print("正在打开页面……")
    browser.get(url)
    # time.sleep(3)
    print("执行登陆操作")
    browser.find_element_by_xpath(
        "//body/div[@id='app']/div[@id='loginActivity']/div[1]/div[2]/div[2]/div[1]/div[3]/form[1]/div[1]/div[1]/div[1]/input[1]").send_keys(
        '【用户名】')
    browser.find_element_by_xpath(
        "//body/div[@id='app']/div[@id='loginActivity']/div[1]/div[2]/div[2]/div[1]/div[3]/form[1]/div[2]/div[1]/div[1]/input[1]").send_keys(
        "【密码】")
    browser.find_element_by_xpath(
        "//body/div[@id='app']/div[@id='loginActivity']/div[1]/div[2]/div[2]/div[1]/div[3]/form[1]/button[1]").click()
    print("等待页面加载……")
    # time.sleep(3)
    browser.find_element_by_xpath(
        "//body/div[@id='app']/div[2]/div[2]/div[1]/div[1]/div[2]/div[1]/span[2]/i[1]").click()
    browser.find_element_by_xpath("//body/div[starts-with(@id,'wz-popover-')]/span/div[2]/div/span/i").click()
    browser.find_element_by_xpath("//div[contains(text(),'导出为excel')]").click()
    print("等待文件下载")
    # 校验文件下载是否完成
    flag = 0
    count = 0
    recheck = 0
    while 1:
        # 确认文件是否下载成功
        for i in os.listdir(path):
            if 'xlsx' in i:
                b.quit()
                return "下载成功!"
        count += 1
        print("等待下载...")
        time.sleep(5)

        if count >= 3:
            if recheck > 2:
                print("下载过程中出现了未知错误，程序异常退出!")
                b.quit()
                sys.exit(1)
            else:
                print("等待下载超时，重试下载动作...")
                count = 0
                browser.refresh()
                browser.find_element_by_xpath(
                    "//body/div[@id='app']/div[2]/div[2]/div[1]/div[1]/div[2]/div[1]/span[2]/i[1]").click()
                browser.find_element_by_xpath(
                    "//body/div[starts-with(@id,'wz-popover-')]/span/div[2]/div/span/i").click()
                browser.find_element_by_xpath("//div[contains(text(),'导出为excel')]").click()
                recheck += 1


def remove_chinese(string):
    # pattern = re.compile(r'[\u4e00-\u9fa5]')
    pattern = re.compile(r'[\u4e00-\u9fa5]+-?[\u4e00-\u9fa5]+')
    return re.sub(pattern, "", string).rstrip()


def highlight(s, column):
    series = pd.Series(data=False, index=s.index)
    series[column] = s.loc[column] == '是'
    return ['background-color: #C7E0B4' if series.any() else '' for v in series]


def deal_excel(file):
    with warnings.catch_warnings(record=True):
        warnings.simplefilter('ignore', ResourceWarning)
        df = pd.read_excel(file, engine='xlrd')

    global df_all, done_count, done_percent
    # 获取总行数
    df_all = len(df)
    # 获取已完成的行数
    df_done = df.loc[(df['是否已完成'] == '是') | (df['是否已完成'] == '已完成')].copy()
    done_count = len(df_done)
    # 计算完成率
    done_percent = int(done_count / df_all * 100)
    df.fillna('', inplace=True)

    data = [df.columns.tolist()]
    in_list = df.values.tolist()
    for temp in in_list:
        data.append(temp)

    # print(data)
    return data


def html_format(table_html):
    html_string = '''
    <html>
      <head><title>HTML Pandas Dataframe with CSS</title></head>
        <style type="text/css">
            #main {{border-collapse: collapse;word-break: keep-all;white-space: nowrap;font-size: 13px;font-family: "Microsoft Yahei UI";text-align:center;}}
            #main th {{padding: 5px;background-color: #92D050;font-size: 16px;text-align:center}}
            #main tr {{font-size: 13px;}}
            #main td {{border-color: #000;border-style: solid;padding: 3px;white-space:nowrap;}}
            p {{font-size:14.5px;font-family: "Microsoft Yahei UI"}}
            span {{color:red;font-size:18px;font-family: "Microsoft Yahei UI";font-weight: bold}}
        </style>
      <body>
        <p>各位好，</p>
        <p>运维组2023年K8S迁移计划当前完成进度为：<span>{done_percent} %</span></p>
        <p>总共需容器化系统数量为：{df_all}</p>
        <p>目前已完成的系统数量为：{done_count}</p>
        <p>如果有系统进度更新，请系统负责人自行到<a href='http://xxx.com.cn/#/post/46679187'>文档</a>内进行更新，邮件每次发送前会自动拉取文档最新数据</p>
        <br/>
        <p>以下为需容器化的系统进度详单：</p>
        {main}
        <br/>
      </body>
    </html>
    '''

    html = html_string.format(df_all=df_all, done_count=done_count, done_percent=done_percent,
                              main=table_html)
    # print(html)
    html = html.replace('\"', '\'')
    html = html.replace('\n', '')
    return html


def list_to_html_table(in_list):
    # pandas输出的list转HTML，转换格式主要用于邮件发送
    table = HTMLTable(caption="")
    title = in_list[0]
    # print(temp)
    table.append_header_rows((
        title, ()
    ))

    content = in_list[1:]
    table.append_data_rows(content)

    # 表格样式，即<table>标签样式
    table.set_style({
        'border-collapse': 'collapse',
        'word-break': 'keep-all',
        'white-space': 'nowrap',
        'font-size': '13px',
        'font-family': 'Microsoft Yahei UI',
        'text-align': 'center',
    })

    # 表头样式
    table.set_header_row_style({
        'font-size': '16px',
        'background-color': '#92D050',
    })

    # 统一设置所有单元格样式，<td>或<th>
    table.set_cell_style({
        'border-color': '#000',
        'border-width': '1px',
        'border-style': 'solid',
        'padding': '3px',
        'white-space': 'nowrap',
    })

    # 覆盖表头单元格字体样式
    table.set_header_cell_style({
        'padding': '5px',
    })

    # 遍历数据行，满足特定条件，行标记特殊颜色
    for row in table.iter_data_rows():
        if str(row[6].value) != "" and str(row[4].value).find("是") == -1:
            row.set_style({
                'background-color': '#C7E0B4',
            })

    table_html = table.to_html()
    table_html = table_html.replace('\"', '\'')
    # print(html)
    return table_html


def now_time():
    time = datetime.datetime.now()
    return time


def month_start_date(today):
    year = str(today.year)
    month = str(today.month)
    day = "1"
    return strp_time(year + "-" + month + "-" + day)


def month_end_date(today):
    year = str(today.year)
    month = str(today.month + 1)
    if month == "13":
        month = "1"
        year = str(int(year) + 1)
    day = "1"
    return strp_time(year + "-" + month + "-" + day) - datetime.timedelta(days=1)


def strp_time(time_str, str_module="%Y-%m-%d"):
    time = datetime.datetime.strptime(time_str, str_module)
    return time


# 校验路径是否存在, 并清理目录
def path_check(path):
    print("正在检查路径： " + path)
    if os.path.exists(path):
        # 校验文件是否存在，如存在先进行删除
        get_file = os.listdir(path)
        if get_file == []:
            print('目录为空，无需清理')
        else:
            os.chdir(path)
            for i in get_file:
                try:
                    os.remove(i)
                    print("已清理：" + i)
                except PermissionError as reason:
                    print("文件无法被删除,请检查路径权限!")
                    sys.exit(1)
    else:
        print('目录不存在，新建目录')
        os.mkdir(path)


if __name__ == '__main__':
    # 校验下载目录是否已清空，否则影响文件读取
    # 下载地址
    path_download = '/nfsc/cnas_csp_cims_szc_id4465_vol1001_prd/mail/k8s/download/'
    path_attached = '/nfsc/cnas_csp_cims_szc_id4465_vol1001_prd/mail/k8s/attached/'
    # path_download = 'D:\\download\\'
    # path_attached = 'D:\\download\\'
    path_check(path_download)
    path_check(path_attached)
    # 模拟登录下载操作
    # url相关
    url_yj = 'http://xxx.com.cn/#/post/46679187'
    b = open_browser(path_download)
    # 执行任务
    control_browser(b, url_yj, path_download)

    # 获取文件名
    os.chdir(path_download)
    list_file = sorted(os.listdir(), key=os.path.getmtime)
    xlsx_name = list_file[-1]
    # print(xlsx_name)

    # 表格操作
    get_html = html_format(list_to_html_table(deal_excel(path_download + xlsx_name)))

    # 发送邮件
    mail_uuid = str(uuid.uuid1())
    send_to(deal_message_text(mail_uuid, get_html))
