# -*- coding: utf-8 -*-
"""
Created on Tue Apr 30 08:41:43 2024

@author: makej
"""

import requests,time,json

from selenium import webdriver
from selenium.webdriver.common.by import By


def get_cookies(url):
    driver=webdriver.Firefox()
    driver.implicitly_wait(5)
    # url='https://me.sichuanair.com/login.shtml'
    driver.get(url['airnavx'])


    "输入账号密码进入airnav，获取cookies"
    elements_acesscode=driver.find_element(By.NAME,'access-code')
    elements_acesscode.send_keys('airbus123')

    driver.find_element(By.NAME,'submit').click()

    time.sleep(5)
    cookies = driver.get_cookies()
    return cookies
    driver.close() 
    
def get_fl(fl_type,cookies):
    session=requests.Session()
    air_cookies={cookie['name']: cookie['value'] for cookie in cookies}
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',}

    "需要看清楚是get还是post方法"
    # l=session.post(url['330'],data=post_data['330'],headers=headers,cookies=air_cookies)
    l=requests.get(url['330'],data=post_data['330'],headers=headers,cookies=air_cookies)
    if l.status_code==200:
        json_data=l.content.decode('utf-8')
        data_str=json.loads(json_data)
        fln_list=data_str['results']
        fl=[i['aircraftDetail'][0][0:6] for i in fln_list]
        return fl
    else:
        print('no data')
    




    
if __name__=='__main__':
    "url列表"
    url={'airnavx':'http://tp3.sichuanair.com:8000/airnavx/search/text',
             '330':'http://tp3.sichuanair.com:8000/airnavx/api/filter/getFilter?filterType=tailNumber&maxResults=21&msnBinding=%7B%22actype%22:%5B%22A330%22%5D,%22customization%22:%5B%22CSC%22%5D%7D&revId=654749_SGML_C&searchFilter=&searchMode=document.toc',
             '350':'http://tp3.sichuanair.com:8000/airnavx/api/filter/getFilter?filterType=tailNumber&maxResults=21&msnBinding=%7B%22actype%22:%5B%22A350%22%5D,%22customization%22:%5B%22CSC%22%5D%7D&revId=655658_S1KD_C&searchFilter=&searchMode=document.toc'
             }
    "post_data列表"
    "同一型号的飞机号列表"
    post_data={'330':{'filterType': 'tailNumber',
                      'maxResults': '21',
                      'msnBinding': {"actype":["A330"],"customization":["CSC"]},
                      'revId': '654749_SGML_C',
                      'searchMode':'document.toc'},
               '350':{'filterType': 'tailNumber',
                      'maxResults': '21',
                      'msnBinding': {"actype":["A350"],"customization":["CSC"]},
                      'revId': '655658_S1KD_C',
                      'searchMode':'document.toc'}}
    
    
    
    
    