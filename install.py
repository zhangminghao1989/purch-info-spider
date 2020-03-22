# -*- coding: utf-8 -*-

'一个招投标网站信息采集工具'
__author__ = 'Zhang Minghao'

print('安装windows系统下运行环境')
import urllib, os, zipfile, hashlib, subprocess, re, json, platform
from html.parser import HTMLParser
from urllib.request import urlopen, urlretrieve

print('安装第三方库：')
os.system('python -m pip install --upgrade pip')
os.system('python -m pip install -U configparser selenium colorlog')

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
        try:
            urlretrieve(download_url[i], chrome_version+'_chrome_installer.exe', cbk)
            print('\nChrome安装包下载完成，请自行安装！')
        except:
            print('下载失败，请手动下载安装。\n' + download_url[i])

proxy = input('设置http代理（可选）：')
if proxy != '':
    os.environ['http_proxy'] = proxy
    os.environ['https_proxy'] = proxy

#读取配置文件中设置使用的浏览器
import config_load
conf = config_load.load_conf()
chosen_webdriver = conf.get('DEFAULT', 'webdriver')

#检查操作系统，windows系统可以自动下载webdriver
if platform.system() == 'Windows':
    if chosen_webdriver == 'Chrome':
        print('配置为使用Chrome浏览器。')
        #检查本地是否存在chromedriver
        if os.path.exists('chromedriver.exe'):
            local_version = re.split(' ', subprocess.Popen('chromedriver -v', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.readline().decode('ascii'))[1]
            print('本地chromedriver版本号：' + local_version)
        else:
            local_version = '0'
            print('本地缺失chromedriver，尝试自动下载。')
        #尝试获取chromedriver最新版本号，获取失败则使用80.0.3987.106
        print('尝试获取chromedriver最新版本号：', end='')
        try:
            version = urlopen('https://chromedriver.storage.googleapis.com/LATEST_RELEASE').read().decode('utf-8')
        except urllib.error.URLError:
            print('\n获取失败，使用', end='')
            version = '80.0.3987.106'
        print(version)
        
        check_version = versionCompare(local_version, version)
        
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
            print('chromedriver版本检查失败，请自行更新！http://chromedriver.storage.googleapis.com/index.html')
        
        #下载Chrome浏览器安装包
        chrome = input('是否下载Chrome浏览器安装包（Y/N）：')
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
    elif chosen_webdriver == 'Firefox':
        print('配置为使用Firefox浏览器。')
        #检查本地是否存在geckodriver
        if os.path.exists('geckodriver.exe'):
            local_version = re.split(' ', subprocess.Popen('geckodriver -V', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.readline().decode('ascii'))[1]
            print('本地geckodriver版本号：' + local_version)
        else:
            local_version = '0'
            print('本地缺失geckodriver，尝试自动下载。')
        #尝试获取geckodriver最新版本号，获取失败则使用0.26.0
        print('尝试获取geckodriver最新版本号：', end='')
        try:
            version = json.loads(urlopen('https://api.github.com/repos/mozilla/geckodriver/releases/latest').read())["tag_name"].replace('v', '')
        except urllib.error.URLError:
            print('\n获取失败，使用', end='')
            version = '0.26.0'
        print(version)
        
        check_version = versionCompare(local_version, version)
        
        if platform.architecture()[0] == '32bit':
            arch = 'x86'
        elif platform.architecture()[0] == '64bit':
            arch = 'x64'
        else:
            print('Chrome编译版本：\n1：win32\n2：win64')
            arch = input('请选择geckodriver的编译版本（默认为x86）：')
            if arch == '2' or arch == 'x64' or arch == '64':
                arch = 'win64'
            else:
                arch = 'win32'
        print('已选择编译版本：%s' % arch)
            
        if check_version == 1:
            print('下载geckodriver')
            #下载geckodriver并解压缩到当前目录
            url = f'https://github.com/mozilla/geckodriver/releases/download/v{version}/geckodriver-v{version}-{arch}.zip'
            try:
                urlretrieve(url, 'geckodriver.zip', cbk)
            except:
                print('下载失败，请手动下载并解压。\n' + url)
            if os.path.exists('geckodriver.zip'):
                zip_file = zipfile.ZipFile('geckodriver.zip')
                print('\ngeckodriver下载完成！')
                for names in zip_file.namelist():
                    zip_file.extract(names)
                zip_file.close()
                os.remove('geckodriver.zip')
        elif check_version == 0:
            print('geckodriver已为最新版本！')
        else:
            print('geckodriver版本检查失败，请自行更新！https://github.com/mozilla/geckodriver/releases/latest')
        
        #下载Firefox浏览器安祖航宝
        firefox = input('是否下载Firefox浏览器（Y/N）：')
        if firefox == 'Y' or firefox == 'y':
            if arch != 'win64':
                arch = 'win'
            url = f'https://download.mozilla.org/?product=firefox-latest-ssl&os={arch}&lang=zh-CN'
            try:
                urlretrieve(url, 'Firefox Setup.exe', cbk)
                print('Firefox安装包下载完成，请自行安装！')
            except:
                print('下载失败，请手动下载并安装。https://www.mozilla.org/zh-CN/firefox/download/thanks/')
            
    else:
        print('webdriver配置错误，请在spider.conf配置文件中配置webdriver参数，可选参数为Chrome和Firefox，注意大小写！')
    
else:
    print('Linux操作系统请自行下载webdriver和浏览器。')
    print('chromedriver：http://chromedriver.storage.googleapis.com/index.html')
    print('geckodriver：https://github.com/mozilla/geckodriver/releases/latest')
