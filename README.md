# 青岛流量挂机
使用mysql存储数据的自动抽奖脚本

官网(https://m.client.10010.com/sma-lottery/qpactivity/qingpiindex)



# 使用环境：
python3，pip3，mysql

需要安装模块:
```
pip3 install requests
pip3 install pytesseract
pip3 install Pillow
python3 -m pip install web.py==0.40
pip3 install schedule
pip3 install PyMySQL
```

- text2sql.py 用于数据转移

如果以前是使用master或者outwitthemilk分支的脚本，要切换到本版本，则要使用text2sql.py


启动:python3 indexC.py，默认使用8080端口，使用其它端口：python3 indexC.py 端口号

