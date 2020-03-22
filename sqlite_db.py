#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'一个招投标网站信息采集工具'
__author__ = 'Zhang Minghao'

def check(cursor,info):
    url_hash = md5(info[1])
    check_status = cursor.execute('SELECT * FROM history where URL_Hash=?', (url_hash,))
    if len(check_status.fetchall()) == 1:
        #检查数据库中存在已抓取过的记录
        return 1
        #检查数据库中不存在已抓取过的记录
    else:
        return 0
def add(cursor, info):
    cursor.execute('''
        insert into history ("URL_Hash","URL","Title","Date") values (?, ?, ?, ?)
        ''', (md5(info[1]), info[1], info[2], info[3]))
    return

def add_info(cursor, url_info):
    cursor.execute('''
        UPDATE history set Info=? where URL_Hash=?
        ''', (url_info[1], md5(url_info[0])))
    return

def md5(data):
    import hashlib
    hash_result = hashlib.md5()
    hash_result.update(str(data).encode('utf-8'))
    return hash_result.hexdigest()

#初始化数据库，建立表
def main(cursor):
    import logger
    logger.debug('初始化SQLite3数据库！')
    cursor.execute('''
        create table history (
            URL_Hash char(32) primary key,
            URL TEXT,
            Title TEXT,
            Date TEXT,
            [InsertTime] TimeStamp NOT NULL DEFAULT (datetime('now','localtime')),
            Info TEXT DEFAULT NULL
            )
        ''')
    return


if __name__=='__main__':
    import sqlite3, os
    try:
        os.remove('history.db')
    except:
        pass
    conn = sqlite3.connect('history.db')
    cursor = conn.cursor()
    main(cursor)
    