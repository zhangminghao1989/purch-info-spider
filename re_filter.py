#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'一个招投标网站信息采集工具'
__author__ = 'Zhang Minghao'

#读取配置文件
import re
import config_load
conf = config_load.load_conf()
pattern = conf.get('DEFAULT', 'pattern')

def main(info):
    a = re.search(pattern, info)
    if a != None:
        return 1
    else:
        return 0
