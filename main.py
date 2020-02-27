#!/usr/bin/python
# -*- coding: UTF-8 -*-

import requests
import re
import web
import schedule
import threading
from api import Request
from db import DB
from sql import SQL
from proxy import checkDBProxyConnect

#创建一把同步锁
lock = threading.Lock()
# 多线程标记，第一个号码抽到1000M 时标记
a_burning_shame = False
# 用户列表
users = []
# 数据库操作对象
sql_db = {}



class User:
    def __init__(self, user):
        self.user_id = str(user['user_id'])
        self.phone = user['phone']

    def checkUser(self):
        # ret = re.match(r"1[35678]\d{9}", tel)
        # 由于手机号位数大于11位也能匹配成功，所以修改如下：
        return re.match(r"^1[35678]\d{9}$", self.phone)

class Prize:
    def __init__(self, prize):
        if prize['sum_50'] is None:
            self.sum_50 = 0
        else:
            self.sum_50 =  int(prize['sum_50'])
        
        if prize['sum_100'] is None:
            self.sum_100 = 0
        else:
            self.sum_100 = int(prize['sum_100'])
        
        if prize['prize_1000'] is None:
            self.prize_1000 = 0
        else:
            self.prize_1000 = int(prize['prize_1000'])

    # 检查是否超过1000M
    def check_out_of_range(self):
        if self.prize_1000 == 1000:
            return True
        elif self.sum_50 + self.sum_100 >= 1000:
            return True
        else:
            return False




def gg(i):
    global users
    global sql_db
    global a_burning_shame
    user = users[i]
    userObj = User(user)
    isMobile = userObj.checkUser()
    if not(isMobile):
        sql_db.deleteUser(userObj.user_id)

    lock.acquire()
    prize = sql_db.getPrize(userObj.user_id)
    lock.release()
    
    prizeObj = Prize(prize)

    print('手机号:',userObj.phone)

    # 流量>1000M跳过
    if prizeObj.check_out_of_range():
        print('流量>1000M')
        return

    # 进入抽奖页面获取cookie
    reqObj = Request()

    # 设置cookie和用户id
    reqObj.setCookiesAndUserId()

    while True:
        # 结束条件
        if reqObj.count > 2 or not(reqObj.isunicom):
            break
        
        reqObj.mobile = userObj.phone
        # 获取验证码(这里要同步锁)
        lock.acquire()
        code = reqObj.getVerificationCode()
        lock.release()
        reqObj.code = code
        print('验证码:'+code)
        # 设置验证码
        reqObj.setFormData()

        # 验证码验证并获取加密手机号
        encryptionMobile = reqObj.getEncryptionMobile()
        # 验证返回加密手机号
        if isinstance(encryptionMobile, str):
            reqObj.mobile = encryptionMobile
            # 更新表单
            reqObj.setFormData()
            # 抽奖
            prize = reqObj.goodLuck()
            if prize == -1:
                reqObj.isunicom = False

            # 开始放大水，标记，多线程走起
            # 4是1000MB
            elif prize == 3:
                print('---------------------')
                print('号码%s中1000M' % (userObj.phone))
                a_burning_shame = True
                
            lock.acquire()
            sql_db.savePrize(prize, userObj.user_id)
            lock.release()

def out_wit_the_milk():
    global users
    global sql_db
    global a_burning_shame
    with DB(create_db=False) as db:
        sql_db = SQL(db)
        
        users = sql_db.getUsers()
        thread_list = []
        for i in range(len(users)):
            if not(a_burning_shame):
                gg(i)
            else:
                t = threading.Thread(target=gg, args=(i, ))
                t.start()
                thread_list.append(t)
        
        for thread in thread_list:
            t.join()
    print('抽奖结束')
    a_burning_shame = False

if __name__ == '__main__':
    checkDBProxyConnect()
    out_wit_the_milk()


