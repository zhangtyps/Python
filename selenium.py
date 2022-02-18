#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@File: selenium_switch-open-or-off.py
@Time: 2021/8/31 16:13:00
@Author: 
@Version: 1.0
@Desc: 通过selenium结合chrome-linux，能够在linux上做到打开网页并点击网页相关按钮，实现一些配置项调整操作
'''
# here put the import lib
import time,requests,sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException


def deal_message_text(text_content, at_members):
    data = {
        "textContent": text_content,
        "atMembers": at_members,
    }
    return data


def send_to_pingan_robot(call_data):
    url = 'https://www.baidu.com/openplatform/robotSendMessage?robotId=e22a468665fe460daa3ee9680d3247e3&groupId=11200000044772685'
    data = call_data
    headers = {
        'Content-Type': 'application/json',
        'Cookie': 'f5monweb=2366115870.10275.0000'
    }
    data = str(data).encode('utf-8')
    response = requests.request("POST", url, headers=headers, data=data)
    print(response.text)

#通过selenium启动一个浏览器
def open_browser():
    ops = Options()
    # Linux环境参数
    # ops.add_argument('--headless')  # 设置无界面
    # ops.add_argument('--no-sandbox')  # root用户下运行代码需添加这一行
    # # ops.add_argument('--disable-dev-shm-usage') #使用/tmp而非/dev/shm
    # ops.add_argument('--disable-gpu')  # 禁用gpu加速，规避bug
    ops.add_experimental_option('excludeSwitches', ['enable-automation'])
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
    # 集体配置
    driver.delete_all_cookies()  # 清除浏览器cookie
    driver.set_page_load_timeout(10)
    driver.implicitly_wait(5)  # 隐式等待
    return driver


def sys_ann(browser,url,switch):
    key_name = ["key1", "key2"]
    change = False
    print("正在打开SYS页面……")
    browser.get(url)
    time.sleep(3)
    print("切到配置管理页面")
    browser.find_element_by_xpath('//a[contains(text(),"配置管理")]').click()
    # 切换到iframe
    print("切到内置窗体，开始执行开关命令")
    browser.switch_to.frame("content")
    browser.find_element_by_xpath('//input[@name="configKeyNo"]').clear()
    browser.find_element_by_xpath('//input[@name="configKeyNo"]').send_keys("valiCustomerLegal")
    browser.find_element_by_id("btnSearch").click()
    for key in key_name:
        browser.find_element_by_xpath('//input[@name="configKeyNo"]').clear()
        browser.find_element_by_xpath('//input[@name="configKeyNo"]').send_keys(key)
        browser.find_element_by_id("btnSearch").click()
        time.sleep(1)
        if browser.find_element_by_xpath('//input[@id="configKey1"]').get_attribute("value")==key:
            if browser.find_element_by_id("configValue1").get_attribute("value")==switch:
                print("开关当前值与动作相同，无需调整")
            else:
                browser.find_element_by_id("configValue1").clear()
                browser.find_element_by_id("configValue1").send_keys(switch)
                time.sleep(1)
                browser.find_element_by_id("index").click()
                time.sleep(1)
                browser.find_element_by_xpath('//*[@id="batch_btn_div"]/input').click()
                print("提交" + key + ": " + switch)
                time.sleep(1)
                change=True
    if change:
        message = deal_message_text("SYS 开关: " + switch, ["zhangtyps"])
        send_to_pingan_robot(message)


def login_pacas(url):
    b = open_browser()
    print("启动浏览器成功")
    try:
        print("检测打开页面是否被反爬……")
        b.get(url)
    except TimeoutException:
        print("打开页面失败，信息如下：")
        print(b.page_source)
        b.quit()
        sys.exit(1)
    print("页面打开成功，即将开始登录")
    b.find_element_by_id("username").send_keys("username")
    b.find_element_by_id("password").send_keys("passwd")
    b.find_element_by_id("loginButton").click()
    print("登录成功!")
    return b


if __name__ == '__main__':
    # 脚本执行总开关，Y表示打开，N表示关闭
    action = 'Y'
    # url相关
    url_pacas = 'https://testcheck.com.cn'
    url_sys_1='http://sys_name.com.cn'

    # 执行任务
    b=login_pacas(url_pacas)
    sys_ann(b,url_sys_1,action)

    print("关闭浏览器")
    b.quit()
