#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'一个招投标网站信息采集工具'
__author__ = 'Zhang Minghao'

#读取配置文件
import config_load
conf = config_load.load_conf()
chrome_location = conf.get('DEFAULT', 'chrome_location')

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.binary_location = chrome_location
driver = webdriver.Chrome(options=chrome_options)

def get(url, info_class_name):
    driver.get(url)
    info = driver.find_element_by_class_name(info_class_name).text
    return info