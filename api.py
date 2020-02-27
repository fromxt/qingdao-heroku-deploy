#!/usr/bin/python
# -*- coding: UTF-8 -*-


from myimg import MyImage
import json
from sql import SQL
from req import HTTP
import time

class Request():
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
        self.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
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
        self.http = HTTP()

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
        imgResp = self.http.httpGet(codeUrl)
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
        resp = self.http.httpGet(self.officialUrl)
        cookies = self.http.getCookie(resp)
        cookiesValue = ''
        for key in cookies.keys():
            cookiesValue += key + '=' + cookies.get(key) + ';'
            if key == 'JSESSIONID':
                self.userid = cookies.get(key)
                
        self.headers['Cookie'] = cookiesValue


    # 验证验证码获取加密手机号
    def getEncryptionMobile(self):
        resp = self.http.httpPost(self.validationUrl, data=self.formData, headers=self.headers)
        jsonObj = json.loads(resp.text)
        # print(jsonObj)
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
        resp = self.http.httpPost(self.luckUrl, data=self.formData, headers=self.headers)
        resp.encoding = 'utf-8'
        jsonObj = json.loads(resp.text)
        print(jsonObj)
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
        
        # 好像是被拉黑
        elif jsonObj['status'] == 300:
            self.count += 1
    # 设置表单
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
