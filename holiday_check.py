#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File: holiday_check.py
@Time: 2021/6/28 16:13:00
@Author: zhangtyps
@Version: 2.0
@Desc: 通过chinese_calendar模块判断中国节假日信息，以及requests模块POST请求对应地址（比如企业微信群聊机器人的api地址），推送到点下班信息
'''

# here put the import lib
import chinese_calendar,requests,calendar,datetime,sys


def deal_message_text(extra_message=""):
    data = {
        "cardType":1,
        "title":"下班啦！",
        "cardTextContent":'>><span color = "#FF0000" href="http://www.baidu.com.cn/ts/#/manage/work">点击填写</span>'+extra_message,
        "tailName": "xxxx系统",
        "tailLocation": 1,
        "tailUrl": "http://www.baidu.com.cn/ts/#/manage/work"
    }
    return data


def send_to_pingan_robot(call_data):
    url = 'https://www.baidu.com.cn/openplatform/robotSendMessage?robotId=123123&groupId=123123'
    data = call_data
    headers = {
        'Content-Type': 'application/json',
        'Cookie': 'f5monweb=2366115870.10275.0000'
    }
    data = str(data).encode('utf-8')
    response = requests.request("POST", url, headers=headers, data=data)
    print(response.text)


if __name__ == "__main__":
    now_date=datetime.datetime.now().date()
    next_date = now_date + datetime.timedelta(days=1)
    # 测试代码
    #time_str = "2021-07-24 11:11:11"
    #now_date = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    #next_date=now_date+datetime.timedelta(days=1)

    try:
        if chinese_calendar.is_holiday(now_date):
            print("非法定工作日，跳过提醒！")
            sys.exit(0)
        # 当今天不是节假日时：
        # 当今天是本月最后一天工作日，特殊提醒
        elif next_date.month != now_date.month:
            send_to_pingan_robot(deal_message_text('\n友情提示：今天为本月最后一个工作日，请务必准时上报，以免造成跨月填报！'))
        # 当今天为20号之后的日期，进行特殊判断（应该没有哪个节假日能从20号放到月底的吧）
        elif now_date.day > 20:
            # 判断后面的日子是否都为节假日
            # 获得本月总共多少天
            last_day_num = calendar.monthrange(now_date.year, now_date.month)[1]
            last_day = now_date + datetime.timedelta(days=last_day_num - now_date.day)
            # 获取明天的日期
            check_day = now_date + datetime.timedelta(days=1)
            # 当检测的日期大于这个月总天数时，跳出循环
            while check_day <= last_day:
                if chinese_calendar.is_holiday(check_day):
                    check_day += datetime.timedelta(days=1)
                else:
                    send_to_pingan_robot(deal_message_text())
                    sys.exit(0)
            send_to_pingan_robot(deal_message_text('\n友情提示：今天为本月最后一个工作日，请务必准时上报，以免造成跨月填报！'))
        else:
            # 以上条件均不满足，为普通工作日，无附加信息
            send_to_pingan_robot(deal_message_text())
    except NotImplementedError:
        if now_date.month==1 and now_date.day==1:
            print("元旦，跳过提醒！")
        else:
            day_of_week=now_date.isoweekday()
            if day_of_week!=6 and day_of_week!=7:
                send_to_pingan_robot(deal_message_text('\nchinese_calendar模块已过期，请及时升级~'))
            else:
                print("周末，可能为节假日，跳过告警！")