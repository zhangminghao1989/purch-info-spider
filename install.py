# -*- coding: utf-8 -*-

'一个招投标网站信息采集工具'
__author__ = 'Zhang Minghao'

print('安装windows系统下运行环境')
import urllib, os, zipfile, hashlib, subprocess, re
from html.parser import HTMLParser
from urllib.request import urlopen, urlretrieve

print('安装第三方库：')
os.system('python -m pip install configparser selenium colorlog')

def versionCompare(v1, v2):
    v1_check = re.match("\d+(\.\d+){0,3}", v1)
    v2_check = re.match("\d+(\.\d+){0,3}", v2)
    if v1_check is None or v2_check is None or v1_check.group() != v1 or v2_check.group() != v2:
        return 2
    v1_list = v1.split(".")
    v2_list = v2.split(".")
    v1_len = len(v1_list)
    v2_len = len(v2_list)
    if v1_len > v2_len:
        for i in range(v1_len - v2_len):
            v2_list.append("0")
    elif v2_len > v1_len:
        for i in range(v2_len - v1_len):
            v1_list.append("0")
    else:
        pass
    for i in range(len(v1_list)):
        if int(v1_list[i]) < int(v2_list[i]):
            return 1
    return 0

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

#检查本地是否存在chromedriver
if os.path.exists('chromedriver.exe'):
    local_version = re.split(' ', subprocess.Popen('chromedriver -v', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.readline().decode('ascii'))[1]
    print('本地chromedriver版本号：' + local_version)
else:
    local_version = '0'
    print('本地缺失chromedriver，尝试自动下载。')
#尝试获取chromedriver最新版本号，获取失败则使用75.0.3770.8
print('尝试获取chromedriver最新版本号：', end='')
try:
    version = urlopen('https://chromedriver.storage.googleapis.com/LATEST_RELEASE').read().decode('utf-8')
except urllib.error.URLError:
    print('\n获取失败，使用', end='')
    version = '75.0.3770.8'
print(version)

check_version = versionCompare(local_version, version)

#driver = input('是否自动下载Chromedriver（Y/N）：')
if check_version == 1:
    print('下载chromedriver')
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
elif check_version == 0:
    print('chromedriver已为最新版本！')
else:
    print('chromedriver版本检查失败，请自行更新！')

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