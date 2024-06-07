# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 08:56:42 2024

@author: makej
"""

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

time.sleep(3)
"获取验证码"
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
            "keyWord":"刹车",
            "keyWordStr":"刹车",
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

# xwb=['B-304U','B-304V','B-301D','B-306N','B-325J','B-32AG','B-32F8','B-32G2','B-32G6']
with open('fl.json','r') as f:
     fl=json.load(f)


d={}
for i in fl['350']:
    print(str(i)+'刹车更换时间')
    d[i]=[[],[],[],[],[],[],[],[]] #八个刹车的更换时间的列表
    for j in whrp_data:
        if j['ACNO']==i:
            if re.search('1|一',j['MDTITLE_C'] ):
                d[i][0].append(j['EN_DT'][0:10])
            elif re .search('2|二', j['MDTITLE_C']):
                d[i][1].append(j['EN_DT'][0:10])
            elif re .search('3|三', j['MDTITLE_C']):
                d[i][2].append(j['EN_DT'][0:10])
            elif re .search('4|四', j['MDTITLE_C']):
                d[i][3].append(j['EN_DT'][0:10])
            elif re .search('5|五', j['MDTITLE_C']):
                d[i][4].append(j['EN_DT'][0:10])
            elif re .search('6|六', j['MDTITLE_C']):
                d[i][5].append(j['EN_DT'][0:10])            
            elif re .search('7|七', j['MDTITLE_C']):
                d[i][6].append(j['EN_DT'][0:10])
            elif re .search('8|八', j['MDTITLE_C']):
                d[i][7].append(j['EN_DT'][0:10])

# df=pd.DataFrame.from_dict(d,orient='index')

def save_dict(dictionary, file_path):
    with open(file_path, 'w') as file:
        json.dump(dictionary, file)
        
save_dict(d,'brake.json')