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


    def kw_search(self,kw1,kw2):
        driver=self.driver
        ele=driver.find_elements_by_xpath("//div[@id='item_r']/div[last()]/a")
        ele[0].click()

        box1=driver.find_elements_by_xpath("//input[@name='psnName_1']")
        box2=driver.find_elements_by_xpath("//input[@name='org_1']")
        if len(box1)!=1 or len(box2)!=1:
            print 'box psnName_1,tr_1 find error'
            exit()
        box1[0].click()
        box1[0].clear()
        box1[0].send_keys(kw1.decode('utf-8'))
        sleep(0.2)
        box2[0].click()
        box2[0].clear()
        box2[0].send_keys(kw2.decode('utf-8'))
        sleep(0.2)
        ele=driver.find_elements_by_xpath("//input[@id='searchBt2']")
        if len(ele)!=1:
            print('search button not found')
            exit()
        ele[0].click()
        sleep(2)

        ele=driver.find_elements_by_xpath("//div[@id='grid_2']/table/tbody/tr[@name='rm_tr']/td[@id='rt_cy']/a[@href]")
        print 'search results count: %s'%len(ele)
        if len(ele) < 1 :
            print 'search result 0, to be skiped'
            return []
        results=[]
        for i in range(len(ele)):
            print 'ele[%s].text: %s'%(i,ele[i].text)
            for item in self.crawl_lists(i):
                results.append( [kw1,kw2]+item )
        return results

    # 搜索表单页，按钮下ajax返回的条目列表，按序号逐条处理
    def crawl_lists(self,idx):
        driver=self.driver
        # 参与项目数的链接
        print 'crawl_lists(idx=%s)'%idx
        ele=driver.find_elements_by_xpath("//div[@id='grid_2']/table/tbody/tr[@name='rm_tr']/td[@id='rt_cy']/a[@href]")
        ele[idx].click()
        locator=(By.ID,'TB_iframeContent')
        WebDriverWait(driver,30).until(EC.frame_to_be_available_and_switch_to_it(locator))
        #driver.switch_to.frame('TB_iframeContent')
        #sleep(5)
        print "iframe ready, and switched to it, and wait for //table[@id='dataGrid1']/tbody/tr"
        locator=(By.XPATH,"//table[@id='dataGrid1']/tbody/tr")
        WebDriverWait(driver,30).until(EC.presence_of_element_located(locator))
        print 'ready'
        items=[]
        while True:
            sleep(1)
            ele=driver.find_elements_by_xpath("//table[@id='dataGrid1']/tbody/tr[@id]")
            if len(ele) < 1:
                continue
            for i in range(len(ele)):
                e=ele[i].find_elements_by_tag_name('td')
                if len(e) == 4:
                    item=[it.text.encode('utf-8') for it in e]
                    items.append(item)
            print 'items count: %s'%len(items)
            e=driver.find_elements_by_xpath("//td[@id='next_t_TopBarMnt1'][not(contains(@class,'ui-state-disabled'))]/span")
            if len(e) >=1 :
                print "发现下一页，准备翻页"
                e[0].click()
            else:
                print '下页不可用，多页完成；关闭弹出层'
                sleep(1)
                e=driver.find_elements_by_xpath("//input[@id='back']")
                if len(e)>=1:
                    e[0].click()
                driver.switch_to.default_content()
                break
        return items



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
        buff=''
        for i in range(len(results)):
            buff+="%s\r\n"%('\t'.join(results[i]))
        f=open(data_dir+'/results.txt','a+')
        f.write(buff)
        f.flush()
        f.close()




if __name__ == '__main__':
    fetch=Fetcher()
    fetch.init(config)
    kws=fetch.read_left_kw_list(data_dir+'/keywords.txt')
    pos=fetch.read_done_pos(data_dir+'/pos.txt')
    fetch.dmesg('pos: %s'%pos)
    for i in range(len(kws)):
        print 'kw[%s]: %s  %s'%(i,kws[i][0],kws[i][1])
        if i < pos:
            print 'skiped'
            continue
        results=fetch.kw_search(kws[i][0],kws[i][1])
        fetch.write_result(data_dir+'/results.txt',results)
        fetch.write_done_pos(data_dir+'/pos.txt',i)
        sleep(3)
