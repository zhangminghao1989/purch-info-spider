#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'一个招投标网站信息采集工具'
__author__ = 'Zhang Minghao'

#加载功能模块
import get_web
import config_load
import page_list_fun
import sqlite3
import sqlite_db
import csv
import os
import sys
import queue
import random
import re_filter
import logger

#设置获取最近n天的信息
date_limit = input('获取最近几天的信息？（默认为2天）：')
if date_limit == '':
    date_limit = 2
else:
    date_limit = int(date_limit)
logger.debug(f'获取最近 {date_limit} 天的信息。')
#是否跳过已抓取过的信息
check_history = str.lower(input('是否跳过已抓取过的信息？（Y/n）：'))
if check_history == 'n':
    check_history = 0
    logger.debug('不跳过已抓取过的信息。')
else:
    check_history = 1
    logger.debug('跳过已抓取过的信息。')
    logger.debug('默认写入数据库。')
#是否写入数据库
#正常情况默认写入数据库，当选择不跳过已抓取的信息或单独抓取时，可选择不写入数据库，方便调试
write_data = 'y'
if check_history == 0 or len(sys.argv) != 1:
    write_data = str.lower(input('是否写入数据库？（y/N）：'))
    if write_data != 'y':
        write_data = 'n'
        logger.debug('不写入数据库。')
    else:
        logger.debug('写入数据库。')


#读取配置文件
conf = config_load.load_conf()
encoding = conf.get('DEFAULT', 'encoding')
chrome_location = conf.get('DEFAULT', 'chrome_location')
firefox_location = conf.get('DEFAULT', 'firefox_location')
thread_number = int(conf.get('DEFAULT', 'thread_number'))
save_info_to_sql = conf.get('DEFAULT', 'save_info_to_sql')
if save_info_to_sql == 'False':
    save_info_to_sql = False
else:
    save_info_to_sql = True
website_data = config_load.load_website_data()
city = website_data.sections()

#配置webdriver，可在配置文件设置使用的webdriver
chosen_webdriver = conf.get('DEFAULT', 'webdriver')
from selenium import webdriver
if chosen_webdriver == 'Chrome':
    from selenium.webdriver.chrome.options import Options
    chrome_options = Options()
    #chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--log-level=3')
    chrome_options.binary_location = chrome_location
    chrome_options.add_argument('--blink-settings=imagesEnabled=false')

if chosen_webdriver == 'Firefox':
    firefox_options = webdriver.FirefoxOptions()
    firefox_options.add_argument('-headless')
    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.set_preference('permissions.default.image', 2)
    #禁用Flash
    firefox_profile.set_preference('dom.ipc.plugins.enabled.npswf32.dll', 'false')
    #禁用javascript，部分网站可能会不能正常使用
    #firefox_profile.set_preference('javascript.enabled', 'false')

#建立数据存储目录
try:
    os.mkdir('output')
except FileExistsError:
    pass

#初始化历史信息数据库
conn = sqlite3.connect('history.db')
cursor = conn.cursor()
try:
    cursor.execute('select * from history')
except:
    sqlite_db.main(cursor)

import threading

#初始化全局变量
page_list = []
info_list = []
url_info = []
info_count = [0]*len(city)
#定义Driver队列
driver_queue = queue.Queue(thread_number)
for i in range(thread_number):
    if chosen_webdriver == 'Chrome':
        driver_init = webdriver.Chrome(options=chrome_options)
    if chosen_webdriver == 'Firefox':
        driver_init = webdriver.Firefox(firefox_binary=firefox_location, options=firefox_options, firefox_profile = firefox_profile)
    #设置浏览器分辨率
    size = driver_init.get_window_size()
    driver_init.set_window_size(1280, size['height'])
    driver_queue.put(driver_init)


def worker_list(page, info_list):
    #从Driver队列获取一个Driver
    driver = driver_queue.get(block=True, timeout=None)
    count = get_web.get_info_list(driver, page, info_list, date_limit)
    info_count[count[0]] += count[1]
    #将Driver放回从Driver队列
    driver_queue.put(driver)

def worker_info(info, writer, writer_all=None):
    #从Driver队列获取一个Driver
    driver = driver_queue.get(block=True, timeout=None)
    url_info.append(get_web.get_info(driver, info, writer, writer_all))
    #将Driver放回从Driver队列
    driver_queue.put(driver)
    return

#info_list去重
def del_dup(info_list):
    all_count = len(info_list)
    tmp_list = []
    for  i in info_list:
        if i not in tmp_list:
            tmp_list.append(i)
    duplicate_count = all_count - len(tmp_list)
    info_list = []
    for info in tmp_list:
        #检查数据库中是否存在已抓取过的记录
        if sqlite_db.check(cursor,info) == 1:
            #当存在已抓取的数据并且设置为不跳过已抓取的信息时
            if check_history == 0:
                info_list.append(info)
        #检查数据库中不存在已抓取过的记录
        else:
            info_list.append(info)
            if write_data == 'y':
                sqlite_db.add(cursor,info)
    unusefull_count = all_count - len(info_list) - duplicate_count
    logger.info(f'共抓取 {all_count} 条信息，去除重复信息 {duplicate_count} 条，已抓取信息 {unusefull_count} 条，剩余 {len(info_list)} 条。')
    logger.info('抓取公告列表完成，开始抓取正文。')
    #打乱列表顺序，避免短时间大量抓取同一网站
    random.shuffle(info_list)
    return info_list

def get_page_list(m):
    for page in page_list_fun.get_list(m):
        page_list.append([m, page])
    #打乱列表顺序，避免短时间大量抓取同一网站
    random.shuffle(page_list)

def mulit_thread(page_list):
    global info_list
    thread_list=[]
    for i in page_list:
        t = threading.Thread(target=worker_list,args=(i, info_list))
        t.setDaemon(True)
        thread_list.append(t)
    for t in thread_list:
        while True:
            if threading.activeCount() <= thread_number:
                t.start()
                break
    for t in thread_list:
        t.join()
    return

def main():
    #删除上次的数据
    old_files = os.listdir('./output/')
    for i in old_files:
        os.remove('./output/'+i)
    
    #定义数据储存文件列表
    csv_file_list = []
    for i in range(len(city)):
        file_name = '%s%s.%s%s' % ('./output/', i, city[i], '.csv')
        csv_file = open(file_name, 'w', newline='', encoding=encoding)
        csv_file_list.append(csv_file)
        writer = csv.writer(csv_file)
        writer.writerow(['时间', '标题', '链接', '内容'])

        
    #设置保存所有数据汇总的文件
    csv_file_all = open('./output/All.csv', 'w', newline='', encoding=encoding)
    writer_all = csv.writer(csv_file_all)
    writer_all.writerow(['网站', '时间', '标题', '链接', '内容'])
    

    
    #获取起始页列表
    for i in range(len(city)):
        get_page_list(i)
    
    #获取正文列表
    global info_list
    mulit_thread(page_list)
    for m in range(len(info_count)):
        logger.info(f'{city[m]} 列表抓取完成，{date_limit} 天内共有 {info_count[m]} 条信息。')
    
    #info_list去重
    info_list = del_dup(info_list)
    
    #抓取正文
    info_thread_list = []
    for i in info_list:
        writer = csv.writer(csv_file_list[i[0]])
        t = threading.Thread(target=worker_info,args=(i, writer, writer_all))
        t.setDaemon(True)
        info_thread_list.append(t)
    for t in info_thread_list:
        while True:
            if threading.activeCount() <= thread_number:
                t.start()
                #print(len(info_thread_list), r'/', len(info_list))
                break
    for t in info_thread_list:
        t.join()
    logger.info('正文抓取完成，开始进行收尾处理。')
    
    #关闭浏览器进程
    for i in range(thread_number):
        driver = driver_queue.get(block=True, timeout=None)
        driver.quit()


    #关闭全部数据csv文件
    csv_file_all.close()
    for i in csv_file_list:
        i.close()
        
    #按关键词匹配数据单独输出
    re_filter.main()
    #是否写入数据库
    if write_data == 'y' and save_info_to_sql:
        for i in url_info:
            sqlite_db.add_info(cursor, i)

    cursor.close()
    conn.commit()
    conn.close()
    input('抓取完成，按回车键退出。')
    return

#单独抓取配置文件中第n个网站
#使用方法：python spider.py n
#n为spider.conf文件中网站的次序，从0开始
def get():
    #读取网站数据
    city_num = int(sys.argv[1])
    
    #定义数据储存文件列表
    file_name = '%s%s.%s%s' % ('./output/', city_num, city[city_num], '.csv')
    csv_file = open(file_name, 'w', newline='', encoding=encoding)
    writer = csv.writer(csv_file)
    writer.writerow(['时间', '标题', '链接', '内容'])
    
    #获取起始页列表
    get_page_list(city_num)
    #获取正文列表
    global info_list
    mulit_thread(page_list)
    
    #info_list去重
    info_list = del_dup(info_list)
    
    #抓取正文
    info_thread_list = []
    for i in range(len(info_list)):
        t = threading.Thread(target=worker_info,args=(info_list[i], writer))
        t.setDaemon(True)
        info_thread_list.append(t)
    for t in info_thread_list:
        while True:
            if threading.activeCount() <= thread_number:
                t.start()
                break
    for t in info_thread_list:
        t.join()
    logger.info('正文抓取完成，开始进行收尾处理。')

    #关闭浏览器进程
    for i in range(thread_number):
        driver = driver_queue.get(block=True, timeout=None)
        driver.quit()
        
    #关闭数据文件
    csv_file.close()
    #是否写入数据库
    if write_data == 'y' and save_info_to_sql:
        for i in url_info:
            sqlite_db.add_info(cursor, i)

    cursor.close()
    conn.commit()
    conn.close()
    input('抓取完成，按回车键退出。')
    return


if __name__=='__main__':
    if len(sys.argv)==1:
        main()
    else:
        get()
