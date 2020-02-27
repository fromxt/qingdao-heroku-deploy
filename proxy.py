#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2020/2/9 11:04
# @Author : Cdx
# @Site : 测试成功的IP在proxies.txt
# @File : A8.py
# @Software: PyCharm
import re
from concurrent.futures.thread import ThreadPoolExecutor
import requests
from db import DB
from sql import SQL
import datetime
import json
from req import HTTP
from req import setProxie_list


# 每晚11点检测ip代理

T_SIZE=10   #线程池的线程数量
IP_SIZE=100     #需要测试ip的数量
n=1     #n=0测试https，等于其他是测试http
IP_LIST = []
# 超时多少毫秒则丢弃
delayed = 500
# 代理IP最小数量
minCount = 0

'''获取ip组'''
def get_ip(i):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0",
        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive"
    }
    r = requests.get('http://www.89ip.cn/tqdl.html?num={}&address=&kill_address=&port=&kill_port=&isp='.format(i),
                     headers=headers)
    # result = re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", r.text)
    result = re.findall(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}:[0-9]{2,4}", r.text)
    return result

'''测试'''
def check(ip_prot):
    try:
        if(n==0):
            requests.get('https://www.douban.com/', proxies={"https":ip_prot}, timeout=5)
        else:
            requests.get('http://www.baidu.com/', proxies={"http": ip_prot}, timeout=5)
    except:
        print('{}失败'.format(ip_prot))
        return None
    else:
        print('{}----------------------->成功'.format(ip_prot))
        return ip_prot

# 检测连通性
def connectivity(IP_LIST):
    proxy_count = 0
    url = 'http://www.moguproxy.com/proxy/checkIp/ipList?'
    # 拼接参数s
    for ip_prot in IP_LIST:
        url = url + 'ip_ports[]=' + ip_prot + '&'
    try:
        print(url)
        resp = requests.get(url)
    except Exception as e:
        print('未知错误!')
        return 0
    else:
        jsonObj = json.loads(resp.text)
        print(jsonObj)
        if jsonObj['code'] == '0':
            with DB(create_db=False) as db:
                josnList = jsonObj['msg']
                http = HTTP()
                for data in josnList:
                    print(data)

                    if 'time' in data and int(data['time'].replace('ms','')) < 500:
                        # 高匿不要
                        # if data['anony'] == '高匿':
                            # continue
                        # 检测是否可用
                        if not(http.checkProxy(ip_prot)):
                            print('无效')
                            continue
                        
                        # 可用则存数据库
                        create_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        ip = data['ip']
                        port = data['port']
                        anonymity = data['anony']
                        response_time = int(data['time'].replace('ms',''))

                        sql = 'insert into proxys(ip,_port,anonymity,response_time,create_time) \
                                values("%s","%s","%s",%d,str_to_date(\"%s\","%%Y-%%m-%%d %%H:%%i:%%s"))' % (ip,port, anonymity, response_time, create_time)
                        # print(sql)
                        db.execute(sql)
                        proxy_count += 1
        return proxy_count

# 获取新的代理
def getNewProxy():
    executor = ThreadPoolExecutor(max_workers=T_SIZE)  # 线程池数量
    ips = get_ip(IP_SIZE)
    # for i in range(len(ips)):
    #     executor.submit(check, ips[i], n)
    # all_task = [executor.submit(check, (ip,n)) for ip in ips)]
    for data in executor.map(check, ips):
        if not(data is None):
            IP_LIST.append(data)
    print(IP_LIST)
    return connectivity(IP_LIST)

def checkDBProxyConnect():
    with DB(create_db=False) as db:
        sql = SQL(db)
        # 可用数量
        count = 0
        proxy_list = sql.get_ip_ports()
        http = HTTP()
        for proxy in proxy_list:
            ip_port = "{}:{}".format(proxy['ip'],proxy['_port'])
            if not(http.checkProxy(ip_port)):
               sql.deleteProxy(proxy['id'])
            else:
                count += 1
        print(count)

        # 如果代理ip不够，则获取新的代理ip
        if (count <= minCount):
            proxy_count = getNewProxy()
            print('可用代理ip数量:',count + proxy_count)
            if count+proxy_count == 0:
                checkDBProxyConnect()
            
        proxy_list = sql.getProxy()
        print('proxy_list')
        setProxie_list(proxy_list)


