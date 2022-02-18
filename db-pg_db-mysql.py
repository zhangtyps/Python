#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File: db-pg_db-mysql.py
@Time: 2021/10/12 17:52:00
@Author: zhangtyps
@Version: 1.0
@Desc: 主要是psycopg2连接pg库和pymysql连接mysql库的代码
'''
# here put the import lib
import psycopg2,pymysql
import json


def connect_pg():
    #连接同城库，减少主库压力
    db = psycopg2.connect(database='', user='', password='', host='1.1.1.1', port=3306)
    print("连接my-system-PG库成功!")
    return db


def connect_mysql():
    db = pymysql.connect(database='', user='', password='', host='2.2.2.2', port=3306)
    print("连接MYSQL库成功!")
    return db


def select_db(db, sql):
    cursor = db.cursor()
    cursor.execute(sql)
    re = cursor.fetchall()
    cursor.close()
    return re


def handle_mysql(db,sql):
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        db.commit()
    except pymysql.err.IntegrityError:
        db.rollback()
        print('sql执行异常: '+sql)
    else:
        print("sql执行成功！" )
    cursor.close()


def close_db(db):
    db.close()
    print('关闭数据库连接：'+str(db))


def get_ccf_num_yesterday():
    db_pg = connect_pg()
    num_temp = select_db(db_pg, sql="SELECT COUNT FROM(SELECT (SELECT COALESCE (SUM(T .retry_times), 0) * 200 \
                                FROM my-system_push_data_task T WHERE T .transaction_code IN ( 'TCCCFBATCH002', 'TCCCFBATCHQUERY', '', '') \
                                AND T .task_created_time :: TIMESTAMP >= CURRENT_DATE-INTERVAL'1D' AND T .task_created_time :: \
                                TIMESTAMP < CURRENT_DATE) + (SELECT COUNT (1) * 200 FROM my-system_push_data_task T WHERE \
                                T .transaction_code IN ( 'TCCCFBATCH002', 'TCCCFBATCHQUERY', '', '' ) AND T .task_created_time :: TIMESTAMP\
                                 >= CURRENT_DATE-INTERVAL'1D' AND T .task_created_time :: TIMESTAMP < CURRENT_DATE AND T .retry_times = '0' )\
                                  + (SELECT COUNT (1) FROM PUBLIC .my-system_partner_a_request_log A WHERE A .transaction_code LIKE '%CCF%' AND A .request_time\
                                   :: TIMESTAMP >= CURRENT_DATE-INTERVAL'1D' AND A .request_time :: TIMESTAMP < CURRENT_DATE AND A .is_origin = 'Y' )\
                                    AS COUNT FROM PUBLIC .my-system_email_config GROUP BY COUNT ) A")
    close_db(db_pg)
    return num_temp


def get_ccf_list_yesterday():
    db_pg = connect_pg()
    list_temp = select_db(db_pg, sql="SELECT real_partner_id, COUNT(1) AS COUNT FROM my-system_partner_a_request_log WHERE transaction_code like 'TCCCFREALTIME01' \
                                AND request_time >= CURRENT_DATE - INTERVAL '1D' AND request_time < CURRENT_DATE AND is_origin = 'Y' \
                                GROUP BY real_partner_id ORDER BY COUNT DESC")
    close_db(db_pg)
    return list_temp


if __name__ == '__main__':
    ccf_limit_num = 150000
    # 查询昨日值
    ccf_num_y = get_ccf_num_yesterday()
    print("昨日值为："+str(ccf_num_y[0][0]))
    
    # 查询当前各个系统调用量，此sql输出是list格式，类似[('PAPSSANN001', 120970), ('PAEGISECIF001', 9811)]
    ccf_list_y = get_ccf_list_yesterday()
    ccf_list_y = json.dumps(dict(ccf_list_y))
    print("各系统调用清单："+str(ccf_list_y))

    #判断昨天是否有记录写入
    mysql_db=connect_mysql()
    date_yesterday=select_db(mysql_db,'SELECT * FROM my-system_ccf_log WHERE date=DATE_FORMAT(SYSDATE()-INTERVAL 1 DAY, "%Y-%m-%d")')
    if date_yesterday==tuple():
        print('不存在昨天的记录，执行插入数据操作')
        # 插入一行数据到表中
        db_mysql = connect_mysql()
        insert_sql = 'INSERT INTO my-system_ccf_log (date,ccf_all,ccf_final,final_details,updated_time) \
                      VALUES(DATE_FORMAT(SYSDATE()-INTERVAL 1 DAY, "%Y-%m-%d"),'+str(ccf_limit_num)+','+str(ccf_num_y[0][0])+',\''+ccf_list_y+'\',now())'
        print(insert_sql)
        handle_mysql(db_mysql, insert_sql)
        close_db(db_mysql)
    else:
        #更新数据
        print('执行更新数据操作')
        db_mysql= connect_mysql()
        update_sql = 'UPDATE my-system_ccf_log SET ccf_final='+str(ccf_num_y[0][0])+', final_details=\''+ccf_list_y+'\',updated_time=now() \
                      WHERE date = DATE_FORMAT(SYSDATE()-INTERVAL 1 DAY, "%Y-%m-%d")'
        print(update_sql)
        handle_mysql(db_mysql,update_sql)
        close_db(db_mysql)
