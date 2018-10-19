#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'一个招投标网站信息采集工具'
__author__ = 'Zhang Minghao'

#加载功能模块
#import get_info
import get_web
import config_load

#import sqlite3
import csv
import os
import sys

#读取配置文件
conf = config_load.load_conf()
encoding = conf.get('DEFAULT', 'encoding')

#建立数据存储目录
try:
    os.mkdir('output')
except FileExistsError:
    pass

def main():
    #设置保存所有数据汇总的文件
    csv_file_all = open('./output/All.csv', 'w', newline='', encoding=encoding)
    writer_all = csv.writer(csv_file_all)
    writer_all.writerow(['网站', '时间', '标题', '链接', '内容'])


    #读取网站数据
    for m in range(len(conf.sections())):
       get_web.get(conf, m, writer_all)

    #关闭数据汇总文件
    csv_file_all.close()
    os.system('taskkill /IM chromedriver.exe /T /F')
    return

#单独抓取配置文件中第n个网站
#使用方法：python spider.py n
#n为spider.conf文件中网站的次序，从0开始
def get():
    city = int(sys.argv[1])
    get_web.get(conf, city)
    os.system('taskkill /IM chromedriver.exe /T /F')
    return


if __name__=='__main__':
    if len(sys.argv)==1:
        main()
    else:
        get()
