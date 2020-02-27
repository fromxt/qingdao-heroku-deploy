#!/usr/bin/python
# -*- coding: UTF-8 -*-

import pymysql
import requests
import time
from http import cookiejar
import pytesseract
from PIL import Image
import os
from pathlib import Path
import json
import time
import datetime
import re
import web
import schedule
import threading

#创建一把同步锁
lock = threading.Lock()
# 多线程标记，第一个号码抽到1000M 时标记
a_burning_shame = False
users = []
sql_db = {}

# -------------------------------------http-------------------------------
def httpGet(url):
    response = {}
    try:
        response = requests.get(url)
    except requests.exceptions.ConnectTimeout:
        print('连接超时')
        time.sleep(2)
        httpGet(url)
    except requests.HTTPError:
        print('http状态码非200')
        time.sleep(2)
        httpGet(url)
    except Exception as e:
        print('未知错误:', e)
        time.sleep(2)
        httpGet(url)
    return response

def httpPost(url, data, headers):
    response = {}
    try:
        response = requests.post(url, data=data, headers=headers)
    except requests.exceptions.ConnectTimeout:
        print('连接超时')
        time.sleep(2)
        httpPost(url, data, headers)
    except requests.HTTPError:
        print('http状态码非200')
        time.sleep(2)
        httpPost(url, data, headers)
    except Exception as e:
        print('未知错误:', e)
        time.sleep(2)
        httpPost(url, data, headers)
    return response
# ------------------------------------------------------------------------

# --------------------------------------class req--------------------------------
class Req():
    def __init__(self):
        self.userid = ''
        self.mobile = ''
        self.code = ''
        # 是否是联通手机
        self.isunicom = True
        # 官方地址
        self.officialUrl = 'https://m.client.10010.com/sma-lottery/qpactivity/qingpiindex'
        # 验证码获取地址
        self.loginCodeUrl = 'https://m.client.10010.com/sma-lottery/qpactivity/getSysManageLoginCode.htm?userid='
        # 验证码验证
        self.validationUrl = 'https://m.client.10010.com/sma-lottery/validation/qpImgValidation.htm'
        #抽奖地址
        self.luckUrl = 'https://m.client.10010.com/sma-lottery/qpactivity/qpLuckdraw.htm'
        self.headers = {}
        self.headers['Accept'] = 'application/json, text/javascript, */*; q=0.01'
        self.headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.89 Safari/537.36'
        self.headers['Content-Type'] = 'application/x-www-form-urlencoded;charset=UTF-8'
        self.headers['Referer'] = 'https://m.client.10010.com/sma-lottery/qpactivity/qingpiindex'
        self.headers['Host'] = 'm.client.10010.com'
        self.headers['Origin'] = 'https://m.client.10010.com'
        self.headers['Sec-Fetch-Mode'] = 'cors'
        self.headers['Sec-Fetch-Site'] = 'same-origin'
        self.headers['X-Requested-With'] = 'XMLHttpRequest'
        self.formData = {}
        # 抽奖此时
        self.count = 0

    # 获取验证码链接
    def getCodeUrl(self):
        url = self.loginCodeUrl + self.userid + '&'
        t = time.time()
        timestamp = int(round(t * 1000))
        url = url + 'code=' + str(timestamp)
        return url

    # 获取验证码
    def getVerificationCode(self):
        # 请求获取验证码
        codeUrl = self.getCodeUrl()
        imgResp = httpGet(codeUrl)
        myImage = MyImage('%s.png' % (self.mobile))
        # 转为图片
        imgObj = myImage.saveImage(imgResp)
        # 转为字符串
        code = myImage.imgToString(imgObj)
        if len(code) != 4:
            print('验证码识别失败！重新获取验证码')
            self.getVerificationCode()
        myImage.removeThisImg()
        return code
    
    # 获取官方网
    def getOfficialUrl(self):
        return self.officialUrl
    
    # 验证码验证地址
    def getVaildationUrl(self):
        return self.validationUrl
    
    # 抽奖地址
    def getLuckUrl(self):
        return self.luckUrl

    # 获取cookies
    def setCookiesAndUserId(self):
        resp = httpGet(self.officialUrl)
        cookies = requests.utils.dict_from_cookiejar(resp.cookies)
        cookiesValue = ''
        for key in cookies.keys():
            cookiesValue += key + '=' + cookies.get(key) + ';'
            if key == 'JSESSIONID':
                self.userid = cookies.get(key)
                
        self.headers['Cookie'] = cookiesValue


    # 验证验证码获取加密手机号
    def getEncryptionMobile(self):
        resp = httpPost(self.validationUrl, data=self.formData, headers=self.headers)
        jsonObj = json.loads(resp.text)
        if jsonObj['code'] == 'YES':
            return jsonObj['mobile']
        elif jsonObj['code'] == 'IMGNULL':
            #刷新验证码
            print('刷新验证码')
            return False
        elif jsonObj['code'] == 'IMGERROR':
            # 验证码错误
            return False

    # return 返回
    # -3 已抽完
    # -2 不是联通号码
    # -1 没中奖
    # 0 50MB
    # 1 100MB
    # 2 1000MB
    # 3 20砖石
    def goodLuck(self):
        resp = httpPost(self.luckUrl, data=self.formData, headers=self.headers)
        resp.encoding = 'utf-8'
        jsonObj = json.loads(resp.text)
        if jsonObj['status'] == 500:
            isunicom = jsonObj['isunicom']
            if not(isunicom):
                print(self.formData['mobile'] + '不是联通手机')
                self.count = 3
                return -1
            else:
                print('没抽奖次数了哦，改日再战吧!')
                self.count = 3
                return 0

        elif jsonObj['status'] == 0 or jsonObj['status'] == 200:
            self.count += 1
            data = jsonObj['data']
            level = data['level']
            prize = self.switch_id(level)
            print(prize)
            return int(level)
        elif jsonObj['status'] == 700:
            print('当前抽奖人数过多，请稍后重试！')

    def setFormData(self):
        self.formData = {
            'mobile': self.mobile,
            'image': self.code,
            'userid': self.userid
        }


    def switch_id(self,id):
        switcher = {
            '1': '50MB',
            '2': '100MB',
            '3': '幸运奖',
            '4': '1000MB',
            '5': '20钻石',
            '6': '15yuan',
            '7': '50yuan'
        }
        return switcher.get(id)

class DB():
    def __init__(self, host='localhost', port=3306, db='qingdao', user='root', passwd='1108', charset='utf8'):
        # 建立连接 
        self.conn = pymysql.connect(host=host, port=port, db=db, user=user, passwd=passwd, charset=charset)
        # 创建游标，操作设置为字典类型        
        self.cur = self.conn.cursor(cursor = pymysql.cursors.DictCursor)

    """ 
    在python中实现了__enter__和__exit__方法，即支持上下文管理器协议。
    上下文管理器就是支持上下文管理器协议的对象，它是为了with而生。
    当with语句在开始运行时，会在上下文管理器对象上调用 __enter__ 方法。
    with语句运行结束后，会在上下文管理器对象上调用 __exit__ 方法
     """
    def __enter__(self):
        # 返回游标        
        return self.cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 提交数据库并执行        
        self.conn.commit()
        # 关闭游标        
        # self.cur.close()
        # 关闭数据库连接        
        # self.conn.close()

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


class SQL:
    def __init__(self, db):
        self.sql_db = db

    def getUsers(self):
        self.sql_db.execute('select * from users ORDER BY user_id DESC')
        return self.sql_db.fetchall()

    def getPrize(self, user_id):
        sql = "SELECT \
        user_id, \
        prize_id, \
        SUM(prize_50) as sum_50, \
        SUM(prize_100) as sum_100, \
        prize_1000 \
        FROM prize WHERE user_id = %s and DATE_FORMAT( winning_date, '%%Y%%m' ) = DATE_FORMAT( CURDATE() , '%%Y%%m')" % (user_id)

        self.sql_db.execute(sql)
        return self.sql_db.fetchone()

    def deleteUser(self, user_id):
        # 手机号码错误将移除
        sql = 'delete from prize where user_id = ' + user_id
        self.sql_db.execute(sql)
        sql = 'delete from users where user_id = ' + user_id
        self.sql_db.execute(sql)

        # 记录一下
    def savePrize(self, prize, user_id):
        # -1 不是联通号码,移除
        # 0 无抽奖次数
        # 1 50MB
        # 2 100MB
        # 3 幸运奖
        # 4 1000MB
        # 5 20钻石
        # 6 15yuan
        lock.acquire()
        sql = ''
        dateStr = getDate()
        executeCommand = True
        if prize == -1:
            sql = 'delete from users where user_id = ' + user_id
        elif prize == 1:
            sql = 'insert into prize(user_id, winning_date, prize_50) values(%s, %s, %d)' % (user_id, dateStr, 50)
        elif prize == 2:
            sql = 'insert into prize(user_id, winning_date, prize_100) values(%s, %s, %d)' % (user_id, dateStr, 100)
        elif prize == 4:
            sql = 'insert into prize(user_id, winning_date, prize_1000) values(%s, %s, %d)' % (user_id, dateStr, 1000)
        elif prize == 5:
            sql = 'insert into prize(user_id, winning_date, prize_20) values(%s, %s, %d)' % (user_id, dateStr, 20)
        else:
            executeCommand = False

        if executeCommand:
            self.sql_db.execute(sql)
        lock.release()

# --------------------------------------class image--------------------------------
class MyImage():
    imgName = ''
    imgPath = ''
    def __init__(self, imgName):
        self.imgName = imgName
    
    def saveImage(self, res):
        with open(self.imgName, 'wb') as file:
            for data in res.iter_content(128):
                file.write(data)
        img = Image.open(self.imgName)
        return img
    # 使用pytesseract识别图片
    # 先去除干扰线，再把背景变透明
    def imgToString(self,img):
        img = img.convert('RGBA')
        pixdata = img.load()
        for y in range(img.size[1]):
            for x in range(img.size[0]):
                if pixdata[x,y][0] == pixdata[x,y][1] and pixdata[x,y][0] == pixdata[x,y][3]:
                    pixdata[x, y] = (255, 255, 255,0)
                if pixdata[x,y][0] > 80 and pixdata[x,y][0] <= 220  and pixdata[x,y][1] > 80 and pixdata[x,y][1] <= 220 and pixdata[x,y][2] > 80 and pixdata[x,y][2]< 220:
                    pixdata[x, y] = (255, 255, 255,0)
        return pytesseract.image_to_string(img)
    # 删除图片
    def removeThisImg(self):
        path = os.path.abspath('.') + '\\' + self.imgName
        path = path.replace('\\','/')
        # print(path)
        my_file = Path(path)
        if my_file.exists():
            os.remove(path)



def getDate():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


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
        return

    # 进入抽奖页面获取cookie
    reqObj = Req()

    # 设置cookie和用户id
    reqObj.setCookiesAndUserId()

    while True:
        # 结束条件
        if reqObj.count > 2 or not(reqObj.isunicom):
            break
        
        reqObj.mobile = userObj.phone
        # 获取验证码
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
            elif prize == 3:
                a_burning_shame = True

            sql_db.savePrize(prize, userObj.user_id)

def out_wit_the_milk():
    global users
    global sql_db
    global a_burning_shame
    with DB() as db:
        sql_db = SQL(db)
        users = sql_db.getUsers()
        thread_list = []
        for i in range(len(users)):
            print(a_burning_shame)
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
    out_wit_the_milk()


