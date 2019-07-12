# purch-info-spider
purchasing information spider

该项目为`招标信息网站`信息采集工具。
采集到的信息保存在`output`文件夹内，每个网站按配置文件中的网站名称单独保存，所有信息会同步储存在`All.csv`文件中。
支持设置关键词进行信息筛选并保存在`筛选结果.csv`文件中。

## 开发环境
Python 3.7.1

## 使用的第三方库
configparser
selenium

## 其他需求
chromedriver  +  chrome
或
geckodriver  + firefox

可使用install.py脚本自动下载最新版本chromedriver。
webdriver版本需与浏览器版本一致。

## 使用方法
在spider.conf文件中配置抓取规则后执行`python spider.py`即可

可使用`python spider.py n`的方式单独抓取配置文件中的网站，n为配置文件中网站的顺序号，从0开始计算。
