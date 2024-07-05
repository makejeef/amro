# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 10:29:36 2024

@author: makej
"""
import json 
import matplotlib.pyplot as plt


with open('wheels_fl.json','r') as f:
    fl=json.load(f)
    
for i in fl:
    for j in fl[i]:
        for k in fl[i][j]:
            

