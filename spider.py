#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'一个招投标网站信息采集工具'
__author__ = 'Zhang Minghao'

import get_info
import config_load

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.binary_location = r'D:\Program Files\Chrome\Chrome\chrome.exe'
driver = webdriver.Chrome(options=chrome_options)

#读取配置文件
conf = config_load.load_conf()
encoding = conf.get('DEFAULT', 'encoding')

#import sqlite3
import csv
#设置保存所有数据汇总的文件
csv_file_all = open('./output/All.csv', 'w', newline='', encoding=encoding)
writer_all = csv.writer(csv_file_all)
writer_all.writerow(['标题', '时间', '链接', '内容'])



#读取网站列表
city = conf.sections()

for m in range(len(city)):
    #读取网站配置
    site = conf.get(city[m], 'url')
    start_page = conf.get(city[m], 'start_page')
    stop_page = conf.get(city[m], 'stop_page')
    
    #设置数据储存文件
    file_name = '%s%s%s' % ('./output/', city[m], '.csv')
    csv_file = open(file_name, 'w', newline='', encoding=encoding)
    writer = csv.writer(csv_file)
    writer.writerow(['标题', '时间', '链接', '内容'])

    n = int(start_page)
    while n <= int(stop_page):
        #载入标题列表
        page = '%s%s' % (site, str(n))
        driver.get(page)
        
        
        data = driver.find_element_by_class_name('wb-data-item').\
            find_elements_by_tag_name('li')
        for i in range(len(data)):
            item = data[i].find_element_by_tag_name('a')
            title = data[i].find_element_by_class_name('wb-data-infor').text
            time = data[i].find_element_by_class_name('wb-data-date').text
            url = item.get_attribute('href')
            info = get_info.get(url)
            writer.writerow([time, title, url, info])
            writer_all.writerow([time, title, url, info])
        n = n + 1
    csv_file.close()

csv_file_all.close()