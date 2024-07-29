# -*- coding: utf-8 -*-
"""
Created on Sat Mar 23 09:02:52 2024

@author: makej
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd

import time,ddddocr,requests,json,re,json


"获取网页信息"
driver=webdriver.Firefox()
driver.implicitly_wait(5)
url='https://me.sichuanair.com/login.shtml'
driver.get(url)

#等待五秒
#wait = WebDriverWait(driver, 5)
time.sleep(3)
"获取验证码"
#elements_acesscode=driver.find_element(By.ID,'')
elements_acesscode=driver.find_element(By.ID,'img_vcode').screenshot("a.jpg")

ocr = ddddocr.DdddOcr()              # 实例化
with open('a.jpg', 'rb') as f:     # 打开图片
    img_bytes = f.read()             # 读取图片
res = ocr.classification(img_bytes)  # 识别
#print(res)


"输入账号密码进入amro，获取cookies"
elements_acesscode=driver.find_element(By.NAME,'username')
username=input("username:")
elements_acesscode.send_keys(username)

elements_acesscode=driver.find_element(By.NAME,'userPassword')
password=input("password:")
elements_acesscode.send_keys(password)

elements_acesscode=driver.find_element(By.NAME,'vCode')
elements_acesscode.send_keys(res)

elements_but=driver.find_element(By.ID,'btnSubmit').click()

time.sleep(5)
cookies = driver.get_cookies()
driver.close()

"requests使用selenium获取的cookies，来模拟登录获取相关数据"
session=requests.Session()
cookies={cookie['name']: cookie['value'] for cookie in cookies}
headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',}
url_workorder='https://me.sichuanair.com/api/v1/plugins/LM_WORKORDER_LIST'
url_chtl='https://me.sichuanair.com/api/v1/plugins/LM_NRC_CHTL_LIST'
postdata_330={"planstd":"2019-01-04 08:00:00",
            "planend":" 2024-07-29 08:00:00",
            # "ifClose":"",
            # "order":"asc",
            "keyWord":"刹车",
            "keyWordStr":"刹车",
            "actypeStr": "(A330|350)",
            "actype": "A330,A350",
            "page":"1",
            "rows":"9999"}
l=session.post(url_workorder,headers=headers,data=postdata_330,cookies=cookies)
if l.status_code==200:
    json_data=l.content.decode('utf-8')
    data_str=json.loads(json_data)
    data_list=data_str['data']
    whrp_data=[i for i in data_list if re.search('更换',i['MDTITLE_C'])]

else:
    print('no data')


           

# value_data=[]
# def whrp1(i):
#     taskid=i['TASKID']
#     postdata_chtl={"taskid":"{}".format(taskid)}
#     chtl=session.post(url_chtl,headers=headers,data=postdata_chtl,cookies=cookies)
#     if chtl.status_code==200:
#         chtl_data=chtl.content.decode('utf-8')
#         chtl_str=json.loads(chtl_data)
#         if chtl_str['data'] !=[]:
#             chtl_list=chtl_str['data'][0]
#             if 'VPN' in chtl_list:
#                 if re.search('2-1577-9', chtl_list['VPN']):
#                     return i
# whrp=list(filter(whrp1,whrp_data))#筛选更换工作包


"飞机号导入"
with open('fl.json','r') as f:
     fl=json.load(f)

d={'330':{},'350':{}}
for i in fl['330']:#i飞机号
    d['330'][i]=[[],[],[],[],[],[],[],[]] #八个刹车的更换时间的列表
    for j in whrp_data:
        if j['TASKSTS']=='FC':
            if 'ACNO' in j:
                if j['ACNO']==i:
                    cnNumber=['一','二','三','四','五','六','七','八']
                    for k in range(8):#k号刹车
                        pattern='更换.*?({}|{})'.format(k+1,cnNumber[k])
                        if re.search(pattern,j['FK_INFO']):
                            d['330'][i][k].append(j['ACTUEND'][0:10]+j['FK_INFO'])
                

   
for i in fl['350']:#区分飞机号
    d['350'][i]=[[],[],[],[],[],[],[],[]] #八个刹车的更换时间的列表
    for j in whrp_data:
        if j['TASKSTS']=='FC':
            if 'ACNO' in j:
                if j['ACNO']==i:
                    cnNumber=['一','二','三','四','五','六','七','八']
                    for k in range(8):
                        pattern='更换.*?({}|{})'.format(k+1,cnNumber[k])
                        if re.search(pattern,j['FK_INFO']):
                            # print('更换{}号刹车'.format(cnNumber[k]))
                            d['350'][i][k].append(j['ACTUEND'][0:10]+j['FK_INFO'])
            

            
def save_dict(dictionary, file_path):
    with open(file_path, 'w',encoding='utf-8') as file:
        json.dump(dictionary, file,ensure_ascii=False)
        
save_dict(d,'brakes_time.json')
