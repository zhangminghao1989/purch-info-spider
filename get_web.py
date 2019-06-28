#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'一个招投标网站信息采集工具'
__author__ = 'Zhang Minghao'


import page_list

#读取配置文件
import config_load
conf = config_load.load_conf()
pattern = conf.get('DEFAULT', 'pattern')
city = conf.sections()

import csv
import re
import time
from datetime import datetime, timedelta
#driver.find_element_by_partial_link_text('下页').click()
def get_info_list(driver, m, info_list, date_limit):
    #读取网站配置
    site = conf.get(city[m], 'url')
    data_class_name = conf.get(city[m], 'data_class_name')
    data_tag_name = conf.get(city[m], 'data_tag_name')
    data_xpath = conf.get(city[m], 'data_xpath')
    list_tag_name = conf.get(city[m], 'list_tag_name')
    page_link_xpath = conf.get(city[m], 'page_link_xpath')

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
            #获取列表中的发布时间，使用正则表达式，读取失败则说明不是标题列表
            try:
                date = re.search(r'(20\d{2}-\d{1,2}-\d{1,2})', re.sub(re.compile(r'/|\\'), '-', data[i].text)).group(0)
            except:
                continue
            #跳过n天前的信息
            now = datetime.now().date()
            info_date = datetime.strptime(date, '%Y-%m-%d').date()
            date_diff = now - info_date
            if date_diff.days > date_limit:
                break
            #储存数据
            info = []
            info.append(m) #city_num
            info.append(item.get_attribute('href')) #url
            info.append(item.text) #title
            info.append(date) #date
            info_list.append(info)
            
    return


def get_info(driver, info_data, writer, writer_all, writer_target):
    import get_info
    city_num = info_data[0]
    url = info_data[1]
    title = info_data[2]
    date = info_data[3]
    info_class_name = conf.get(city[city_num], 'info_class_name')
    info_id_name = conf.get(city[city_num], 'info_id_name')
    #获取正文
    if info_class_name != '':
        info = get_info.get_class(driver, url, info_class_name)
    elif info_id_name != '':
        info = get_info.get_id(driver, url, info_id_name)
    else:
        return print('错误：[', city[city_num], ']未设置info_class_name或info_id_name参数')

    #输出数据
    writer.writerow([date, title, url, info])
    try:
        writer_all.writerow([city[city_num], date, title, url, info])
    except TypeError:
        pass
    except AttributeError:
        pass
    
    #按关键词匹配数据单独输出
    
    if re.search(pattern, info ) != None:
        try:
            writer_target.writerow([city[city_num], date, title, url, info])
        except TypeError:
            pass
        except AttributeError:
            pass

    return