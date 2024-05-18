# -*- coding: utf-8 -*-
"""
Created on Sat Mar 23 09:02:52 2024

@author: makej
"""

from selenium import webdriver
from selenium.webdriver.common.by import By

import time,ddddocr,requests,json,csv,re


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
post_data={"planstd":"2018-01-04 08:00:00",
            "planend":" 2024-04-05 08:00:00",
            # "ifClose":"",
            # "order":"asc",
            "keyWord":"主轮",
            "keyWordStr":"主轮",
            "actypeStr": "(A350)",
            "actype": "A350",
            "page":"1",
            "rows":"999"}
l=session.post(url_workorder,headers=headers,data=post_data,cookies=cookies)
if l.status_code==200:
    json_data=l.content.decode('utf-8')
    data_str=json.loads(json_data)
    data_list=data_str['data']
    # print(data_list)
    whrp_data=[i for i in data_list if re.search('更换',i['MDTITLE_C'])]
    
else:
    print('no data')

xwb=['B-304U','B-304V','B-301D','B-306N','B-325J','B-32AG','B-32F8','B-32G2','B-32G6']
rp_date=[]
for i in range(len(xwb)):
    rp_date.append([])
    for j in whrp_data:
        if j['ACNO']==xwb[i]:
            rp_date[i].append(j['EN_DT'][0:10])
            
value=dict(zip(xwb,rp_date))

    