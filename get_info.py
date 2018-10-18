#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.binary_location = r'D:\Program Files\Chrome\Chrome\chrome.exe'
driver = webdriver.Chrome(options=chrome_options)

def get(url):
    driver.get(url)
    info = driver.find_element_by_class_name('infodetail').text
    return info