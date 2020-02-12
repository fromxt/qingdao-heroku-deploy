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
测试环境：python3。

程序没有使用数据库，仅使用phone.txt记录抽奖情况，phone.back备份文件。

index.py为原版，运行需要安装[tesseract-ocr](https://digi.bib.uni-mannheim.de/tesseract/)。indexC.py改为调用接口获取验证码，无需安装tesseract-ocr。
具体请看[indexC.py](https://github.com/teenyda/qingdao/blob/master/indexC.py)

验证码验证接口: http://47.94.234.77:9527/getCode

只针对[青岛流量](https://m.client.10010.com/sma-lottery/qpactivity/qingpiindex)。其它网站的验证码均不能识别。

请求方法:POST<br />
请求参数 FormData = {url: 验证码地址}<br />
返回参数：验证码<br />
indexC.py已经写好，可以直接使用<br />
启动:python indexC.py，默认使用8080端口，使用其它端口：python indexC.py 端口号

# 2-12更新：
### 添加抽奖记录日志（phone.txt）
每一行格式:手机号 50MB累计流量,100MB累计流量,1000MB累计流量,20钻石
### 用户抽到1000MB不再抽奖
月底恢复记录
