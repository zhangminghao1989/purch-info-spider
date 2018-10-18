#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'一个招投标网站信息采集工具'
__author__ = 'Zhang Minghao'

import get_info

#读取配置文件
import config_load
conf = config_load.load_conf()
chrome_location = conf.get('DEFAULT', 'chrome_location')
encoding = conf.get('DEFAULT', 'encoding')

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.binary_location = chrome_location
driver = webdriver.Chrome(options=chrome_options)

import csv

def get(conf, m, writer_all):
    #读取网站配置
    city = conf.sections()
    site = conf.get(city[m], 'url')
    start_page = conf.get(city[m], 'start_page')
    stop_page = conf.get(city[m], 'stop_page')
    
    #设置数据储存文件
    file_name = '%s%s%s' % ('./output/', city[m], '.csv')
    csv_file = open(file_name, 'w', newline='', encoding=encoding)
    writer = csv.writer(csv_file)
    writer.writerow(['时间', '标题', '链接', '内容'])

    n = int(start_page)
    while n <= int(stop_page):
        #载入标题列表网页
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
            writer_all.writerow([city[m], time, title, url, info])
        n = n + 1
    csv_file.close()
    return