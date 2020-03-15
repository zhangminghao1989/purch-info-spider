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
    pattern_group = conf.sections()
    for pattern_group_name in pattern_group:
        csv_write_file = './output/' + pattern_group_name + '筛选结果.csv'
        csv_junk_file = './output/' + pattern_group_name + '无用信息.csv'
        csv_write = open(csv_write_file, 'w', newline='', encoding=encoding)
        csv_junk = open(csv_junk_file, 'w', newline='', encoding=encoding)
        writer = csv.writer(csv_write)
        writer.writerow(['网站', '时间', '标题', '链接', '内容'])
        junk = csv.writer(csv_junk)
        junk.writerow(['网站', '时间', '标题', '链接', '内容'])
        csv_read = open('./output/All.csv', 'r', newline='', encoding=encoding)
        reader = csv.DictReader(csv_read)
        list = []
        for row in reader:
            list.append(row)

        for i in list:
            city = i['网站']
            date = i['时间']
            title = i['标题']
            url = i['链接']
            info = i['内容']
            if filter.main(pattern_group_name, info) == 1:
                writer.writerow([city, date, title, url, info])
            else:
                junk.writerow([city, date, title, url, info])
            
if __name__=='__main__':
    main()