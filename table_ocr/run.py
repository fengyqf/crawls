#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import datetime
import time
from aip import AipOcr

'''
APP_ID=''
API_KEY=''
SECRET_KEY=''
'''
from config import *

script_dir=os.path.split(os.path.realpath(__file__))[0]+'/'
image_path=['']*5
image_path[1]=script_dir+'images/screen_2.png'
image_path[2]=script_dir+'images/table_1.png'



def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()


aipOcr=AipOcr(APP_ID, API_KEY, SECRET_KEY)

options = {
    'detect_direction': 'true',
    'language_type': 'CHN_ENG',
}

'''
# 通用文字识别
result = aipOcr.basicGeneral(get_file_content(image_path[1]), options)
# 通用文字识别（含位置信息版）
result = aipOcr.general(get_file_content(image_path[1]), options)
'''


# 表格识别
result = aipOcr.tableRecognitionAsync(get_file_content(image_path[2]), options)
log_id=result['log_id']
request_id=result['result'][0]['request_id']
print '[%s]   log_id: %s    request_id: %s ' %(image_path[2],log_id,request_id)
while True:
    result=aipOcr.getTableRecognitionResult(request_id,{'result_type':'json'})
    print result
    if result['result']['percent'] == 100:
        break
    pass

















