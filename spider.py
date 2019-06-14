#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'一个招投标网站信息采集工具'
__author__ = 'Zhang Minghao'

#设置获取最近n天的信息
date_limit = input('获取最近几天的信息？（默认为2天）：')
if date_limit == '':
    date_limit = 2
else:
    date_limit = int(date_limit)

#加载功能模块
import get_web
import config_load

#import sqlite3
import csv
import os
import sys
import queue

#读取配置文件
conf = config_load.load_conf()
encoding = conf.get('DEFAULT', 'encoding')
chrome_location = conf.get('DEFAULT', 'chrome_location')
thread_number = int(conf.get('DEFAULT', 'thread_number'))

#配置webdriver
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
chrome_options = Options()
#chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--log-level=3')
chrome_options.binary_location = chrome_location
chrome_options.add_argument('--blink-settings=imagesEnabled=false')

#建立数据存储目录
try:
    os.mkdir('output')
except FileExistsError:
    pass

import threading

def worker(city, writer_all=None, writer_target=None):
    driver = webdriver.Chrome(options=chrome_options)
    get_web.get(driver, city, date_limit, writer_all, writer_target)
    #关闭浏览器进程
    driver.quit()

def main():
    #删除上次的数据
    old_files = os.listdir('./output/')
    for i in old_files:
        os.remove('./output/'+i)
    
    #设置保存所有数据汇总的文件
    csv_file_all = open('./output/All.csv', 'w', newline='', encoding=encoding)
    writer_all = csv.writer(csv_file_all)
    writer_all.writerow(['网站', '时间', '标题', '链接', '内容'])
    
    #设置保存关键词匹配数据的文件
    csv_file_target = open('./output/筛选结果.csv', 'w', newline='', encoding=encoding)
    writer_target = csv.writer(csv_file_target)
    writer_target.writerow(['网站', '时间', '标题', '链接', '内容'])

    #读取网站数据

    thread_list=[]
    for i in range(len(conf.sections())):
        t = threading.Thread(target=worker,args=(i, writer_all, writer_target))
        t.setDaemon(True)
        thread_list.append(t)
    for t in thread_list:
        while True:
            if threading.activeCount() <= thread_number:
                t.start()
                break
    for t in thread_list:
        t.join()

    #关闭数据汇总文件
    csv_file_all.close()
    csv_file_target.close()
    
    return

#单独抓取配置文件中第n个网站
#使用方法：python spider.py n
#n为spider.conf文件中网站的次序，从0开始
def get():
    #读取网站数据
    city = int(sys.argv[1])
    worker(city)
    return


if __name__=='__main__':
    if len(sys.argv)==1:
        main()
    else:
        get()
