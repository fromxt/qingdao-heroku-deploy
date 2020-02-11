# coding=utf8

import requests
import time
from http import cookiejar
import pytesseract
from PIL import Image
import os
import json
import time
import re
import web
import schedule

#官网
# url = 'https://m.client.10010.com/sma-lottery/qpactivity/qingpiindex'

# 抽奖接口 post
# 参数:mobile,image(验证码),userid
# luckUrl = 'https://m.client.10010.com/sma-lottery/qpactivity/qpLuckdraw.htm'

# 验证码地址
# https://m.client.10010.com/sma-lottery/qpactivity/getSysManageLoginCode.htm?userid=" + "8F62A3D5E3ED9AF1472CDB071B2BDD63"+"&code=" + new Date().getTime()

# 验证图片地址
# type: "POST",
# url: "/sma-lottery/validation/qpImgValidation.htm",
# data: {
#     'mobile':mobile,
#     'image':imgCode,
#     'userid':'1C8434B91D3F3E02BD634AA11BBA673B'
# },
# 步骤：获取验证码，验证验证码获取加密手机号， 抽奖
fileName = 'phone.txt'
urls = (
    '/qingdao', 'qingdao',
    '/addphone', 'addphone',
    '/removephone', 'removephone'
)

app = web.application(urls, globals())
render = web.template.render('templates/')

# --------------------------------------web--------------------------------

class qingdao:
    def GET(self):
        return render.index()

class addphone:
    def POST(self):
        data = web.input('phone')
        phone = data.phone
        result = writeToFile(phone)
        if result:
            return '添加成功'
        return '手机号已存在'

class removephone:
    def POST(self):
        data = web.input('phone')
        phone = data.phone
        removePhoneByFile(phone)
        return '删除成功'

def removePhoneByFile(phone):
    with open(fileName,"r",encoding="utf-8") as f:
        lines = f.readlines()
        #print(lines)
    with open(fileName,"w",encoding="utf-8") as f_w:
        for line in lines:
            if phone in line.strip():
                continue
            f_w.write(line)

def writeToFile(phone):
    phoneList = readFile()
    for pho in phoneList:
        if pho == phone:
            return False
    file = open(fileName, 'a')
    try:
        file.write(phone + '\n')
        return True
    finally:
        file.close()
    
def readFile():
    phoneList = []
    file = {}
    try:
        file = open(fileName, 'r')
        phones = file.readlines()

        for phone in phones:
            # print(phone.strip())
            phoneList.append(phone.strip())
        return phoneList
    except FileNotFoundError:
        file = open(fileName, mode='w', encoding='utf-8')
        print("文件创建成功！")
        return phoneList
    finally:
        if not(file is None):
            file.close()

# --------------------------------------定时任务--------------------------------
schedule.every().day.at('13:50').do(go)

# --------------------------------------req--------------------------------
class Req():
    def __init__(self):
        self.userid = ''
        self.mobile = ''
        self.sourceMobile = ''
        self.code = ''
        # 官方地址
        self.officialUrl = 'https://m.client.10010.com/sma-lottery/qpactivity/qingpiindex'
        # 验证码获取地址
        self.loginCodeUrl = 'https://m.client.10010.com/sma-lottery/qpactivity/getSysManageLoginCode.htm?userid='
        # 验证码验证
        self.validationUrl = 'https://m.client.10010.com/sma-lottery/validation/qpImgValidation.htm'
        #抽奖地址
        self.luckUrl = 'https://m.client.10010.com/sma-lottery/qpactivity/qpLuckdraw.htm'
        self.headers = {}
        self.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
        self.headers['Content-Type'] = 'application/x-www-form-urlencoded;charset=UTF-8'
        self.headers['Referer'] = 'https://m.client.10010.com/sma-lottery/qpactivity/qingpiindex'
        self.formData = {}
        self.count = 0

    # 获取验证码链接
    def getCodeUrl(self):
        url = self.loginCodeUrl + self.userid + '&'
        t = time.time()
        timestamp = int(round(t * 1000))
        url = url + 'code=' + str(timestamp)
        return url
    
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
    def setCookiesAndUserId(self,resp):
        cookies = requests.utils.dict_from_cookiejar(resp.cookies)
        cookiesValue = ''
        for key in cookies.keys():
            cookiesValue += key + '=' + cookies.get(key) + ';'
            if key == 'JSESSIONID':
                self.userid = cookies.get(key)
                
        self.headers['Cookie'] = cookiesValue

    # 验证码验证
    def vailSubmit(self):
        # self.setFormData(user)
        # self.printReqParam()
        resp = requests.post(self.validationUrl, data=self.formData, headers=self.headers)
        # resp.encoding = 'utf-8'
        print('resp1----------------')
        print(resp.text)
        # b'{"code":"YES","mobile":"aceaf972232b2372d3b8184affa9f367"}'
        jsonObj = json.loads(resp.text)
        return jsonObj

    def goodLuck (self):
        resp = requests.post(self.luckUrl, data=self.formData, headers=self.headers)
        resp.encoding = 'utf-8'
        print('resp2----------------')
        print(resp.text)
        jsonObj = json.loads(resp.text)
        if jsonObj['status'] == 500:
            isunicom = jsonObj['isunicom']
            if not(isunicom):
                print(self.formData['mobile'] + '不是联通手机')
                self.count = 3
                return
            else:
                print('没抽奖次数了哦，改日再战吧!')
                self.count = 3
                return

        elif jsonObj['status'] == 0 or jsonObj['status'] == 200:
            self.count += 1
            data = jsonObj['data']
            prize = switch_id(data['level'])
            print(prize)
        elif jsonObj['status'] == 700:
            print('当前抽奖人数过多，请稍后重试！')

    def setFormData(self):
        self.formData = {
            'mobile': self.mobile,
            'image': self.code,
            'userid': self.userid
        }

    def printReqParam(self):
        print('--------------------------')
        print('userid', self.userid)
        print('code', self.code)
        print('mobile', self.mobile)
        print('sourceMobile', self.sourceMobile)
        print('headers', self.headers)
        print('formData', self.formData)
        print('--------------------------')

class User():
    mobile = ''
    image = ''
    userid = ''
    def __init__(self, mobile, imageCode, userid):
        self.mobile = mobile
        self.image = imageCode
        self.userid = userid
    def printParam(self):
        print('++++++++++++++')
        print(self.mobile)
        print(self.image)
        print(self.userid)
        print('++++++++++++++')
        

def switch_id(id):
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

    def removeThisImg(self):
        path = os.path.abspath('.') + '\\' + self.imgName
        path = path.replace('\\','/')
        print(path)
        os.remove(path)


def getResponse(url):
    response = requests.get(url)
    return response

def checkMobile(mobile):
    # ret = re.match(r"1[35678]\d{9}", tel)
    # 由于手机号位数大于11位也能匹配成功，所以修改如下：
    result = re.match(r"^1[35678]\d{9}$", mobile)
    if result:
        return True
    else:
        print("手机号码错误")
        return False

    
# 获取验证码，验证验证码获取加密手机号， 抽奖

# 获取验证码
def getVerificationCode(reqObj):
    # 请求获取验证码
    codeUrl = reqObj.getCodeUrl()
    print('验证码链接', codeUrl)
    imgResp = getResponse(codeUrl)
    print(imgResp)
    myImage = MyImage('test.png')
    # 转为图片
    imgObj = myImage.saveImage(imgResp)
    # 转为字符串
    code = myImage.imgToString(imgObj)
    if len(code) != 4:
        print('验证码识别失败！重新获取验证码')
        getVerificationCode(reqObj)
    return code

# 验证验证码获取加密手机号
def getEncryptionMobile(reqObj):
    jsonObj = reqObj.vailSubmit()
    # print(jsonObj)
    if jsonObj['code'] == 'YES':
        return jsonObj['mobile']
    elif jsonObj['code'] == 'IMGNULL':
        #刷新验证码
        print('刷新验证码')
        time.sleep(3)
        # code = getVerificationCode(reqObj)
        # reqObj.formData['image'] = code
        # return getEncryptionMobile(reqObj, code)
        return False
    elif jsonObj['code'] == 'IMGERROR':
        # 应该是验证码错误
        return False

def getPhoneList():
    
    return readFile()

def gg(reqObj):
    if(reqObj.count > 2):
        return
    code = getVerificationCode(reqObj)
    reqObj.code = code
    print('验证码:'+code)

    reqObj.setFormData()
    # print(reqObj.printReqParam())

    # 验证码验证并获取加密手机号
    encryptionMobile = getEncryptionMobile(reqObj)
    time.sleep(2)
    if isinstance(encryptionMobile, str):
        reqObj.mobile = encryptionMobile
        reqObj.setFormData()
        # 抽奖
        reqObj.goodLuck()
        reqObj.mobile = reqObj.sourceMobile
        time.sleep(3)
    gg(reqObj)    

def go():
    mobileList = getPhoneList()
    for mobile in mobileList:
        print('手机号', mobile)
        if not(checkMobile(mobile)):
            continue
        reqObj = Req()

        reqObj.mobile = mobile
        reqObj.sourceMobile = mobile

        resp = getResponse(reqObj.officialUrl)

        reqObj.setCookiesAndUserId(resp)

        gg(reqObj)

def main():
    while True:
        # 启动服务
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    app.run()
    main()
    