#!/usr/bin/python
# -*- coding: UTF-8 -*-

# 数据库连接

import pymysql


# ------------------------------------------------------------------------
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

class DB():
    def __init__(self, host=host, port=port, db=db, user=user, passwd=passwd, charset='utf8', create_db = False):
        # 建立连接 
        self.conn = pymysql.connect(host=host, port=port, db=db, user=user, passwd=passwd, charset=charset)
        # 创建游标，操作设置为字典类型        
        self.cur = self.conn.cursor(cursor = pymysql.cursors.DictCursor)
        if create_db:
            self.create_database()
            self.create_table()

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
        self.cur.close()
        # 关闭数据库连接        
        self.conn.close()

    # 创建数据库
    def create_database(self):
        sql = "drop database if exists qingdao"
        self.cur.execute(sql)
        sql = "create database qingdao"
        self.cur.execute(sql)
        

    # 创建表
    def create_table(self):
        sql = "use qingdao"
        self.cur.execute(sql)
        # 用户表
        sql = """ 
            CREATE TABLE `users` (
            `user_id` int(11) NOT NULL AUTO_INCREMENT,
            `phone` varchar(11) NOT NULL,
            `create_date` datetime DEFAULT NULL,
            PRIMARY KEY (`user_id`)
            ) ENGINE=InnoDB AUTO_INCREMENT=725 DEFAULT CHARSET=utf8;
         """
        self.cur.execute(sql)

        # 奖品记录表
        sql = """ 
            CREATE TABLE `prize` (
            `prize_id` int(11) NOT NULL AUTO_INCREMENT,
            `user_id` int(11) NOT NULL,
            `winning_date` datetime DEFAULT NULL,
            `prize_50` int(11) DEFAULT NULL,
            `prize_100` int(11) DEFAULT NULL,
            `prize_1000` int(11) DEFAULT NULL,
            `prize_20` int(11) DEFAULT NULL,
            PRIMARY KEY (`prize_id`),
            KEY `user_id` (`user_id`),
            CONSTRAINT `prize_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
            ) ENGINE=InnoDB AUTO_INCREMENT=135 DEFAULT CHARSET=utf8;
          """
        self.cur.execute(sql)

        # 创建代理表
        sql = """ 
         CREATE TABLE `proxys` (
        `id` int(11) NOT NULL AUTO_INCREMENT,
        `ip` varchar(16) NOT NULL,
        `_port` varchar(5) NOT NULL,
        `anonymity` varchar(10) NOT NULL,
        `response_time` int(11) DEFAULT NULL,
        `create_time` datetime DEFAULT NULL,
        PRIMARY KEY (`id`)
        ) ENGINE=InnoDB AUTO_INCREMENT=135 DEFAULT CHARSET=utf8;
        """
        self.cur.execute(sql)