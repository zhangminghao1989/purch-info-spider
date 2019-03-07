# -*- coding: utf-8 -*-

'一个招投标网站信息采集工具'
__author__ = 'Zhang Minghao'

print('安装windows系统下运行环境')
import urllib, os, zipfile, hashlib
from html.parser import HTMLParser
from urllib.request import urlopen, urlretrieve

print('安装第三方库：')
os.system('python -m pip install configparser selenium')

def cbk(a,b,c):  
    '''''回调函数 
    @a:已经下载的数据块 
    @b:数据块的大小 
    @c:远程文件的大小 
    '''  
    per=100.0*a*b/c  
    if per>100:  
        per=100  
    print('下载进度：%.2f%%' % per, end='\r')
    
proxy = input('设置http代理（可选）：')
if proxy != '':
    os.environ['http_proxy'] = proxy
    os.environ['https_proxy'] = proxy

driver = input('是否自动下载Chromedriver（Y/N）：')
if driver == 'Y' or driver == 'y':
    print('下载chromedriver')
    #尝试获取chromedriver最新版本号，获取失败则使用2.43
    print('获取chromedriver最新版本号：', end='')
    try:
        version = urlopen('https://chromedriver.storage.googleapis.com/LATEST_RELEASE').read().decode('utf-8')
    except urllib.error.URLError:
        print('获取失败，使用', end='')
        version = '2.43'
    print(version)

    #下载chromedriver并解压缩到当前目录
    url = 'https://chromedriver.storage.googleapis.com/%s/chromedriver_win32.zip' % version
    try:
        urlretrieve(url, 'chromedriver_win32.zip', cbk)
    except:
        print('下载失败，请手动下载并解压。\n' + url)
    if os.path.exists('chromedriver_win32.zip'):
        zip_file = zipfile.ZipFile('chromedriver_win32.zip')
        print('\nchromedriver下载完成！')
        for names in zip_file.namelist():
            zip_file.extract(names)
        zip_file.close()
        os.remove('chromedriver_win32.zip')

def CalcSha1(filepath):
    with open(filepath,'rb') as f:
        sha1obj = hashlib.sha1()
        sha1obj.update(f.read())
        hash = sha1obj.hexdigest()
    return hash

def download_chrome(chrome_version, download_url):
    for i in range(len(download_url)):
        if os.path.exists(chrome_version+'_chrome_installer.exe'):
            break
        urlretrieve(download_url[i], chrome_version+'_chrome_installer.exe', cbk)
        print('\nChrome安装包下载完成，请自行安装！')


chrome = input('是否自动下载Chrome浏览器（Y/N）：')
if chrome == 'Y' or chrome == 'y':
    import chromechecker
    chrome_info = chromechecker.main()
    download_url = chrome_info[0]
    chrome_version = chrome_info[1]
    chrome_hash = chrome_info[2]
    if os.path.exists(chrome_version+'_chrome_installer.exe'):
        file_hash = CalcSha1(chrome_version+'_chrome_installer.exe')
        if file_hash != chrome_hash:
            os.remove(chrome_version+'_chrome_installer.exe')
            download_chrome(chrome_version, download_url)
    else:
        download_chrome(chrome_version, download_url)