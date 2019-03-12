#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'一个招投标网站信息采集工具'
__author__ = 'Zhang Minghao'

#读取配置文件
import time
import config_load
conf = config_load.load_conf()
chrome_location = conf.get('DEFAULT', 'chrome_location')

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--log-level=3')
chrome_options.binary_location = chrome_location
chrome_options.add_argument('--blink-settings=imagesEnabled=false')
driver = webdriver.Chrome(options=chrome_options)

def get_class(url, info_class_name):
    attempts = 0
    success = False
    while attempts < 3 and not success:
        try:
            driver.get(url)
            time.sleep(1)
            info = driver.find_element_by_class_name(info_class_name).text
            print(url, '抓取成功')
            success = True
        except:
            attempts += 1
            if attempts == 3:
                print('抓取重试次数达到3次，内容页抓取失败！')
                info = '抓取重试次数达到3次，内容页抓取失败！'
                break
    return info

def get_id(url, info_id_name):
    attempts = 0
    success = False
    while attempts < 3 and not success:
        try:
            driver.get(url)
            time.sleep(1)
            info = driver.find_element_by_id(info_id_name).text
            print(url, '抓取成功')
            success = True
        except:
            attempts += 1
            if attempts == 3:
                print('抓取重试次数达到3次，内容页抓取失败！')
                info = '抓取重试次数达到3次，内容页抓取失败！'
                break
        return info