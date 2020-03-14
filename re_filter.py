#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'一个招投标网站信息采集工具'
'用于对抓取结果进行重新筛选'
__author__ = 'Zhang Minghao'
def main():
    #读取配置文件
    import config_load
    conf = config_load.load_conf()
    encoding = conf.get('DEFAULT', 'encoding')
    import filter
    import csv
    csv_read_file = open('./output/All.csv', 'r', newline='', encoding=encoding)
    csv_write_file = open('./output/筛选结果.csv', 'w', newline='', encoding=encoding)
    csv_junk_file = open('./output/无用信息.csv', 'w', newline='', encoding=encoding)
    reader = csv.DictReader(csv_read_file)
    writer = csv.writer(csv_write_file)
    writer.writerow(['网站', '时间', '标题', '链接', '内容'])
    junk = csv.writer(csv_junk_file)
    junk.writerow(['网站', '时间', '标题', '链接', '内容'])

    list = []
    for row in reader:
        list.append(row)

    for i in list:
        city = i['网站']
        date = i['时间']
        title = i['标题']
        url = i['链接']
        info = i['内容']
        if filter.main(info) == 1:
            writer.writerow([city, date, title, url, info])
        else:
            junk.writerow([city, date, title, url, info])
            
if __name__=='__main__':
    main()