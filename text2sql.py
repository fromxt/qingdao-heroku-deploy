#!/usr/bin/python
# -*- coding: UTF-8 -*-

""" 说明：
以前的版本(master、outwitthemilk)使用文本方式储存数据，使得数据容易丢失。而这次使用的是mysql方式存储数据
本脚本是把文本存储的手机号转移到MySQL数据库
本分支：sql
需要修改的地方：
fileName(存储手机号的文件名)
数据库用户名和密码
testCount可以不管
"""

import datetime
from db import DB



# ------------------------------------------------------------------------
# 需要修改的地方

# 存储手机号码的文本文件名
fileName = 'phone2.txt'
# 数据库主机ip
host='localhost'
# 数据库端口
port=3306
# 数据库名
db='qingdao'
# 数据库登录用户名
user='root'
# 数据库登录密码
passwd='1108'
# ------------------------------------------------------------------------

# 测试手机号，比如 1 则在原来的手机号上+1，用来测试抽奖，从而不影响原来的手机号的抽奖次数
# 0则是原来手机号 phone = phone + testCount
testCount = 2


# ------------------------------------------------------------------------------



class Record():
    phone = ''
    prizeList = []
    prize = 0
    prize_50 = 0
    prize_100 = 0
    prize_1000 = 0     
    isunicom = True

    def setAttribute(self,line):
        # line既一行，存放手机号和奖品记录
        # 手机号 50MB累计流量,100MB累计流量,1000MB累计流量,20钻石
        record = line.split(' ')
        self.phone = record[0].strip()
        strArr = record[1].strip().split(',')
        # 将字符串转成数组
        prizeList = list(map(int, strArr))
        self.prizeList = prizeList
        self.prize_1000 = int(prizeList[2])
        self.prize_50 = int(prizeList[0])
        self.prize_100 = int(prizeList[1])



def job():
    global testCount
    with open(fileName,"r",encoding="utf-8") as f, DB(create_db=True) as db:
        lines = f.readlines()
        for line in lines:
            record = Record()
            record.setAttribute(line)
            phone = record.phone
            phone = int(phone)
            phone = phone + testCount
            prize_50 = record.prize_50
            prize_100 = record.prize_100
            prize_1000 = record.prize_1000
            sql = 'insert into users (phone) values(' + str(phone) +')'
            db.execute(sql)
            user_id = db.lastrowid
            if not(prize_1000 == 0):
                now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                sql = 'insert into prize(user_id,winning_date, prize_1000) values(' + str(user_id) + ',"' + now + '",' + str(prize_1000) + ')'
                db.execute(sql)
        print('success')
 


if __name__ == '__main__':
    job()