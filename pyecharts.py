#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@File: pyecharts.py
@Time: 2022/01/20 10:00:00
@Author: zhangtyps
@Version: 1.0
@Desc: 通过pyecharts模块，根据数据库查到的数据，导出一个png格式的饼图和折线图，然后POST邮件接口，给业务发送邮件（其实直接发表格也行，但为了可视化，还是发图的好）
'''


# here put the import lib
import time, requests, sys, warnings, uuid, os, pymysql, datetime
import pandas as pd
from HTMLTable import HTMLTable
from pyecharts import options as opts
from pyecharts.charts import Pie
from pyecharts.charts import Line
from pyecharts.render import make_snapshot
from snapshot_selenium import snapshot
from pyecharts.globals import CurrentConfig


#该函数只要是为了拼接邮件接口的请求文本，本身并不重要，具体情况具体对待了~
def deal_message_text(mail_uuid, ccf_today, uuid1, uuid2, img_pie, img_line):
    data = '{"mailId": "' + mail_uuid + '",\
            "sender": "xxxx@system.com.cn",\
            "sysName": "ABC_SYSTEM",\
            "title": "邮件标题",\
            "recList": ["zhangtyps@vip.qq.com"],\
            "ccList": ["zhangtyps@vip.qq.com"], \
            "content": "<p style=\'font-size:14.5px;font-family:Microsoft Yahei UI\'>'+str(yesterday)+' 调用总量： ' + ccf_today + '<br/><br/><img src=\'cid:' + uuid1 + '\'/><br/><img src=\'cid:' + uuid2 + '\'/><br/>此邮件为自动发送，如对此邮件有任何问题，请联系zhangtyps", \
            "flagPic": true, \
            "picList":{ \
                    "' + uuid1 + '": "' + img_pie.replace('nas1', 'data') + '", \
                    "' + uuid2 + '": "' + img_line.replace('nas2', 'data') + '" \
                      }, \
            "flagAttached": false}'
    print(data)
    return data

#利用requests请求邮件接口
def send_to(call_data):
    url = 'http://email.com.cn/mail/api/send/singleMailReq'
    data = call_data
    headers = {
        'Content-Type': 'application/json'
    }
    data = str(data).encode('utf-8')
    response = requests.request("POST", url, headers=headers, data=data)
    print(response.text)

#xlsx表格处理，本质上这个代码没用到，我懒得删除了
def deal_excel(file):
    with warnings.catch_warnings(record=True):
        warnings.simplefilter('ignore', FutureWarning)
        df = pd.read_excel(file, engine='xlrd')  # ,header=None
    # 将非空数据转换为""
    df = df.where(df.notnull(), "")
    # 日期处理
    for i in df["完成时间"]:
        if type(i) == int or type(i) == float:
            row_num = df[df["完成时间"].isin([i])].index.values[0]
            i = pd.to_datetime((i - 25569) * 86400, unit='s')
            df.loc[row_num, "完成时间"] = i.date()
    # dataframe转list
    data = []
    data.append(df.columns.tolist())
    in_list = df.values.tolist()
    for temp in in_list:
        data.append(temp)
    print(data)
    return data

#此函数用于将list列表转换成html格式的表格，这个模块很酷，可以直接将list格式的表格（list长度一致，一行list代表表格里的一行）转换成html格式，用于邮件接口的能够展示表格    
#本质上这个函数这个脚本也没用到，也是我懒得删
def list_to_html_table(in_list):
    table = HTMLTable(caption="表格的标题")
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
    })
    # 表头样式
    table.set_header_row_style({
        'font-size': '13px',
    })
    # 统一设置所有单元格样式，<td>或<th>
    table.set_cell_style({
        'border-color': '#000',
        'border-width': '1px',
        'border-style': 'solid',
        'padding': '3px',
    })
    # 覆盖表头单元格字体样式
    table.set_header_cell_style({
        'padding': '5px',
    })
    # 遍历数据行，满足特定条件，行标记特殊颜色
    for row in table.iter_data_rows():
        if str(row[4].value) != "" and str(row[4].value).find("预计") == -1:
            row.set_style({
                'background-color': '#ccffcc',
            })
    html = table.to_html()
    html = html.replace('\"', '\'')
    # print(html)
    return html


def connect_mysql():
    db = pymysql.connect(database='', user='', password='', host='', port=3306)
    print("连接MYSQL库成功!")
    return db


def select_db(db, sql):
    cursor = db.cursor()
    cursor.execute(sql)
    re = cursor.fetchall()
    cursor.close()
    return re


def handle_mysql(db, sql):
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        db.commit()
    except pymysql.err.IntegrityError:
        db.rollback()
        print('sql执行异常: ' + sql)
    else:
        print("sql执行成功！")
    cursor.close()


def close_db(db):
    db.close()
    print('关闭数据库连接：' + str(db))

#pyecharts重点代码，根据数据绘制饼图
def draw_pie(data, img_path, title):
    c = (
        Pie()
            .add("", data, radius=["40%", "55%"])
            .set_global_opts(title_opts=opts.TitleOpts(title=title),
                             legend_opts=opts.LegendOpts(orient="vertical", pos_top="15%", pos_left="2%"))
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}:  {c}"))
        # .render(img_path+"pie_base.html")
    )
    # make_snapshot(snapshot,file_name="D:\\pie_base.html",output_name="D:\\1.png",is_remove_html=True)
    make_snapshot(snapshot, c.render(), output_name=img_path, pixel_ratio=1, is_remove_html=True)

#pyecharts重点代码，根据数据绘制折线图
def draw_line(a, b, img_path, title):
    c = (
        Line()
            .add_xaxis(a[-7:])
            .add_yaxis("每日调用量", b[-7:],
                       markline_opts=opts.MarkLineOpts(data=[opts.MarkLineItem(type_="average")], precision=0),
                       is_connect_nones=True, linestyle_opts=opts.LineStyleOpts(width=2))
            # .add_yaxis("上周同期",b[:7],markline_opts=opts.MarkLineOpts(data=[opts.MarkLineItem(type_="average")],precision=0),is_connect_nones=True,linestyle_opts=opts.LineStyleOpts(width=0.5))
            .set_global_opts(title_opts=opts.TitleOpts(title=title))
        # .render(img_path+"line_markline.html")
    )
    make_snapshot(snapshot, c.render(), output_name=img_path, pixel_ratio=1, is_remove_html=True)

#用于在nas上检查目录是否存在，因为邮件想要发送图片，需要将图片上传到NAS上
def os_control(path):
    if not os.path.exists(path):
        print("目录不存在，创建目录:\n" + path)
        os.makedirs(path)
    else:
        print(path)

#清理历史NAS目录
def clean_history_path(delete=3, save=3, path='/nfsc/nas1_prd/mail/ccf/'):
    print("清理历史目录，当前参数：保留天数 = " + str(save) + ", 删除天数 = " + str(delete))
    today_date = datetime.datetime.today().date()
    delete_start_date = today_date - datetime.timedelta(delete + save)
    save_date = today_date - datetime.timedelta(save)
    while delete_start_date < save_date:
        path_2 = os.path.join(path + str(delete_start_date))
        if os.path.exists(path_2):
            print("删除：" + path_2)
            os.system('rm -rf ' + path_2)
        else:
            print("不存在目录：" + path_2)
        delete_start_date += datetime.timedelta(1)


if __name__ == '__main__':
    # 获取昨天日期
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    # yesterday = datetime.datetime.strptime('2022-01-26', "%Y-%m-%d").date()

    # 获取昨日CCF总量和各系统调用量
    mysql = connect_mysql()
    res = select_db(mysql, 'select date,ccf_final from dap_ccf_log where date="' + str(yesterday) + '"')
    # res=((datetime.date(2022, 1, 24), 81301),)

    print("查询昨天总调用量为：%s " % str(res))
    ccf_yes = str(res[0][1])

    # 获取昨日各系统调用量
    res_sys = select_db(mysql, 'select system_name,ccf_final from sys_ccf_details where date="' + str(yesterday) + '"')
    # res_sys=(('PAEGISECIF001', 41854), ('PAEGISPOS001', 6724), ('PAEGISCSPI001', 996), ('PAEGISCLAIM001', 82), ('PAEGISISP001', 3))
   
    # 获取前7天的总调用量
    res_14days = select_db(mysql,
                           'select date,ccf_final from dap_ccf_log where date>DATE_FORMAT(SYSDATE()-INTERVAL 15 DAY, "%Y-%m-%d") order by date')
    # res_14days=((datetime.date(2022, 1, 12), 71949), (datetime.date(2022, 1, 13), 59607), (datetime.date(2022, 1, 15), 0), (datetime.date(2022, 1, 16), 85621), (datetime.date(2022, 1, 17), 62047), (datetime.date(2022, 1, 18), 71031), (datetime.date(2022, 1, 19), 56292), (datetime.date(2022, 1, 20), 62781), (datetime.date(2022, 1, 21), 59449), (datetime.date(2022, 1, 22), 25730), (datetime.date(2022, 1, 23), 19803), (datetime.date(2022, 1, 24), 81301), (datetime.date(2022, 1, 25), 53739), (datetime.date(2022, 1, 26), 11221))
    res_14days = list(res_14days)
    close_db(mysql)
   
    # 折线图数据预处理
    start_day = yesterday - datetime.timedelta(days=13)
    i = start_day
    days = []
    ccfs = []
    while i <= yesterday:
        days.append(i)
        for temp in res_14days:
            if i == temp[0]:
                ccfs.append(temp[1])
                break
            else:
                if temp == res_14days[-1]:
                    ccfs.append(None)
                    break
        i += datetime.timedelta(days=1)
    
    # 获取数据完成，先确认目录是否存在
    today_path = '/nfsc/nas1/mail/ccf/' + str(datetime.datetime.today().date()) + '/'
    mail_uuid = str(uuid.uuid1())
    mail_path = today_path + mail_uuid + '/'
    image_path = mail_path + 'pic/'
    os_control(image_path)
 
    # echarts.min.js文件的路径地址，这个js文件很重要，在没有外网的地址，需要事先将js文件放到服务器上（这个文件用于pyecharts把网页转png图片用的）
    CurrentConfig.ONLINE_HOST = '/opt/'
 
    # 绘制饼图
    pie_uuid = str(uuid.uuid1())
    img_pie = image_path + pie_uuid + ".png"
    draw_pie(res_sys, img_pie, title="调用量来源")
  
    # 绘制折线图
    line_uuid = str(uuid.uuid1())
    img_line = image_path + line_uuid + ".png"
    draw_line(days, ccfs, img_line, title="近七天调用量走势")
    # output_list = deal_excel(path+'weblogic12灾备升级跟踪.xlsx')
    # html = list_to_html_table(output_list)
 
    # 发送邮件
    print("发送邮件")
    send_to(deal_message_text(mail_uuid, ccf_yes, pie_uuid, line_uuid, img_pie, img_line))
 
    # 清理历史目录
    clean_history_path()
