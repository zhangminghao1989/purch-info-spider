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
        url_var_0 = make_list(str_to_int(re.split(',', conf.get(city[m], 'url_var_0'))))
    if conf.get(city[m], 'url_var_1') != '':
        url_var_1 = make_list(str_to_int(re.split(',', conf.get(city[m], 'url_var_1'))))
    if conf.get(city[m], 'url_var_2') != '':
        url_var_2 = make_list(str_to_int(re.split(',', conf.get(city[m], 'url_var_2'))))
    if conf.get(city[m], 'url_var_3') != '':
        url_var_3 = make_list(str_to_int(re.split(',', conf.get(city[m], 'url_var_3'))))
    if conf.get(city[m], 'url_var_4') != '':
        url_var_4 = make_list(str_to_int(re.split(',', conf.get(city[m], 'url_var_4'))))
    page_list = []
    for a in range(len(url_var_0)):
        for b in range(len(url_var_1)):
            for c in range(len(url_var_2)):
                for d in range(len(url_var_3)):
                    for e in range(len(url_var_4)):
                        page_list.append(site.format(url_var_0[a], url_var_1[b], url_var_2[c], url_var_3[d], url_var_4[e]))
    return page_list
    
#生成变量列表
def make_list(var):
    page_list = list(range(var[0], var[1]+1))
    n = 0
    while n <= var[1]-var[0]:
        page_list[n] = str(page_list[n]).zfill(var[2])
        n = n + 1
    return page_list
    
#转换数据类型
def str_to_int(var):
    n = 0
    while n < 3:
        try:
            var[n] = int(var[n])
        except ValueError:
            var = []
            return var
        except IndexError:
            var = []
            return var
        n = n + 1
    return var

if __name__=='__main__':
    if len(sys.argv)==2:
        get_list(int(sys.argv[1]))
