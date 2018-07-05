#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import base64
import shutil
from datetime import datetime
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
import config

'''
1. 运行环境：
2. 一些特性
'''




script_dir=os.path.split(os.path.realpath(__file__))[0]+'/'

data_dir="%s%s"%(script_dir,'data')


class FetchRtifData():

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

        if 'login.webofknowledge.com/error/Error' in self.driver.current_url:
            self.dmesg('login status Error, trying re-login')
            ele=self.driver.find_element_by_name('username')
            ele.clear()
            ele.send_keys(config.wos_username)
            ele=self.driver.find_element_by_name('password')
            ele.clear()
            ele.send_keys(config.wos_password)
            ele=self.driver.find_element_by_name('rememberme')
            if ele.get_property('checked')==False:
                ele.click()
            ele=self.driver.find_element_by_tag_name('button')
            ele.click()
            sleep(1)
        if 'login.webofknowledge.com/error/Error' in self.driver.current_url:
            exit('login failed, Maybe VPN required.')
        elif 'apps.webofknowledge.com/' in self.driver.current_url:
            self.dmesg('login passed')
        else:
            exit('登录状态未知，为可靠起见，请检查')
            pass


    def do_wos_adv_search(self,search_text):
        driver=self.driver
        self.goto_adv_search_box_page()
        self.dmesg('高级检索页面输入条件:\n%s'%search_text)
        ele=driver.find_element_by_xpath("//form[@id='WOS_AdvancedSearch_input_form']//div[@class='AdvSearchBox']//textarea[@id='value(input1)']")
        ele.clear()
        ele.send_keys(search_text)
        ele=driver.find_element_by_xpath("//form[@id='WOS_AdvancedSearch_input_form']//div[@class='AdvSearchBox']//span[@id='searchButton']//button[@id='search-button']")
        ele.click()
        self.dmesg('高级搜索完成，搜索历史中应该已经有该项')

        ele=driver.find_elements_by_xpath("//div[@id='skip-to-navigation']//a[contains(@href,'_CombineSearches_input.do')]")
        if len(ele)==0:
            self.dmesg('无法在主导航栏中找到“检索历史”: href contains(_CombineSearches_input.do)')
            return False
        elif len(ele)>1:
            self.dmesg('在主导航栏中找到多个“检索历史”项: href contains(_CombineSearches_input.do)')
            return False
        else:
            pass
        ele[0].click()
        sleep(1)
        if '.com/WOS_CombineSearches_input.do?' not in driver.current_url:
            url=driver.current_url.encode('utf-8')
            self.dmesg('当前非检索历史页面，尝试切换数据库')
            print(url)
            self.dmesg('展开数据库下拉列表')
            ele=driver.find_element_by_xpath("//div[@class='dbselectdiv']//span[@class='select2-selection__arrow']")
            ele.click()
            sleep(0.3)
            self.dmesg('点击wos核心合集切换')
            ele=driver.find_element_by_xpath("//ul[@id='select2-databases-results'][@class='select2-results__options']/li[contains(text(),'Web of Science')]")
            ele.click()
            sleep(0.3)
            self.dmesg('进入wos核心合集检索历史页')

        assert '.com/WOS_CombineSearches_input.do?' in driver.current_url

        ele=driver.find_elements_by_xpath("//form[@name='WOS_CombineSearches_input_form']//tbody/tr[@id]/td/div[@class='historyQuery']")
        self.dmesg('搜索历史条数 %s'%len(ele))
        ele=[e for e in ele if e.text==search_text]
        self.dmesg('与search_text一致的搜索历史条数 %s'%len(ele))
        if len(ele):
            self.dmesg('之前没有手工加入paper, review的精练，请先手工操作后继续，可以使用下面条件')
            self.dmesg('PY=(2016 OR 2015) AND IS=2050-7488')
            self.dmesg('完成wos精练，返回 False，注意，本次尝试查询的search_text要重新执行')
            return false
        for i in range(len(ele)):
            e=ele[i].find_elements_by_class_name('historyRefine')
            for j in range(len(e)):
                print e[j].text


    def goto_adv_search_box_page(self):
        driver=self.driver
        ele=driver.find_elements_by_xpath("//a[@class='reverse-focus-style']")
        if len(ele)==1:
            self.dmesg('返回首页')
            ele[0].click()
        else:
            self.dmesg('首页链接查找异常 %s'%len(ele))
        sleep(1)
        if '.com/WOS_GeneralSearch_input.do?' not in driver.current_url:
            url=driver.current_url.encode('utf-8')
            self.dmesg('当前非检索历史页面，尝试切换数据库')
            print(url)
            self.dmesg('展开数据库下拉列表')
            ele=driver.find_element_by_xpath("//div[@class='dbselectdiv']//span[@class='select2-selection__arrow']")
            ele.click()
            sleep(0.3)
            self.dmesg('点击wos核心合集切换')
            ele=driver.find_element_by_xpath("//ul[@id='select2-databases-results'][@class='select2-results__options']/li[contains(text(),'Web of Science')]")
            ele.click()
            sleep(0.3)
            self.dmesg('进入wos核心合集检索历史页')

        if '/WOS_AdvancedSearch_input.do?product=WOS&' in driver.current_url:
            self.dmesg('当前即是wos核心合集库的高级检索')
        else:
            self.dmesg('点tab上高级检索')
            ele=driver.find_element_by_xpath("//ul[@class='searchtype-nav']//a[contains(@href,'WOS_AdvancedSearch_input.do?')]")
            ele.click()
            sleep(1)


    def goto_search_history_page(self):
        driver=self.driver
        ele=driver.find_elements_by_xpath("//div[@id='skip-to-navigation']//a[contains(@href,'_CombineSearches_input.do')]")
        if len(ele)==0:
            self.dmesg('无法在主导航栏中找到“检索历史”: href contains(_CombineSearches_input.do)')
            return False
        elif len(ele)>1:
            self.dmesg('在主导航栏中找到多个“检索历史”项: href contains(_CombineSearches_input.do)')
            return False
        else:
            pass
        ele[0].click()
        sleep(1)


    def search_his_filter(self,search_text):
        driver=self.driver
        self.goto_search_history_page()
        ele=driver.find_elements_by_xpath("//button[@name='selsets']")
        ele[0].click()
        sleep(1)
        ele=driver.find_elements_by_xpath("//button[@title='删除所选检索式']")
        ele[0].click()
        self.dmesg('清理历史搜索完成')
        sleep(1)

        self.goto_adv_search_box_page()
        ele=driver.find_element_by_xpath("//form[@id='WOS_AdvancedSearch_input_form']//div[@class='AdvSearchBox']//textarea[@id='value(input1)']")
        ele.clear()
        ele.send_keys(search_text)
        ele=driver.find_element_by_xpath("//form[@id='WOS_AdvancedSearch_input_form']//div[@class='AdvSearchBox']//span[@id='searchButton']//button[@id='search-button']")
        ele.click()
        self.dmesg('高级搜索完成，搜索历史中应该已经有该项')
        ele=driver.find_elements_by_xpath("//div[@id='skip-to-navigation']//a[contains(@href,'_CombineSearches_input.do')]")
        self.goto_search_history_page()
        ele=driver.find_elements_by_xpath("//div[@id='set_1_div'][@class='historyResults']/a")


        ele[0].click()
        self.dmesg('进入检索结果页')
        #ele=driver.find_element_by_xpath("//a[text()='Web of Science 类别']")
        ele=driver.find_elements_by_xpath("//input[@value='DocumentType_ARTICLE']")
        if len(ele)==1:
            ele[0].click()
            sleep(0.2)
        ele=driver.find_elements_by_xpath("//input[@value='DocumentType_REVIEW']")
        if len(ele)==1:
            ele[0].click()
            sleep(0.2)
        ele=driver.find_elements_by_xpath("//div[@id='JCRCategories_tr']/button")
        ele[0].click()
        sleep(1)






    '''
    PY=(2016 OR 2015) AND IS=2050-7488
    '''


    def change_search_text(self,issn,year):
        driver=self.driver
        self.goto_search_history_page()
        #search_text="IS=%s AND PY=(%s OR %s)"%(issn,year-2,year-1)
        search_text="PY=(%s OR %s) AND IS=%s"%(year-2,year-1,issn)
        self.dmesg('找搜索历史记录，期望两条，一条原始检索（下），一行精炼结果（上）')
        ele=driver.find_elements_by_xpath("//form[@name='WOS_CombineSearches_input_form']//tbody/tr[@id]/td/div[@class='historyQuery']")
        if len(ele)!=2:
            self.dmesg('条数非2条，谨慎退出，请检查。  len(ele)=%s'%len(ele))
            return False
        ele=driver.find_elements_by_xpath("//div[@id='refineDiv']")
        print ele[0].text
        tmp=ele[0].text.encode('utf-8')
        if not (r'精炼依据' in tmp and r'精炼依据' in tmp):
            self.dmesg('第一条搜索历史似乎不是精炼搜索')
            return False
        self.dmesg('查找并编辑检索式')
        ele=driver.find_elements_by_xpath("//div[@class='historyEdit']/a")
        ele[0].click()
        sleep(1)
        ele=driver.find_element_by_xpath("//form[@id='WOS_AdvancedSearch_input_form']//div[@class='AdvSearchBox']//textarea[@id='value(input1)']")
        ele.clear()
        ele.send_keys(search_text)
        ele=driver.find_element_by_xpath("//form[@id='WOS_AdvancedSearch_input_form']//div[@class='AdvSearchBox']//span[@id='searchButton']//button[@id='search-button']")
        ele.click()
        self.dmesg('高级搜索完成，搜索历史中应该已经有该项')

        self.goto_search_history_page()
        self.dmesg('再次查找修改后的搜索历史记录，期望两条，一条原始检索（下），一行精炼结果（上）')
        ele=driver.find_elements_by_xpath("//form[@name='WOS_CombineSearches_input_form']//tbody/tr[@id]/td/div[@class='historyQuery']")
        if len(ele)!=2:
            self.dmesg('条数非2条，谨慎退出，请检查。  len(ele)=%s'%len(ele))
            return False
        ele=driver.find_elements_by_xpath("//div[@id='refineDiv']")
        print ele[0].text
        tmp=ele[0].text.encode('utf-8')
        if not (r'精炼依据' in tmp and r'精炼依据' in tmp):
            self.dmesg('第一条搜索历史似乎不是精炼搜索')
            return False
        ele=driver.find_elements_by_xpath("//div[@class='historyResults']/a")
        ele[0].click()
        sleep(1)
        #locator=(By.XPATH,"//div[@id='view_citation_report_image_placeholder']/div[@class='summary_CitCount']//a")
        locator=(By.XPATH,"//div[@id='view_citation_report_image_placeholder']//a")
        WebDriverWait(driver, 20, 0.5).until(EC.presence_of_element_located(locator))
        ele=driver.find_elements_by_xpath("//div[@id='view_citation_report_image_placeholder']/div[@class='summary_CitCount']//a")
        if len(ele)>=1:
            ele[0].click()
            sleep(1)
            ele=driver.find_elements_by_xpath("//td[@id='piChart-container'][@class='quarter-width']//em")
            pub_count=ele[0].text

            ele=driver.find_elements_by_xpath("//div[@class='CitReportTotalRow1']/div[@class='tcPerYear']")
            label=[e.text.encode('utf-8') for e in ele]+['sum','avg']
            ele=driver.find_elements_by_xpath("//div[@class='CitReportTotalRow2']/div[@class='CitReport_totals_row']/div[@class!='CRpt_Remove']")
            value=[e.text.encode('utf-8') for e in ele]
            # TODO: 可以从下面表格中分析出top 10高引文章的引用量，不过太麻烦，暂时放弃
            #ele=driver.find_elements_by_xpath("//div[@class='search-results-item']")
        else:
            #找不到引用报告入口，可能引用报告不可用
            pub_count=0
            ele=driver.find_elements_by_xpath("//div[@id='view_citation_report_image_placeholder']/div[@class='CitCountError']")
            if len(ele) >=1:
                self.dmesg('引用报告错误消息div框:')
                print ele[0].text
                label=['']*7
                value=['-1']*7
            else:
                label=['']*7
                value=['-999']*7



        print '\n\n---- %s %s -------\npub_count: %s\nlabel: %s  value:%s\n'%(issn,year,pub_count,len(label),len(value))
        print label
        print value
        self.save_ifrt(issn,year,pub_count,label,value)



    def save_ifrt(self,issn,year,pub_count,label,value):
        path='%s/raw.txt'%data_dir
        now=datetime.now().strftime('%Y%m%d%H%M%S')
        if not os.path.exists(path):
            f=open(path,'w+')
            f.write('\t'.join(['issn','ifyear','pubcnt']+label+['time'])+'\r\n')
        else:
            f=open(path,'a')
        line='\t'.join([issn,str(year),str(pub_count)]+value+[now])+'\r\n'
        f.write(line)
        f.close()






#======================================================================





if __name__ == '__main__':
    issn_list=['0001-7213','0236-6290','0044-605X','0567-8315','0001-723X','1217-8837','0001-7272','1139-9287','0151-9093','0360-1293','0001-7884','1280-8571','1059-7123','0736-5829','0306-4603','1355-6215','0965-2140','0001-821X','0263-6174','0929-5607','0065-2113','0149-1423','1550-7416','1522-1059','1530-9932','0942-8925','0025-5858','1085-3375','1069-6563','1040-2446','1076-6332','0001-4842','0949-1775','1217-8969','0889-325X','0889-3241','0360-0300','0362-1340','0734-2071','0362-5915','0730-0301','1046-8188','0098-3500','0164-0925','1049-331X','1063-7710','1529-7853','1554-8929','1936-0851','0097-6156','1091-5397','0906-4702']
    year=2017
    issn='2050-7488'
    search_text="PY=(%s OR %s) AND IS=%s"%(issn,year-2,year-1)
    fetch=FetchRtifData()
    fetch.init(config)
    fetch.search_his_filter(search_text)

    fetch.do_wos_adv_search(search_text)

#----------------------

'''
# 本脚本还不能完全自动执行，其中一步需要手工操作，执行如下


import fetch
f=fetch.FetchRtifData()
f.init(fetch.config)
f.goto_adv_search_box_page()

##  这里是手工步骤.......
PY=(2016 OR 2017) AND IS=2050-7488

##

f.goto_search_history_page()



f.change_search_text('1049-331X',2017)
f.change_search_text('1233-2356',2017)
'''

