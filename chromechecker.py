#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from xml.dom.minidom import parseString
from base64 import b64decode
from urllib import request
import sys
import time
import platform

info = {
    "Stable": {
        "x86": "-multi-chrome",
        "x64": "x64-stable-multi-chrome",
        "appid": "{8A69D345-D564-463C-AFF1-A69D9E530F96}"
    },
    "Beta": {
        "x86": "1.1-beta",
        "x64": "x64-beta-multi-chrome",
        "appid": "{8A69D345-D564-463C-AFF1-A69D9E530F96}"
    },
    "Dev": {
        "x86": "2.0-dev",
        "x64": "x64-dev-multi-chrome",
        "appid": "{8A69D345-D564-463C-AFF1-A69D9E530F96}"
    },
    "Canary": {
        "x86": "",
        "x64": "x64-canary",
        "appid": "{4EA16AC7-FD5A-47C3-875B-DBF4A2008C20}"
    }
}

update_url = 'https://tools.google.com/service/update2'

def main():
    print('Chrome开发版本：\n1：Stable\n2：Beta\n3：Dev\n4：Canary')
    chrome = input('请选择Chrome的开发版本（默认为Stable）：')
    if chrome == '':
        chrome = 1
    else:
        chrome = int(chrome)
    if chrome == 1:
        ver = 'Stable'
    elif chrome == 2:
        ver = 'Beta'
    elif chrome == 3:
        ver = 'Dev'
    elif chrome == 4:
        ver = 'Canary'
    else:
        ver = 'Stable'
    print('已选择开发版本：%s' % ver)
    
    if platform.architecture()[0] == '32bit':
        arch = 'x86'
    elif platform.architecture()[0] == '64bit':
        arch = 'x64'
    else:
        print('Chrome编译版本：\n1：x86\n2：x64')
        arch = input('请选择Chrome的编译版本（默认为x86）：')
        if arch == '2' or arch == 'x64' or arch == '64':
            arch = 'x64'
        else:
            arch = 'x86'
    print('已选择编译版本：%s' % arch)
    
    time.sleep(2)

    print('='*20)
    print(ver, arch)
    payload = """<?xml version='1.0' encoding='UTF-8'?>
        <request protocol='3.0' version='1.3.23.9' ismachine='0'
                 installsource='ondemandcheckforupdate' dedup='cr'
                 sessionid='{3597644B-2952-4F92-AE55-D315F45F80A5}'
                 requestid='{CD7523AD-A40D-49F4-AEEF-8C114B804658}'>
        <hw sse='1' sse2='1' sse3='1' ssse3='1' sse41='1' sse42='1' avx='1'/>
        <os platform='win' version='6.3' arch='"""+arch+"""'/>
        <app appid='"""+info[ver]['appid']+"""' ap='"""+info[ver][arch]+"""' brand='GGLS'>
            <updatecheck/>
        </app>
        </request>
    """

    requ = request.Request(url=update_url, data=payload.encode())
    resp = request.urlopen(requ).read().decode('utf-8')
    DOMTree = parseString(resp)
    
    version = ''
    for action in DOMTree.getElementsByTagName('action'):
        if action.getAttribute('run') != '': # kind weird
            name = action.getAttribute('run')
        if action.getAttribute('Version') != '':
            print('version:', action.getAttribute('Version'))
            version = action.getAttribute('Version')

    download_url = []
    for url in DOMTree.getElementsByTagName('url'):
        if url.getAttribute('codebase').startswith('https'):
            print(url.getAttribute('codebase')+name)
            download_url.append(url.getAttribute('codebase')+name)
    chrome_hash = ''
    for package in DOMTree.getElementsByTagName('package'):
        print('size: %.2fMB' %(int(package.getAttribute('size'))/1024/1024))
        print('sha1:', b64decode(package.getAttribute('hash').encode()).hex())
        print('sha256:', package.getAttribute('hash_sha256'))
        chrome_hash = b64decode(package.getAttribute('hash').encode()).hex()
    chrome_info = [download_url, version, chrome_hash]
    return chrome_info

if __name__=='__main__':
    if len(sys.argv)==1:
        main()