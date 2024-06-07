# -*- coding: utf-8 -*-
"""
Created on Sat Mar 23 09:02:52 2024

@author: makej
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd

import time,ddddocr,requests,json,csv,re,json


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
elements_acesscode.send_keys('7400233@scal')

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
            "actypeStr": "(A330)",
            "actype": "330",
            "page":"1",
            "rows":"9999"}
l_330=session.post(url_workorder,headers=headers,data=postdata_330,cookies=cookies)
if l_330.status_code==200:
    json_data=l_330.content.decode('utf-8')
    data_str=json.loads(json_data)
    data_list=data_str['data']
    # print(data_list)
    whrp_330data=[i for i in data_list if re.search('更换',i['MDTITLE_C'])]
    
else:
    print('no data')
    
    

with open('fl.json','r') as f:
     fl=json.load(f)

d={'330':{},'350':{}}
for i in fl['330']:#区分飞机号
    d['330'][i]=[[],[],[],[],[],[],[],[]] #八个轮子的更换时间的列表
    for j in whrp_330data:
        if j['ACNO']==i:
            if re.search('1号|一号',j['MDTITLE_C'] ):
                d['330'][i][0].append(j['EN_DT'][0:10])
            elif re .search('2|二', j['MDTITLE_C']):
                d['330'][i][1].append(j['EN_DT'][0:10])
            elif re .search('3|三', j['MDTITLE_C']):
                d['330'][i][2].append(j['EN_DT'][0:10])
            elif re .search('4|四', j['MDTITLE_C']):
                d['330'][i][3].append(j['EN_DT'][0:10])
            elif re .search('5|五', j['MDTITLE_C']):
                d['330'][i][4].append(j['EN_DT'][0:10])
            elif re .search('6|六', j['MDTITLE_C']):
                d['330'][i][5].append(j['EN_DT'][0:10])            
            elif re .search('7|七', j['MDTITLE_C']):
                d['330'][i][6].append(j['EN_DT'][0:10])
            elif re .search('8|八', j['MDTITLE_C']):
                d['330'][i][7].append(j['EN_DT'][0:10])


postdata_350={"planstd":"2019-01-04 08:00:00",
            "planend":" 2024-04-05 08:00:00",
            # "ifClose":"",
            # "order":"asc",
            "keyWord":"主轮",
            "keyWordStr":"主轮",
            "actypeStr": "(A350)",
            "actype": "350",
            "page":"1",
            "rows":"9999"}
l_350=session.post(url_workorder,headers=headers,data=postdata_350,cookies=cookies)
if l_350.status_code==200:
    json_data=l_350.content.decode('utf-8')
    data_str=json.loads(json_data)
    data_list=data_str['data']
    # print(data_list)
    whrp_350data=[i for i in data_list if re.search('更换',i['MDTITLE_C'])]
    
else:
    print('no data')
    
for i in fl['350']:#区分飞机号
    d['350'][i]=[[],[],[],[],[],[],[],[]] #八个轮子的更换时间的列表
    for j in whrp_350data:
        if j['ACNO']==i:
            if re.search('1号|一号',j['MDTITLE_C'] ):
                d['350'][i][0].append(j['EN_DT'][0:10])
            elif re .search('2|二', j['MDTITLE_C']):
                d['350'][i][1].append(j['EN_DT'][0:10])
            elif re .search('3|三', j['MDTITLE_C']):
                d['350'][i][2].append(j['EN_DT'][0:10])
            elif re .search('4|四', j['MDTITLE_C']):
                d['350'][i][3].append(j['EN_DT'][0:10])
            elif re .search('5|五', j['MDTITLE_C']):
                d['350'][i][4].append(j['EN_DT'][0:10])
            elif re .search('6|六', j['MDTITLE_C']):
                d['350'][i][5].append(j['EN_DT'][0:10])            
            elif re .search('7|七', j['MDTITLE_C']):
                d['350'][i][6].append(j['EN_DT'][0:10])
            elif re .search('8|八', j['MDTITLE_C']):
                d['350'][i][7].append(j['EN_DT'][0:10])


def save_dict(dictionary, file_path):
    with open(file_path, 'w') as file:
        json.dump(dictionary, file)
        
save_dict(d,'wheels_time.json')