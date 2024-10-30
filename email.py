# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 09:11:16 2024

@author: makej
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
 
# 第三方 SMTP 服务
mail_host="smtp.126.com"  #设置服务器
mail_user="makejeef"    #用户名
mail_pass="UZNPWbJbgp3KcRfU"   #口令 
 
 
sender = 'makejeef@126.com'
receivers = ['makejeef@gmail.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

message = MIMEMultipart() 
message['From'] = Header("makejeef", 'utf-8')
message['To'] =  Header("测试", 'utf-8')
subject = '轮刹循环'
message['Subject'] = Header(subject, 'utf-8')
 
#邮件正文内容
message.attach(MIMEText('循环', 'plain', 'utf-8'))
# 构造附件1，传送当前目录下的 test.txt 文件
att1 = MIMEText(open('brakes_fl.json', 'rb').read(), 'base64', 'utf-8')
att1["Content-Type"] = 'application/octet-stream'
# 这里的filename可以任意写，写什么名字，邮件中显示什么名字
att1["Content-Disposition"] = 'attachment; filename="brakes_fl.json"'
message.attach(att1)
 
try:
    smtpObj = smtplib.SMTP() 
    smtpObj.connect(mail_host, 25)    # 25 为 SMTP 端口号
    smtpObj.login(mail_user,mail_pass)  
    smtpObj.sendmail(sender, receivers, message.as_string())
    print("邮件发送成功")
except smtplib.SMTPException:
    print ("Error: 无法发送邮件")
