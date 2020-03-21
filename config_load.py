#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'一个招投标网站信息采集工具'
__author__ = 'Zhang Minghao'

import configparser, os

def load_conf(conf_name='spider.conf'):
    """
    读取配置文件
    """
    if os.path.exists('./spider.conf'):
        pass
    else:
        from shutil import copyfile
        copyfile('./spider.conf.example','./spider.conf')
    config = configparser.ConfigParser()
    config.read(conf_name, encoding='utf-8')
    return config
    
def load_website_data(conf_name='website_data.conf'):
    """
    读取配置文件
    """
    config = configparser.ConfigParser()
    config.read(conf_name, encoding='utf-8')
    return config
    
if __name__=='__main__':
    load_conf()