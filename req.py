#!/usr/bin/python
# -*- coding: UTF-8 -*-

import requests
import time
from http import cookiejar
import threading

# http请求

# 23点检查数据库的代理ip是否有效
# 设置代理ip的数量，如果ip不够则获取新的代理ip
lock = threading.Lock()
proxies_list = []
proxies = {
#   "http": "http://39.137.69.9:8080",
#   "https": "http://39.137.69.9:8080",
}
index = 0

def setProxie_list(proxiesList):
    global proxies_list
    global proxies
    print('代理ip数量:', len(proxiesList))
    proxies_list = proxiesList
    proxies = proxies_list[0]

def setProxies():
    index += 1
    if (index < len(proxies_list)):
        proxies = proxies_list[index]
    else:
        print('超出范围')

class HTTP():

    def httpGet(self, url):
        global index
        print(proxies)
        response = {}
        try:
            # , proxies=proxies
            response = requests.get(url, proxies=proxies)
        except requests.exceptions.ConnectTimeout:
            print('连接超时')
            time.sleep(2)
            httpGet(url)
        except requests.HTTPError:
            print('http状态码非200')
            time.sleep(2)
            httpGet(url)
        except requests.exceptions.ProxyError:
            # 代理ip无效，更换代理ip
            print('代理ip无效')
            setProxies()
        except Exception as e:
            print('未知错误:', e)
            time.sleep(2)
            httpGet(url)
        else:
            return response

    def checkConnection(self, url, proxies):
        print('检测代理ip', proxies)
        try:
            response = requests.get(url, proxies=proxies, timeout=5)
        except requests.exceptions.ProxyError:
            # 代理ip无效，更换代理ip
            print('代理ip无效')
            return False
        except requests.exceptions.ConnectTimeout:
            print('连接超时')
            return False
        except requests.exceptions.SSLError:
            return False
        else:
            return True
    
    def httpPost(self,url, data, headers):
        response = {}
        print(proxies)
        try:
            # , proxies=proxies
            response = requests.post(url, data=data, headers=headers, proxies=proxies)
        except requests.exceptions.ConnectTimeout:
            print('连接超时')
            time.sleep(2)
            httpPost(url, data, headers)
        except requests.HTTPError:
            print('http状态码非200')
            time.sleep(2)
            httpPost(url, data, headers)
        except requests.exceptions.ProxyError:
            # 代理ip无效，更换代理ip
            print('代理ip无效，正在更换代理ip')
        except Exception as e:
            print('未知错误:', e)
            time.sleep(2)
            httpPost(url, data, headers)
        return response

    # 检测ip是否可用
    def checkProxy(self, ip_prot):
        lock.acquire()
        print('检测ip:',ip_prot)
        proxies = {
            "http": "http://{}".format(ip_prot),
            "https": "http://{}".format(ip_prot)
        }
        url = 'https://m.client.10010.com/sma-lottery/qpactivity/qingpiindex'
        result = self.checkConnection(url, proxies)
        print(result)
        lock.release()
        return result

    def getCookie(self, resp):
        return requests.utils.dict_from_cookiejar(resp.cookies)

# ------------------------------------------------------------------------