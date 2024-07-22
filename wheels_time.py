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
elements_acesscode.send_keys('018608')

elements_acesscode=driver.find_element(By.NAME,'userPassword')
elements_acesscode.send_keys('')

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
postdata_330={"planstd":"2019-01-04 08:00:00",
            "planend":" 2024-04-05 08:00:00",
            # "ifClose":"",
            # "order":"asc",
            "keyWord":"主轮",
            "keyWordStr":"主轮",
            "actypeStr": "(A330|350)",
            "actype": "A330,A350",
            "page":"1",
            "rows":"9999"}
l=session.post(url_workorder,headers=headers,data=postdata_330,cookies=cookies)
if l.status_code==200:
    json_data=l.content.decode('utf-8')
    data_str=json.loads(json_data)
    data_list=data_str['data']
    def whrp1(d):
        if 'FK_INFO' in d:
            if re.search('更换',d['FK_INFO']):
                return d
    def whrp2(d):
        if 'ATA' in d:
            if d['ATA'][0:5]=='32-41':
                return d
    
        
    whrp=list(filter(whrp1,data_list))#筛选更换工作包
    whrp_data=list(filter(whrp2,whrp))#筛选章节号‘32-41’工作包

    
else:
    print('no data')
    
    

with open('fl.json','r') as f:
     fl=json.load(f)

d={'330':{},'350':{}}
for i in fl['330']:#i飞机号
    d['330'][i]=[[],[],[],[],[],[],[],[]] #八个轮子的更换时间的列表
    for j in whrp_data:
        if j['TASKSTS']=='FC':
            if j['ACNO']==i:
                cnNumber=['一','二','三','四','五','六','七','八']
                for k in range(8):#k号主轮
                    pattern='更换.*?({}|{})'.format(k+1,cnNumber[k])
                    if re.search(pattern,j['FK_INFO']):
                        d['330'][i][k].append(j['ACTUEND'][0:10]+j['FK_INFO'])

   
for i in fl['350']:#区分飞机号
    d['350'][i]=[[],[],[],[],[],[],[],[]] #八个轮子的更换时间的列表
    for j in whrp_data:
        if j['ACNO']==i:
            if j['TASKSTS']=='FC':
                if j['ACNO']==i:
                    cnNumber=['一','二','三','四','五','六','七','八']
                    for k in range(8):
                        pattern='更换.*?({}|{})'.format(k+1,cnNumber[k])
                        if re.search(pattern,j['FK_INFO']):
                            # print('更换{}号主轮'.format(cnNumber[k]))
                            d['350'][i][k].append(j['ACTUEND'][0:10]+j['FK_INFO'])
                

def save_dict(dictionary, file_path):
    with open(file_path, 'w',encoding='utf-8') as file:
        json.dump(dictionary, file,ensure_ascii=False)
        
save_dict(d,'wheels_time.json')
