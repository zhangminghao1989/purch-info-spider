#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'一个招投标网站信息采集工具'
__author__ = 'Zhang Minghao'

import get_info
import get_web
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
import os
#设置保存所有数据汇总的文件
try:
    os.mkdir('output')
except FileExistsError:
    pass

csv_file_all = open('./output/All.csv', 'w', newline='', encoding=encoding)
writer_all = csv.writer(csv_file_all)
writer_all.writerow(['网站', '时间', '标题', '链接', '内容'])



#读取网站数据
for m in range(len(conf.sections())):
   get_web.get(conf, m, writer_all)


csv_file_all.close()