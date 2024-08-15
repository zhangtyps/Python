#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@File: emergency_drill.py
@CreateTime: 2022/5/6 11:18
@Author: zhangtyps
@Version: 3.1
@Desc:
通过selenium模拟页面操作，下载指定页面上的表格，用pandas打开表格，筛选处理表格，并生成一份新表格。
同时用pandas的df.to_html功能，直接将表格转成html格式，用于邮件发送。
表格的样式由html预定义。
本质功能：将本月需要做应急演练的系统筛选出来，并发送邮件给收件人处理
'''

# here put the import lib
import time, requests, warnings, datetime, uuid, os, re, sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
from decimal import Decimal


def deal_message_text(mail_uuid, year, month, html):
    data = '{"mailId": "' + mail_uuid + '",\
            "sender": "",\
            "sysName": "应急演练小助手",\
            "title": "' + year + '年' + month + '月应急演练",\
            "recList": [""],\
            "ccList": [""], \
            "content": "' + html + '", \
            "flagPic": false, \
            "flagAttached": true, \
            "attachedFile":{"本月应急演练一览_' + datetime.datetime.now().strftime(
        '%y%m%d') + '.xlsx":"/nfsc/data/mail/yingji/attached/temp.xlsx"}}'
    print(data)
    return data


def send_to(call_data):
    # 这里的url是邮箱接口地址。如无封装好的邮件接口，可使用其他方式发送邮件（如自建邮件服务器等，通过调用Linux命令发送邮件等）
    url = 'http://mail/api/send/singleMailReq'
    data = call_data
    headers = {
        'Content-Type': 'application/json'
    }
    data = str(data).encode('utf-8')

    response = requests.request("POST", url, headers=headers, data=data)
    print(response.text)


def send_to_pingan_robot(call_data):
    # 此url为聊天IM软件的群通知机器人地址
    url = 'https://peimc-proxy/openplatform/robotSendMessage?robotId=e22a468665fe460daa3ee9680d3247e3&groupId=11200000044772685'
    data = call_data
    headers = {
        'Content-Type': 'application/json',
        'Cookie': 'f5monweb=2366115870.10275.0000'
    }
    data = str(data).encode('utf-8')
    response = requests.request("POST", url, headers=headers, data=data)
    print(response.text)


def open_browser(download_path):
    ops = Options()
    # Linux环境参数
    if check_platform() == 'linux':
        ops.add_argument('--headless')  # 设置无界面
        ops.add_argument('--no-sandbox')  # root用户下运行代码需添加这一行
        ops.add_argument('--disable-dev-shm-usage')  # 使用/tmp而非/dev/shm
        ops.add_argument('--disable-gpu')  # 禁用gpu加速，规避bug
    ops.add_experimental_option('excludeSwitches', ['enable-automation'])  # 禁止输出日志（存疑）
    # ops.add_experimental_option('excludeSwitches', ['enable-logging'])
    ops.add_experimental_option('prefs', {'download.default_directory': download_path})
    # ops.add_argument(
    #     'user-agent="MQQBrowser/26 Mozilla/5.0 (Linux; U; Android 2.3.7; zh-cn; MB200 Build/GRJ22; CyanogenMod-7) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1"')

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
    # 基础配置
    driver.delete_all_cookies()  # 清除浏览器cookie
    driver.set_page_load_timeout(20)  # 页面加载超时时间
    driver.implicitly_wait(10)  # 隐式等待
    return driver


def control_browser(browser, url_address, um_user, um_pwd):
    # 判断页面是否使用了令牌（对于页面需要用到令牌验证，此段代码用于获取随机令牌登录网页）
    global otp
    browser.get(url_address)
    try:
        browser.find_element_by_xpath("//*[@id='normal_login_validCode']")
    except NoSuchElementException:
        is_otp = False
    else:
        is_otp = True
    # ----------------------------------------------
    if is_otp:
        print(">>>登录网页令牌页面……")
        browser.get("https://otp/newLogin")
        time.sleep(3)
        print(">>>执行登陆操作")
        browser.find_element_by_xpath("//*[@id='pane-ad']/form/div[1]/div/div/input").send_keys(um_user)
        browser.find_element_by_xpath("//*[@id='pane-ad']/form/div[2]/div/div/input").send_keys(um_pwd)
        browser.find_element_by_xpath("//*[@id='pane-ad']/form/div[4]/div/button").click()
        time.sleep(3)

        print(">>>切换到网页令牌")
        browser.find_element_by_xpath("//*[@id='tab-webPageToken']").click()
        browser.find_element_by_xpath("//*[@id='elFormItem']/div/div/input").send_keys(um_pwd)
        browser.find_element_by_xpath("//*[@id='elForm']/button[1]").click()
        # 强制刷新一次，以防获取到的令牌即将过期
        browser.find_element_by_xpath("//*[@id='pane-webPageToken']/div/div[6]/div/div[2]/div/div[2]/div[7]").click()
        print(">>>获取动态令牌口令")
        time.sleep(3)
        otp = ""
        for i in range(1, 7):
            num_xpath = "//*[@id='pane-webPageToken']/div/div[6]/div/div[2]/div[2]/div[2]/div[" + str(i) + "]"
            otp += browser.find_element_by_xpath(num_xpath).text
        print(otp)
    # ----------------------------------------------

    print("正在打开应急演练页面……")
    browser.get(url_address)
    time.sleep(3)
    print("执行登陆操作")
    browser.find_element_by_xpath("//*[@id='normal_login_user']").send_keys(um_user)
    browser.find_element_by_xpath("//*[@id='normal_login_password']").send_keys(um_pwd)
    if is_otp:
        browser.find_element_by_xpath("//*[@id='normal_login_validCode']").send_keys(otp)
        browser.find_element_by_xpath(
            "//*[@id='root1']/div/div/div[3]/div/div/form/div[3]/div/div/span/button").click()
    else:
        browser.find_element_by_xpath(
            "//*[@id='root1']/div/div/div[3]/div/div/form/div[1]/div[3]/div[1]/div[4]/div/div/span/button").click()
    time.sleep(3)
    print("切到应急演练页面")
    browser.get('http://xxxx.com.cn/workstation/constancyManager/emergencyRehearsal/myRehearsalPlan/List')
    browser.find_element_by_xpath("//div[contains(text(),'所有演练计划')]").click()

    browser.find_element_by_xpath(
        "//*[@id='root1']/section/section/main/div/div[3]/div[2]/div[2]/div/div/div[2]/div/div[1]/div/div/div/button[3]").click()
    time.sleep(5)

    # # 操作时间窗体
    # browser.find_element_by_xpath(
    #     "//body/div[@id='app']/div[2]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/form[1]/div[4]/div[1]/div[1]/input[1]").send_keys(
    #     day_start)
    # browser.find_element_by_xpath(
    #     "//body/div[@id='app']/div[2]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/form[1]/div[4]/div[1]/div[1]/input[2]").send_keys(
    #     day_end)
    # # 隐藏时间窗体
    # browser.execute_script(
    #     'document.getElementsByClassName("el-picker-panel el-date-range-picker el-popper")[0].style="display: None;"')

    # 操作演练组
    # browser.find_element_by_xpath(
    #     "//body/div[@id='app']/div[2]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/form[1]/div[1]/div[1]/div[1]/div[1]/input[1]").send_keys(
    #     "xxx")
    # browser.find_element_by_xpath("//span[contains(text(),'xxx总部应用运营组')]").click()

    # # 点击查询
    # browser.find_element_by_xpath(
    #     "//body[1]/div[1]/div[2]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/form[1]/div[8]/div[1]/div[1]/div[1]/button[1]/span[1]").click()
    #
    # # 导出演练文件
    # browser.find_element_by_xpath(
    #     "//body/div[@id='app']/div[2]/div[2]/div[1]/div[2]/div[1]/div[2]/button[5]/span[1]/i[1]").click()


def remove_chinese(string):
    # pattern = re.compile(r'[\u4e00-\u9fa5]')
    pattern = re.compile(r'[\u4e00-\u9fa5]+-?[\u4e00-\u9fa5]+')
    return re.sub(pattern, "", string).rstrip().split(" ")[0]


def deal_excel(file, s_date, e_date, path):
    with warnings.catch_warnings(record=True):
        warnings.simplefilter('ignore', ResourceWarning)
        df = pd.read_excel(file, engine='xlrd')

    df['计划时间'] = pd.to_datetime(df['计划时间'])
    df = df[(df['计划时间'] >= s_date) & (df['计划时间'] <= e_date)]
    df_excel = df.loc[df['公司'] == '有限公司'].copy()
    # 生成待发送的xlsx文档到nas里
    df_excel.to_excel(path + 'temp.xlsx', index=False)
    # 获取本月应急演练总共数量
    all_num = len(df.loc[(df['公司'] == '有限公司') & (df['状态'] != '已取消')])
    print(all_num)

    df_ylx = df.loc[
        (df['公司'] == '有限公司') & (df['状态'] != '已完成') & (df['状态'] != '已取消')].copy()
    df_ylx = df_ylx.sort_values(by=['演练组', '责任人', '演练系统'])
    df_ylx_done = df.loc[(df['公司'] == '有限公司') & (df['状态'] == '已完成')].copy()
    df_ylx_done = df_ylx_done.sort_values(by='完成时间', ascending=False)
    # 获取已完成的数量
    done_num = len(df_ylx_done)
    print(done_num)
    # 计算本月应急演练完成率
    if all_num == 0:
        percent = "100"
    else:
        percent = Decimal(done_num / all_num * 100).quantize(Decimal("0"))
        percent = str(percent)

    # 下面注释这种方法可以新建一个DF，保存特定的列，注意前后有两个中括号
    # df_ylx_select = df_ylx[['ID', '演练组', '演练系统', '演练名称', '计划时间', '状态', '责任人']]
    # 下面注释这种方法可以保存成一个Excel
    # df_ylx.to_excel('D:\\new_plan_2.xlsx')

    for i in df_ylx.index:
        str1 = df_ylx.loc[i, '演练系统']
        df_ylx.loc[i, '演练系统'] = remove_chinese(str1)

    for i in df_ylx_done.index:
        str1 = df_ylx_done.loc[i, '演练系统']
        df_ylx_done.loc[i, '演练系统'] = remove_chinese(str1)

    # print(df_ylx.empty) 判断是否为空表格
    # print(df_ylx_done.empty)
    #
    # # print(df_ylx.index)
    # # print(df_ylx.loc[88,'演练系统'])
    # # df_ylx.to_excel('D:\\new_plan_5.xlsx')
    #
    # print(df_ylx)

    html_string = '''
    <html>
      <head><title>HTML Pandas Dataframe with CSS</title></head>
        <style type="text/css">
            #main {{border-collapse: collapse;word-break: keep-all;white-space: nowrap;font-size: 13px;font-family: "Microsoft Yahei UI";}}
            #main th {{padding: 5px;background-color: #f6b26b;font-size: 16px;text-align:center;}}
            #main tr {{font-size: 13px;}}
            #main td {{border-color: #000;border-style: solid;padding: 3px;white-space:nowrap;}}
            #done {{border-collapse: collapse;word-break: keep-all;white-space: nowrap;font-size: 13px;font-family: "Microsoft Yahei UI";}}
            #done th {{padding: 5px;background-color: #4EEE94;font-size: 16px;text-align:center;}}
            #done tr {{font-size: 13px;}}
            #done td {{border-color: #000;border-style: solid;padding: 3px;white-space:nowrap;}}
            p {{font-size:14.5px;font-family: "Microsoft Yahei UI"}}
            span {{color:red;font-size:18px;font-family: "Microsoft Yahei UI";font-weight: bold}}
        </style>
      <body>
        <p>各位好，</p>
        <p>本月应急演练当前完成率为：<span>{percent} %<span/></p>
        <br/>
        <p>本月应急演练未完成系统的如下：</p>
        {main}
        <br/>
        <p>已完成系统：</p>
        {done}
        <br/>
      </body>
    </html>
    '''

    html_string_none = '''
        <html>
      <head><title>HTML Pandas Dataframe with CSS</title></head>
        <style type="text/css">
            p {{font-size:14.5px;font-family: "Microsoft Yahei UI"}}
            span {{color:red;font-size:18px;font-family: "Microsoft Yahei UI";font-weight: bold}}
        </style>
      <body>
        <p>各位好，</p>
        <p>本月暂无应急演练，请知晓。</p>
        <br/>
      </body>
    </html>
    '''

    if all_num == 0:
        html = html_string_none
    else:
        if df_ylx.empty and not df_ylx_done.empty:
            html = html_string.format(
                percent=percent,
                main="<p>无</p>",
                done=df_ylx_done.to_html(index=False,
                                         columns=['ID', '演练组', '演练系统', '演练名称', '完成时间', '状态', '责任人', '是否真实演练'],
                                         table_id='done'))
        elif df_ylx_done.empty and not df_ylx.empty:
            html = html_string.format(
                percent=percent,
                main=df_ylx.to_html(index=False, columns=['ID', '演练组', '演练系统', '演练名称', '计划时间', '状态', '责任人', '是否真实演练'],
                                    table_id='main'),
                done="<p>无</p>")
        elif df_ylx_done.empty and df_ylx.empty:
            html = html_string.format(
                percent=percent,
                main="<p>无</p>",
                done="<p>无</p>")
        else:
            html = html_string.format(
                percent=percent,
                main=df_ylx.to_html(index=False, columns=['ID', '演练组', '演练系统', '演练名称', '计划时间', '状态', '责任人', '是否真实演练'],
                                    table_id='main'),
                done=df_ylx_done.to_html(index=False,
                                         columns=['ID', '演练组', '演练系统', '演练名称', '完成时间', '状态', '责任人', '是否真实演练'],
                                         table_id='done'))

    html = str(html).replace('\"', '\'')
    html = html.replace('\n', '')
    return html


# 此段代码仅备份，用于风险整改平台使用，不单独弄一个py文件了
def deal_excel2(file, path):
    with warnings.catch_warnings(record=True):
        warnings.simplefilter('ignore', ResourceWarning)
        df = pd.read_csv(file)

    df = df.loc[(df['所属领域'] == '中间件')]
    df['下发时间'] = pd.to_datetime(df['下发时间'])
    df['考核时间'] = df.apply(lambda x: x['下发时间'] + pd.DateOffset(days=30), axis=1)
    # df['考核时间'] = df.apply(lambda x: x['下发时间'] + pd.DateOffset(months=1), axis=1)
    df = df.sort_values(by='下发时间')
    df.fillna('', inplace=True)
    df_not_ok = df.loc[(df['关联风险ID'].str.contains('未处理', na=False)) & (df['无效整改'] == '无效整改')]
    df_not_done = df.loc[(df['状态'] != '已完成')]
    # 生成待发送的xlsx文档到nas里
    df.to_excel(path + 'temp.xlsx', index=False)

    html_string_base = '''
    <html>
          <head><title>风险平台</title></head>
            <style type="text/css">
                #table1 {{border-collapse: collapse;word-break: keep-all;white-space: nowrap;font-size: 13px;font-family: "Microsoft Yahei UI";}}
                #table1 th {{padding: 5px;background-color: #f2948f;font-size: 16px;text-align:center;}}
                #table1 tr {{font-size: 13px;}}
                #table1 td {{border-color: #000;border-style: solid;padding: 3px;white-space:nowrap;}}
                #table2 {{border-collapse: collapse;word-break: keep-all;white-space: nowrap;font-size: 13px;font-family: "Microsoft Yahei UI";}}
                #table2 th {{padding: 5px;background-color: #B2DFEE;font-size: 16px;text-align:center;}}
                #table2 tr {{font-size: 13px;}}
                #table2 td {{border-color: #000;border-style: solid;padding: 3px;white-space:nowrap;}}
                p {{font-size:14.5px;font-family: "Microsoft Yahei UI"}}
                span {{color:red;font-size:15px;font-family: "Microsoft Yahei UI";font-weight: bold}}
                li {{font-size:14.5px;font-family: "Microsoft Yahei UI"}}
                p1 {{font-size:7.5px;font-family: "Microsoft Yahei UI"}}
            </style>
          <body>
            <p>各位好，</p>
            <p>检测到当前<b>中间件</b>风险问题如下，请整改负责人在<span>考核时间</span>截止前尽快完成风险整改处理！点击这里跳转到→<a href='http://rmcp/'>集团运营风控平台</a></p>
            <p>请务必注意<b>风险接受</b>和<b>风险规避</b>的区别：</p>
            <ul>
            <li>风险接受：即对风险进行豁免签报，也就是实际未进行整改，风险仍然存在。</li>
            <li>风险规避：即完成了风险的整改。如果风险规避后仍然被平台识别为未完成整改，原风险会被标记为<b>无效整改</b>并生成新的风险ID。</li>
            </ul>
    '''
    html_string_normal = '''
            <p>待处理风险项如下：</p>
            {table2}
            <br/>
            <p1>PS：本邮件还在测试阶段，如果哪一天没发邮件也很正常，写BUG是程序员的基本素养</p1>
            <br/>
          </body>
        </html>
        '''

    html_string_not_ok = '''
        <p>无效整改项如下：（无效整改请查看<b>关联风险ID</b>列的风险ID继续处理）</p>
        {table1}
        <br/>
        <p>待处理风险项如下：</p>
        {table2}
        <br/>
        <p1>PS：本邮件还在测试阶段，如果哪一天没发邮件也很正常，写BUG是程序员的基本素养</p1>
        <br/>
      </body>
    </html>
    '''

    html_string_normal = html_string_base + html_string_normal
    html_string_not_ok = html_string_base + html_string_not_ok

    if df_not_ok.empty and not df_not_done.empty:
        # 有风险项，但没有无效整改
        html = html_string_normal.format(
            table2=df_not_done.to_html(index=False,
                                       columns=['风险ID', '风险子类', '风险点', '对象', '所属子系统', '整改责任人', '下发时间', '考核时间', '状态'],
                                       table_id='table2'))
    elif df_not_done.empty and not df_not_ok.empty:
        # 没有风险项，但是有未完成的无效整改（草真的有这种情况么?）
        html = html_string_not_ok.format(
            table1=df_not_ok.to_html(index=False,
                                     columns=['风险ID', '风险子类', '风险点', '对象', '所属子系统', '整改责任人', '下发时间', '考核时间', '状态',
                                              '风险控制策略',
                                              '无效整改',
                                              '关联风险ID'],
                                     table_id='table1'),
            table2=None)
    elif df_not_done.empty and df_not_ok.empty:
        # 没有风险项，没有无效整改
        # 不发送邮件，程序直接结束
        send_to_pingan_robot(call_data={"textContent": "当前没有中间件HA风险项目。"})
        sys.exit(0)
    else:
        html = html_string_not_ok.format(
            table1=df_not_ok.to_html(index=False,
                                     columns=['风险ID', '风险子类', '风险点', '对象', '所属子系统', '整改责任人', '下发时间', '考核时间', '状态',
                                              '风险控制策略',
                                              '无效整改',
                                              '关联风险ID'],
                                     table_id='table1'),
            table2=df_not_done.to_html(index=False,
                                       columns=['风险ID', '风险子类', '风险点', '对象', '所属子系统', '整改责任人', '下发时间', '考核时间', '状态'],
                                       table_id='table2'))

    # print(html)

    html = str(html).replace('\"', '\'')
    html = html.replace('\n', '')
    return html


# 未启用功能：用于提前全部完成后，不再发送提醒
# def resume_flag(flag_path):
#     # 重置标识位
#     pass
#
#
# def check_flag(flag_path='/nfsc/cnas_csp_cims_szc_id4465_vol1001_prd/mail/yingji/flag.txt'):
#     # 寻找标识文件
#     if os.path.exists(flag_path):
#         pass
#     else:
#         print("未找到标识文件，本月应急演练未完成！")
#         sys.exit(0)


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
                os.remove(i)
                print("已清理：" + i)
    else:
        print('目录不存在，新建目录')
        os.mkdir(path)


# 判断平台类型
def check_platform():
    if sys.platform.startswith('win'):
        return 'win'
    elif sys.platform.startswith('linux'):
        return 'linux'
    else:
        print('无法识别当前操作系统')
        sys.exit(1)


if __name__ == '__main__':
    # 脚本是否自动下载excel（人肉模式）
    download_excel = True
    # 页面登陆的UM配置
    user = ""
    pwd = ""
    # 下载地址
    if check_platform() == 'linux':
        path_download = '/nfsc/cnas_csp_cims_szc_id4465_vol1001_prd/mail/yingji/download/'
        path_attached = '/nfsc/cnas_csp_cims_szc_id4465_vol1001_prd/mail/yingji/attached/'
    else:
        path_download = 'D:\\py_down\\download\\'
        path_attached = 'D:\\py_down\\attached\\'

    # 测试代码
    # time_str = "2023-11-01 11:11:11"
    # today = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")

    today = now_time()
    start_date = month_start_date(today)
    end_date = month_end_date(today)
    month = today.month
    year = today.year
    print("时间范围为：" + str(start_date) + " ~ " + str(end_date))

    if download_excel:
        # 校验下载目录是否已清空，否则影响文件读取
        path_check(path_download)
        path_check(path_attached)
        # 模拟登录下载操作
        # url相关
        url = 'http://xxxopx.com.cn/home'
        b = open_browser(path_download)
        # 执行任务
        try:
            control_browser(b, url, user, pwd)
        except:
            send_to_pingan_robot(call_data={"textContent": "【应急演练】浏览器模拟操作失败，请检查平台前端元素是否有改动。"})
            b.quit()
            sys.exit(1)

        # 校验文件下载是否完成
        flag = 0
        count = 1
        while 1:
            # 第一轮检测
            for i in os.listdir(path_download):
                if 'xlsx' in i:
                    print("下载成功")
                    flag = 1
            if flag == 1:
                break
            else:
                if count >= 5:
                    print("下载等待超时,还请重新执行脚本")
                    b.quit()
                    sys.exit(1)
                count += 1
                print("等待下载...")
                time.sleep(8)
        print("关闭浏览器")
        b.quit()

    # 获取文件名
    os.chdir(path_download)
    list_file = sorted(os.listdir(), key=os.path.getmtime)
    xlsx_name = list_file[-1]
    # print(xlsx_name)

    # 表格操作
    get_html = deal_excel(path_download + xlsx_name, start_date, end_date, path_attached)

    # 发送邮件
    mail_uuid = str(uuid.uuid1())
    send_to(deal_message_text(mail_uuid, str(year), str(month), get_html))