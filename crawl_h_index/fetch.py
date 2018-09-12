#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import base64
import shutil
import datetime
import re
from time import sleep
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.proxy import Proxy, ProxyType
import config

'''
1. 运行环境：
2. 一些特性
'''


script_dir=os.path.split(os.path.realpath(__file__))[0]+'/'

data_dir="%s%s"%(script_dir,config.storage_subdir)
#backup_dir="%s%s"%(script_dir,config.backup_subdir)

class Fetcher():

    def dmesg(self,m):
        if self.config.debug:
            print '[dmesg] %s'%m


    def init(self,config):
        self.config=config
        print self.config.browser_driver_command_executor
        command_executor=self.config.browser_driver_command_executor
        if self.config.browser_profile_dir:
            profile=FirefoxProfile(profile_directory=self.config.browser_profile_dir)
            self.dmesg('loading browser profile')
        else:
            profile=None
            self.dmesg('browser profile not configured, use None profile')
        self.dmesg('trying start a browser')
        
        px=config.proxy_type
        if px in ['socks','http']:
            self.dmesg('apply %s proxy, %s:%s'%(px,config.proxy_host,config.proxy_port))
            profile.set_preference("network.proxy.type", 1)
            profile.set_preference("network.proxy.%s"%px,config.proxy_host)
            profile.set_preference("network.proxy.%s_port"%px,int(config.proxy_port))

        profile.set_preference("network.proxy.socks_version",5)
        profile.update_preferences()


        self.driver=webdriver.Remote(
            command_executor=self.config.browser_driver_command_executor,
            desired_capabilities=DesiredCapabilities.FIREFOX,
            browser_profile=profile)
        try:
            self.driver.get(self.config.start_url)
        except:
            self.dmesg('打开失败，10s 后重试...')
            sleep(10)
            try:
                self.driver.get(self.config.start_url)
            except:
                self.dmesg('打开失败，10s 后重试...')
                sleep(10)
                self.driver.get(self.config.start_url)


    def run(self):
        pass


    def kw_search(self,kw):
        driver=self.driver
        #检查搜索框的class，无gs_vis为隐藏状态
        ele=driver.find_elements_by_xpath("//form[@id='gs_hdr_frm']")
        if len(ele)!=1:
            print 'form "gs_hdr_frm" not found'
            exit()
        if not ele[0].is_displayed():
            print 'form gs_hdr_frm is hidden, try open it'
            ele=driver.find_elements_by_xpath("//a[@id='gs_hdr_sre']")
            if len(ele)!=1:
                print('search_button not found, when trying open the form input')
                exit()
            ele[0].click()
            sleep(0.2)

        ele=driver.find_elements_by_xpath("//input[@id='gs_hdr_tsi']")
        if len(ele)!=1:
            print('input box not found')
            exit()
        ele[0].click()
        ele[0].clear()
        ele[0].send_keys(kw)
        sleep(0.2)
        ele=driver.find_elements_by_xpath("//button[@id='gs_hdr_tsb']")
        if len(ele)!=1:
            print('search button not found')
            exit()
        ele[0].click()
        sleep(2)

        ele=driver.find_elements_by_xpath("//table[@id='gsc_mvt_table']/tbody/tr")
        print 'search results count: %s'%len(ele)
        if len(ele) < 1 :
            print 'search result 0, to be skiped'
            return []
        results=[]
        for i in range(len(ele)):
            e=ele[i].find_elements_by_tag_name('td')
            item=[it.text for it in e]
            if len(item)==4:
                results.append(item)
        
        return results



    def read_left_kw_list(self,file_path):
        if not os.path.exists(file_path):
            self.dmesg('journals file %s not found '%file_path)
            exit()
        else:
            vals=[]
            f=open(file_path,'r')
            for line in f.readlines():
                vals.append(line.strip('\r\n').split('\t'))
        return vals


    def read_done_pos(self,pos_path):
        if os.path.exists(pos_path):
            f=open(pos_path,'r')
            line=f.readline()
            print 'pos file: %s'%line
            pos=int(line)
            f.close()
        else:
            pos=0
        return pos

    def write_done_pos(self,pos_path,pos):
        f=open(pos_path,'w+')
        f.write('%s'%pos)
        f.close()


    def write_result(self,file_path,results):
        buff=u''
        for i in range(len(results)):
            buff+=u"%s\r\n"%(u'\t'.join(results[i]))
        f=open(data_dir+'/results.txt','a+')
        f.write(buff.encode('utf-8'))
        f.flush()
        f.close()




if __name__ == '__main__':
    fetch=Fetcher()
    fetch.init(config)
    kws=fetch.read_left_kw_list(data_dir+'/journals.txt')
    pos=fetch.read_done_pos(data_dir+'/pos.txt')
    fetch.dmesg('pos: %s'%pos)
    for i in range(len(kws)):
        print 'kw[%s]: %s'%(i,kws[i][1])
        if i < pos:
            print 'skiped'
            continue
        try:
            results=fetch.kw_search(kws[i][1])
            fetch.write_result(data_dir+'/results.txt',results)
            fetch.write_done_pos(data_dir+'/pos.txt',i)
            sleep(10)
        except:
            print 'something goes wrong, skip and go ahead'
            pass
