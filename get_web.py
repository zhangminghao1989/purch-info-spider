#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'一个招投标网站信息采集工具'
__author__ = 'Zhang Minghao'




#读取配置文件
import config_load, logger
conf = config_load.load_conf()
website_data = config_load.load_website_data()
city = website_data.sections()

import csv
import re
import time
from datetime import datetime, timedelta
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def get_info_list(driver, page, info_list, date_limit):
    count = 0
    m = page[0]
    #读取网站配置
    data_class_name = website_data.get(city[m], 'data_class_name')
    data_tag_name = website_data.get(city[m], 'data_tag_name')
    data_xpath = website_data.get(city[m], 'data_xpath')
    list_tag_name = website_data.get(city[m], 'list_tag_name')
    page_link_xpath = website_data.get(city[m], 'page_link_xpath')
    next_page_xpath = website_data.get(city[m], 'next_page_xpath')
    wait_for_load = website_data.get(city[m], 'wait_for_load')
    page_query = website_data.get(city[m], 'page_query')
    
    #获取标题列表网页
    wait_for_load_count = 0
    while wait_for_load_count <= 3:
        #载入标题列表网页
        driver.get(page[1])
        time.sleep(1)
        #等待页面载入完成
        if wait_for_load != '':
            try:
                WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, wait_for_load)))
                logger.debug(f'{city[m]} {page[1]} 页面载入完成！')
            except:
                wait_for_load_count += 1
                logger.debug(f'{city[m]} {page[1]} 页面载入失败，第 {wait_for_load_count} 次重载！')
                continue
            break
        else:
            break
    if wait_for_load_count > 3:
        logger.warning(f'{city[m]} {page[1]} 页面未能完全载入，尝试抓取已载入信息！')

    date_status = 0
    while date_status == 0:
        attempts = 0
        success = False
        while attempts < 3 and not success:
            try:
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
                    logger.error(f'错误：[{city[m]}]未设置data_class_name、data_tag_name或data_xpath参数!')
                    attempts = 3
                    continue
            except:
                attempts += 1
                time.sleep(5)
                logger.debug(f'{m} {city[m]} {driver.current_url} 标题列表抓取失败，刷新重试！')
                driver.refresh()
            if attempts == 3:
                logger.error(f'{m} {city[m]} {driver.current_url} 标题列表抓取失败，跳过！')
                data = 0
                break
        if data == 0:
            break


        #处理数据
        date_status_count = 0
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
                date_status_count += 1
                if date_status_count > 2:
                    date_status = 1
                    break
                else:
                    continue
            #储存数据
            count += 1
            info = []
            info.append(m) #city_num
            info.append(item.get_attribute('href')) #url
            info.append(item.text) #title
            info.append(date) #date
            info_list.append(info)
        if date_status == 1:
            break
        #点击下一页
        url = driver.current_url
        try:
            driver.find_element_by_xpath(next_page_xpath).click()
        except:
            if page_query != '':
                url_next = page_next(url, page_query)
                driver.get(url_next)
                logger.debug(f'{city[m]} {url} 翻页失败，使用备用翻页方式。')
            else:
                logger.debug(f'{city[m]} {url} 翻页失败，无备用翻页方式。')
                break
        try:
            WebDriverWait(driver, 10).until(EC.staleness_of(data[1]))
        except:
            logger.warning(f'{city[m]} {driver.current_url} 使用备用翻页方式翻页失败！')
            break
    logger.debug(f'{city[m]} {page[1]} 列表抓取完成，{date_limit} 天内有 {count} 条信息。')
    return [m, count]


def get_info(driver, info_data, writer, writer_all):
    import get_info_fun
    city_num = info_data[0]
    url = info_data[1]
    title = info_data[2]
    date = info_data[3]
    info_class_name = website_data.get(city[city_num], 'info_class_name')
    info_id_name = website_data.get(city[city_num], 'info_id_name')
    #获取正文
    if info_class_name != '':
        info = get_info_fun.get_class(driver, url, info_class_name)
    elif info_id_name != '':
        info = get_info_fun.get_id(driver, url, info_id_name)
    else:
        info = f'错误：[{city[city_num]}]未设置info_class_name或info_id_name参数'
        logger.error(info)
    
    #输出数据
    writer.writerow([date, title, url, info])
    try:
        writer_all.writerow([city[city_num], date, title, url, info])
    except TypeError:
        pass
    except AttributeError:
        pass
    
    return [url, info]

#备用翻页方式
def page_next(url, page_query):
    from urllib import parse
    #解析URL
    url_obj = parse.urlparse(url)
    #读取页码
    query = dict(parse.parse_qsl(url_obj.query))
    page_num = query[page_query]
    #页码+1
    page_num = str(int(page_num) + 1).zfill(len(page_num))
    query[page_query] = page_num
    parse.urlencode(query)
    #输出下一页url
    return parse.urlunparse(url_obj._replace(query=parse.urlencode(query)))