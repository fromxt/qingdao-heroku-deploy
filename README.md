# 青岛流量挂机

官网(https://m.client.10010.com/sma-lottery/qpactivity/qingpiindex)

抽奖接口 post
参数:mobile,image(验证码),userid
luckUrl = https://m.client.10010.com/sma-lottery/qpactivity/qpLuckdraw.htm

验证码地址
https://m.client.10010.com/sma-lottery/qpactivity/getSysManageLoginCode.htm?userid=" + "8F62A3D5E3ED9AF1472CDB071B2BDD63"+"&code=" + new Date().getTime()

使用web.py框架，schedule定时任务，pytesseract识别验证码
需要安装模块:
- requests
- pytesseract
- Pillow
- web
- schedule
- threading

说明:
运行需要安装tesseract-ocr。程序没有使用数据库，仅使用phone.txt记录抽奖情况，phone.back备份文件
准备提供验证码验证接口，只针对[青岛流量](https://m.client.10010.com/sma-lottery/qpactivity/qingpiindex)

# 2-12更新：
### 添加抽奖记录
每一行格式:手机号 50MB累计流量,100MB累计流量,1000MB累计流量,20钻石
### 用户抽到1000MB不在抽奖
月底恢复记录
