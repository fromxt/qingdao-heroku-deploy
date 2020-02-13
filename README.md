# 青岛流量挂机

官网(https://m.client.10010.com/sma-lottery/qpactivity/qingpiindex)

抽奖接口 post
参数:mobile,image(验证码),userid
luckUrl = https://m.client.10010.com/sma-lottery/qpactivity/qpLuckdraw.htm

验证码地址
https://m.client.10010.com/sma-lottery/qpactivity/getSysManageLoginCode.htm?userid=" + "8F62A3D5E3ED9AF1472CDB071B2BDD63"+"&code=" + new Date().getTime()


验证码验证接口: http://47.94.234.77:9527/getCode
 
只针对[青岛流量](https://m.client.10010.com/sma-lottery/qpactivity/qingpiindex)。其它网站的验证码均不能识别。

安装依赖：
```
pip install requests

# 安装web.py
# Python 2.7使用
pip2 install web.py==0.40
# Python 3使用
python3 -m pip install web.py==0.40

pip install schedule
```
启动:python indexC.py，默认使用8080端口，使用其它端口：python indexC.py 端口号

# 2-12更新：
添加抽奖记录日志（phone.txt）
每一行格式:手机号 50MB累计流量,100MB累计流量,1000MB累计流量,20钻石

用户抽到1000MB不再抽奖
月底恢复记录

# 2-13更新：
连续stopCount次不中奖停止抽奖