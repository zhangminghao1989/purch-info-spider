#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'一个招投标网站信息采集工具'
__author__ = 'Zhang Minghao'

import get_info
import page_list

#读取配置文件
import config_load
conf = config_load.load_conf()
chrome_location = conf.get('DEFAULT', 'chrome_location')
encoding = conf.get('DEFAULT', 'encoding')
pattern = conf.get('DEFAULT', 'pattern')

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.binary_location = chrome_location
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(options=chrome_options)

import csv
import re
import time
from datetime import datetime, timedelta

def get(m, date_limit, writer_all=None, writer_target=None):
    #读取网站配置

    city = conf.sections()
    site = conf.get(city[m], 'url')
    data_class_name = conf.get(city[m], 'data_class_name')
    data_tag_name = conf.get(city[m], 'data_tag_name')
    data_xpath = conf.get(city[m], 'data_xpath')
    list_tag_name = conf.get(city[m], 'list_tag_name')
    page_link_xpath = conf.get(city[m], 'page_link_xpath')
    info_class_name = conf.get(city[m], 'info_class_name')
    info_id_name = conf.get(city[m], 'info_id_name')

    #设置数据储存文件
    file_name = '%s%s.%s%s' % ('./output/', m, city[m], '.csv')
    csv_file = open(file_name, 'w', newline='', encoding=encoding)
    writer = csv.writer(csv_file)
    writer.writerow(['时间', '标题', '链接', '内容'])

    #获取标题列表网页
    page = page_list.get_list(m)
    
    for n in range(len(page)):
        attempts = 0
        success = False
        while attempts < 3 and not success:
            try:
                #载入标题列表网页
                driver.get(page[n])
                time.sleep(1)
                #读取标题列表数据
                if data_class_name != '':
                    data = driver.find_element_by_class_name(data_class_name).find_elements_by_tag_name(list_tag_name)
                    success = True
                elif data_tag_name != '':
                    data = driver.find_element_by_tag_name(data_tag_name).find_elements_by_tag_name(list_tag_name)
                    success = True
                elif data_xpath != '':
                    data = driver.find_element_by_xpath(data_xpath).find_elements_by_tag_name(list_tag_name)
                    success = True
                else:
                    print('错误：[', city[m], ']未设置data_class_name、data_tag_name或data_xpath参数')
                    attempts = 3
                    continue
            except:
                attempts += 1
                
        if attempts == 3:
            print(m, city[m], page[n], '标题列表抓取失败！')
            continue

        #处理数据
        for i in range(len(data)):
            #标题选择器，默认直接读取<a>，也可使用xpath定位方式，读取失败则说明不是标题列表
            try:
                if page_link_xpath != '':
                    item = data[i].find_element_by_xpath(page_link_xpath)
                else:
                    item = data[i].find_element_by_tag_name('a')
            except:
                continue
            title = item.text
            url = item.get_attribute('href')
            #获取列表中的发布时间，使用正则表达式，读取失败则说明不是标题列表
            try:
                date = re.search(r'(20\d{2}-\d{1,2}-\d{1,2})', data[i].text).group(0)
            except:
                continue
            #跳过n天前的信息
            now = datetime.now().date()
            info_date = datetime.strptime(date, '%Y-%m-%d').date()
            date_diff = now - info_date
            if date_diff.days > date_limit:
                break

            #获取正文
            if info_class_name != '':
                info = get_info.get_class(url, info_class_name)
            elif info_id_name != '':
                info = get_info.get_id(url, info_id_name)
            else:
                return print('错误：[', city[m], ']未设置info_class_name或info_id_name参数')
            
            #输出数据
            writer.writerow([date, title, url, info])
            try:
                writer_all.writerow([city[m], date, title, url, info])
            except TypeError:
                pass
            except AttributeError:
                pass
            
            #按关键词匹配数据单独输出
            
            if re.search(pattern, info ) != None:
                try:
                    writer_target.writerow([city[m], date, title, url, info])
                except TypeError:
                    pass
                except AttributeError:
                    pass

            
            
    csv_file.close()
    return