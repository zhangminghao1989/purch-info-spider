#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'一个招投标网站信息采集工具'
__author__ = 'Zhang Minghao'

#读取配置文件
import time, logger

def get_class(driver, url, info_class_name):
    attempts = 0
    success = False
    while attempts < 3 and not success:
        try:
            driver.get(url)
            time.sleep(1)
            info = driver.find_element_by_class_name(info_class_name).text
            success = True
            logger.debug(f'{url} 抓取成功！')
        except:
            attempts += 1
            if attempts == 3:
                info = '抓取重试次数达到3次，内容页抓取失败！'
                logger.error(f'{url} {info}')
                break
    return info

def get_id(driver, url, info_id_name):
    attempts = 0
    success = False
    while attempts < 3 and not success:
        try:
            driver.get(url)
            time.sleep(1)
            info = driver.find_element_by_id(info_id_name).text
            success = True
            logger.debug(f'{url} 抓取成功！')
        except:
            attempts += 1
            if attempts == 3:
                info = '抓取重试次数达到3次，内容页抓取失败！'
                logger.error(f'{url} {info}')
                break
    return info