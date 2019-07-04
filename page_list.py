#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'一个招投标网站信息采集工具'
__author__ = 'Zhang Minghao'

import re
import sys

#读取配置文件
import config_load
conf = config_load.load_conf()

def get_list(m):
    #读取网站配置
    city = conf.sections()
    site = conf.get(city[m], 'url')
    url_var_0 = ['']
    url_var_1 = ['']
    url_var_2 = ['']
    url_var_3 = ['']
    url_var_4 = ['']
    
    if conf.get(city[m], 'url_var_0') != '':
        url_var_0 = re.split(',', conf.get(city[m], 'url_var_0'))
    if conf.get(city[m], 'url_var_1') != '':
        url_var_1 = re.split(',', conf.get(city[m], 'url_var_1'))
    if conf.get(city[m], 'url_var_2') != '':
        url_var_2 = re.split(',', conf.get(city[m], 'url_var_2'))
    if conf.get(city[m], 'url_var_3') != '':
        url_var_3 = re.split(',', conf.get(city[m], 'url_var_3'))
    if conf.get(city[m], 'url_var_4') != '':
        url_var_4 = re.split(',', conf.get(city[m], 'url_var_4'))
    page_list = []
    for a in url_var_0:
        for b in url_var_1:
            for c in url_var_2:
                for d in url_var_3:
                    for e in url_var_4:
                        page_list.append(site.format(a, b, c, d, e))
    return page_list

if __name__=='__main__':
    if len(sys.argv)==2:
        a = get_list(int(sys.argv[1]))
        print(a)
