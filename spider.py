#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'一个招投标网站信息采集工具'
__author__ = 'Zhang Minghao'

#加载功能模块
import get_web
import config_load

#import sqlite3
import csv
import os
import sys
import queue

#设置获取最近n天的信息
date_limit = input('获取最近几天的信息？（默认为2天）：')
if date_limit == '':
    date_limit = 2
else:
    date_limit = int(date_limit)
#读取配置文件
conf = config_load.load_conf()
encoding = conf.get('DEFAULT', 'encoding')
chrome_location = conf.get('DEFAULT', 'chrome_location')
thread_number = int(conf.get('DEFAULT', 'thread_number'))
pattern = conf.get('DEFAULT', 'pattern')
city = conf.sections()

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
    location = r'D:\Program Files\Firefox\firefox.exe'
    options = webdriver.FirefoxOptions()
    options.add_argument('-headless')
    profile = webdriver.FirefoxProfile()
    profile.set_preference('permissions.default.image', 2)
    #禁用Flash
    profile.set_preference('dom.ipc.plugins.enabled.npswf32.dll', 'false')
    #禁用Js
    profile.set_preference('javascript.enabled', 'false')

#建立数据存储目录
try:
    os.mkdir('output')
except FileExistsError:
    pass

import threading

#定义内容页列表
info_list = []

#定义Driver队列
driver_queue = queue.Queue(thread_number)
for i in range(thread_number):
    if chosen_webdriver == 'Chrome':
        driver_queue.put(webdriver.Chrome(options=chrome_options))
    if chosen_webdriver == 'Firefox':
        driver_queue.put(webdriver.Firefox(firefox_binary=location, options=options, firefox_profile = profile))

def worker_list(city_num, info_list):
    #从Driver队列获取一个Driver
    driver = driver_queue.get(block=True, timeout=None)
    get_web.get_info_list(driver, city_num, info_list, date_limit)
    #将Driver放回从Driver队列
    driver_queue.put(driver)

def worker_info(info, writer, writer_all=None, writer_target=None):
    #从Driver队列获取一个Driver
    driver = driver_queue.get(block=True, timeout=None)
    get_web.get_info(driver, info, writer, writer_all, writer_target)
    #将Driver放回从Driver队列
    driver_queue.put(driver)

def main():
    #删除上次的数据
    old_files = os.listdir('./output/')
    for i in old_files:
        os.remove('./output/'+i)
    
    #定义数据储存文件列表
    csv_file_list = []
    for i in range(len(conf.sections())):
        file_name = '%s%s.%s%s' % ('./output/', i, city[i], '.csv')
        csv_file = open(file_name, 'w', newline='', encoding=encoding)
        csv_file_list.append(csv_file)
        writer = csv.writer(csv_file)
        writer.writerow(['时间', '标题', '链接', '内容'])

        
    #设置保存所有数据汇总的文件
    csv_file_all = open('./output/All.csv', 'w', newline='', encoding=encoding)
    writer_all = csv.writer(csv_file_all)
    writer_all.writerow(['网站', '时间', '标题', '链接', '内容'])
    
    #设置保存关键词匹配数据的文件
    csv_file_target = open('./output/筛选结果.csv', 'w', newline='', encoding=encoding)
    writer_target = csv.writer(csv_file_target)
    writer_target.writerow(['网站', '时间', '标题', '链接', '内容'])
    
    #获取正文列表
    global info_list
    thread_list=[]
    for i in range(len(conf.sections())):
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

    print('抓取公告列表完成，开始抓取正文。')
    
    #info_list去重
    tmp_list = []
    for  i in info_list:
        if i not in tmp_list:
            tmp_list.append(i)
    info_list = tmp_list
    
    #抓取正文
    info_thread_list = []
    for i in info_list:
        writer = csv.writer(csv_file_list[i[0]])
        t = threading.Thread(target=worker_info,args=(i, writer, writer_all, writer_target))
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
    
    #关闭浏览器进程
    i = 0
    while i < thread_number:
        driver = driver_queue.get(block=True, timeout=None)
        driver.quit()
        i = i + 1

    #关闭数据文件
    csv_file_all.close()
    csv_file_target.close()
    for i in csv_file_list:
        i.close()
    
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
    
    #获取正文列表
    global info_list
    worker_list(city_num, info_list)
    print('抓取公告列表完成，开始抓取正文。')
    
    #info_list去重
    tmp_list = []
    for  i in info_list:
        if i not in tmp_list:
            tmp_list.append(i)
    info_list = tmp_list    
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
                #print(len(info_thread_list), r'/', len(info_list))
                break
    for t in info_thread_list:
        t.join()

    #关闭数据文件
    csv_file.close()
    #关闭浏览器进程
    i = 0
    while i < thread_number:
        driver = driver_queue.get(block=True, timeout=None)
        driver.quit()
        i = i + 1
    return


if __name__=='__main__':
    if len(sys.argv)==1:
        main()
    else:
        get()
