#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'一个招投标网站信息采集工具'
__author__ = 'Zhang Minghao'

#设置获取最近n天的信息
date_limit = input('获取最近几天的信息？（默认为2天）：')
if date_limit == '':
    date_limit = 2
else:
    date_limit = int(date_limit)

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
    #删除上次的数据
    old_files = os.listdir('./output/')
    for i in old_files:
        os.remove('./output/'+i)
    
    #设置保存所有数据汇总的文件
    csv_file_all = open('./output/All.csv', 'w', newline='', encoding=encoding)
    writer_all = csv.writer(csv_file_all)
    writer_all.writerow(['网站', '时间', '标题', '链接', '内容'])


    #读取网站数据
    for m in range(len(conf.sections())):
       get_web.get(m, date_limit, writer_all)

    #关闭数据汇总文件
    csv_file_all.close()
    
    #关闭浏览器进程
    os.popen('taskkill /IM chromedriver.exe /T /F')
    return

#单独抓取配置文件中第n个网站
#使用方法：python spider.py n
#n为spider.conf文件中网站的次序，从0开始
def get():
    #读取网站数据
    city = int(sys.argv[1])
    get_web.get(city, date_limit)
    #关闭浏览器进程
    os.popen('taskkill /IM chromedriver.exe /T /F')
    return


if __name__=='__main__':
    if len(sys.argv)==1:
        main()
    else:
        get()
