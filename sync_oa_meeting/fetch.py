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
import config

'''
1. 运行环境：
2. 一些特性
'''




script_dir=os.path.split(os.path.realpath(__file__))[0]+'/'

data_dir="%s%s"%(script_dir,config.storage_subdir)
backup_dir="%s%s"%(script_dir,config.backup_subdir)

class FetchMeetingData():

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


    def run(self):
        pass


    def login(self):
        driver=self.driver
        sleep(1)
        ele=driver.find_elements_by_xpath("//div[@class='ms-login']//input")
        if len(ele)!=2:
            print('login form input boxes count unexpected')
            exit()
        else:
            ele[0].send_keys(self.config.ofc_username)
            ele[1].send_keys(self.config.ofc_password)
        ele=driver.find_elements_by_xpath("//div[@class='login-btns']//button")
        ele[0].click()
        sleep(5)
        ele=driver.find_elements_by_xpath("//div[@class='login-btns']//button")
        if len(ele) >=1 or '/login' in driver.current_url:
            print 'login failed, check the username and password'
            exit()


    def navi_to_contract_page(self):
        driver=self.driver
        locator=(By.XPATH,"//div[@class='headnav']/ul/li")
        WebDriverWait(driver, 20, 0.5).until(EC.presence_of_element_located(locator))
        ele=driver.find_elements_by_xpath("//div[@class='headnav']/ul/li")
        e=[e for e in ele if e.text==u'\u5408\u540c\u7ba1\u7406']
        self.dmesg('switch to 合同管理')
        if len(e)!=1:
            self.dmesg('顶部导航中找不到目标元素')
            print [e.text for e in ele]
            exit()
        e[0].click()
        sleep(1)

        #ele=driver.find_elements_by_xpath("//div[@class='main']/ul/li[2]/div/i[2]")
        #ele[0].click()
        #从 左侧栏分组大标题 找 招商
        self.dmesg('展开 招商')
        xpath="//div[@class='main']/ul/li[contains(@class,'el-submenu')]/div/span[text()='招商']/following-sibling::i"
        locator=(By.XPATH,xpath)
        WebDriverWait(driver, 20, 0.5).until(EC.presence_of_element_located(locator))
        ele=driver.find_elements_by_xpath(xpath)
        ele[0].click()
        sleep(1)

        self.dmesg('进入 我已审核的合同')
        xpath="//div[@class='main']/ul/li[contains(@class,'el-submenu')]/ul/li[contains(text(),'我已审核的合同')]"
        locator=(By.XPATH,xpath)
        WebDriverWait(driver, 20, 0.5).until(EC.presence_of_element_located(locator))
        ele=driver.find_elements_by_xpath(xpath)
        ele[0].click()

        sleep(1)
        
        ele=driver.find_elements_by_xpath("//section[@class='content-container']/div[contains(@class,'grid-content')]/div[@class='el-breadcrumb']")
        if len(ele)!=1 or not u'\u6211\u5df2\u5ba1\u6838\u7684\u5408\u540c' in ele[0].text :
            print '由右侧栏面包屑导航文本判断，打开页面非预期'
            print ele[1].text
            exit()
        """#尝试把每页显示条数改为最大项
        sleep(1)
        ele=driver.find_elements_by_xpath("//div[@class='ms-table']/div[@class='block']/div/span[@class='el-pagination__sizes']//span[@class='el-input__suffix']")
        if len(ele)!=1:
            self.dmesg('未找到每页显示条数下拉框，忽略更改')
        else:
            self.dmesg('找到每页显示条数，尝试更改')
            ele[0].click()
            sleep(1)
            ele=driver.find_elements_by_xpath("//body/div[contains(@class,'el-select-dropdown')]/div[@class='el-scrollbar']/div[@class='el-select-dropdown__wrap el-scrollbar__wrap']/ul/li[last()]")
            if len(ele)==1:
                self.dmesg('尝试更改为%s'%(ele[0].text.encode('utf-8')))
                ele[0].click()
                sleep(1)
            else:
                self.dmesg('找最大分页数选项异常')
        """


    def retrive_contract_page(self):
        driver=self.driver
        #等待表格头加载完毕，假定10个以上列
        for i in range(100):
            sleep(1)
            ele=driver.find_elements_by_xpath("//div[@class='ms-table']//section/div/div/table[@class='el-table__header']/thead/tr/th")
            if len(ele) > 10:
                self.dmesg('表头加载完毕')
                break
        column_name=[e.text.encode('utf-8') for e in ele if e.text]

        try:
            lines=[]
            ele=driver.find_elements_by_xpath("//div[@class='ms-table']//section/div/div/table[@class='el-table__body']/tbody/tr")
            for i in range(len(ele)):
                es=ele[i].find_elements_by_tag_name('td')
                line=[e.text.encode('utf-8') for e in es]
                lines.append(line)
        except selenium.common.exceptions.StaleElementReferenceException:
            lines=[]
            ele=driver.find_elements_by_xpath("//div[@class='ms-table']//section/div/div/table[@class='el-table__body']/tbody/tr")
            for i in range(len(ele)):
                es=ele[i].find_elements_by_tag_name('td')
                line=[e.text.encode('utf-8') for e in es]
                lines.append(line)
        return column_name,lines


    def retrive_contract(self):
        driver=self.driver
        header,data=self.retrive_contract_page()
        while True:
            ele=driver.find_elements_by_xpath("//section[@class='content-container']//div[contains(@class,'ms-table')]/div[@class='block']/div/button[contains(@class,'btn-next')]")
            if len(ele)!=1:
                self.dmesg('找到翻页下一页按钮数目异常')
                exit()
            #if u'disabled' in ele[0].get_attribute('class'):
            if ele[0].get_attribute('disabled')=='true':
                self.dmesg('下一页不可用，完成')
                self.dmesg('翻回第一页')
                e=driver.find_elements_by_xpath("//section[@class='content-container']//div[contains(@class,'ms-table')]/div[@class='block']/div/span[@class='el-pagination__jump']/div/input")
                if len(e)==1:
                    e[0].click()
                    e[0].send_keys(Keys.END)
                    e[0].send_keys(Keys.BACKSPACE*10)
                    e[0].send_keys('1')
                    e[0].send_keys(Keys.RETURN)
                    sleep(1)
                break
            self.dmesg('翻页：下一页')
            ele[0].click()
            h,d=self.retrive_contract_page()
            self.dmesg('本页获取%s条'%len(d))
            if h != header:
                self.dmesg('翻页后表格标题栏不一致，谨慎起见脚本退出')
                exit()
            data+=d
            self.dmesg('本页标题栏一致性检查通过')
            self.dmesg('当前共计%s条数据'%len(data))

        #调次序以"合同号"为首列字段名，按表格标题名称，以 utf-8 编码
        try:
            pos=header.index(r'合同号')
        except ValueError:
            self.dmesg('header 中找不到目标列')
        self.dmesg('交换值以调整首列，并清理特殊字符')
        header[0],header[pos] = header[pos],header[0]
        for i in range(len(data)):
            data[i][0],data[i][pos]=data[i][pos],data[i][0]
            for j in range(len(data[i])):
                data[i][j]=data[i][j].replace('"','').replace("'",'').replace('\t','').replace('\n','').replace('\r','')

        return header, data


    def read_file_contract(self,path):
        o_header=None
        o_data=[]
        #新旧数据对比
        if not os.path.exists(path):
            self.dmesg('原文件 %s 不存在，不做对比'%path)
        else:
            f=open(path,'r')
            o_header=f.readline().strip('\r\n').split('\t')
            for line in f.readlines():
                o_data.append(line.strip('\r\n').split('\t'))
        return o_header,o_data


    def write_file_contract(self,path,backup_path,header,data):
        self.dmesg('签单信息写入文件 %s'%path)
        f=open(path,'w+')
        f.write('%s\r\n'%('\t'.join(header)))
        for i in range(len(data)):
            f.write('%s\r\n'%('\t'.join(data[i])))
        f.flush()
        f.close()
        self.dmesg('同步备份：将文件复制到 %s'%backup_path)
        shutil.copyfile(path,backup_path)


    #def save_contract(self):
    #返回 (需要更新的单号, 新增单号, 删除单号, 有变更的单号)
    def retrive_contract_change(self,contract_path,backup_path,income_log_exists):
        header,data=self.retrive_contract()
        #新旧数据对比
        if not os.path.exists(contract_path):
            self.dmesg('原文件 %s 不存在，不做对比'%contract_path)
            self.dmesg('将签单信息写入 %s '%contract_path)
            self.write_file_contract(contract_path,backup_path,header,data)
            code=[it[0] for it in data]
            return code,code,[],[]
        else:
            o_header,o_data=self.read_file_contract(contract_path)
            if o_header != header :
                self.dmesg('标题行数据与原文件标题行不一致，谨慎退出，请备份（如需要）后删除旧数据再运行')
                print header
                print l1
                exit()
            #收入更新过的行，后面以此查询并更新收入记录
            to_update_code=[]
            try:
                income_column=header.index(r'到款金额')
            except ValueError:
                self.dmesg('列头中找不到 到款金额 列，谨慎退出')
                exit()

            deleted_code=[]
            addnew_code=[]
            changed_code=[]     #有信息变更的行，不仅到款金额列，其他列变动也算
            chg_count=0
            data_col_1=[d[0] for d in data]
            #遍历旧数据，看是否有删除或到款价格变化行
            for line in o_data:
                #删除的code
                if not line[0] in data_col_1:
                    deleted_code.append(data[i][0])
                    continue
                #非删除code，查出其在新数据中行号n，然后检查是否有改变，把到款额有改变的行，写入 to_update_code
                n=data_col_1.index(line[0])
                if data[n]!=line:
                    changed_code.append(line[0])
                    if data[n][income_column]!=line[income_column]:
                        to_update_code.append(line[0])
            o_data_c1=[d[0] for d in o_data]
            for i in range(len(data)):
                if not data[i][0] in o_data_c1:
                    addnew_code.append(data[i][0])
                    to_update_code.append(data[i][0])
            if not income_log_exists:
                self.dmesg('到款记录文件不存在，需要更新所有有到款的单号')
                to_update_code=[d[0] for d in data if float(d[income_column]) > 0 ]

            return to_update_code, addnew_code, deleted_code, changed_code



    def update_income_log(self,to_update_code,deleted_code,income_log_path,backup_path,income_log_exists):
        if len(to_update_code)==0:
            self.dmesg('没有待更新到款信息订单')
        else:
            
            #从csv中读入 income_log，根据已删除单号 deleted_code 删除记录；再根据code查询做合并
            #self.update_income_log(to_update_code,income_log_path,backup_path)
            self.income_log=self.read_file_income_log(income_log_path)
            self.income_log=[it for it in self.income_log if it[0] not in deleted_code]

            total_increased=0
            total_removed=0
            for code in to_update_code:
                logs=self.retrive_income_log_by_code(code)
                #TODO 检查变化，把增加新条目记录到income_log中；如果有减少条目，则报警
                increased,removed=self.merge_income_log(logs)
                total_increased += increased
                if removed >0:
                    total_removed += removed
                    self.dmesg('警告： %s 有删除的收入记录 %s 条'%(contract_code,removed))

            #TODO 把income_log写入csv文件，并备份
            f=open(income_log_path,'w+')
            f.write("code\ttime\tincome\tcurrency\r\n")
            for i in range(len(self.income_log)):
                f.write("%s\r\n"%('\t'.join(self.income_log[i])))
            f.flush()
            f.close()
            shutil.copyfile(income_log_path,backup_path)
        return True


    def unknow_unkown():
        income_log_path='%s/%s'%(data_dir,'income_log.csv')
        income_log_exists=os.path.exists(income_log_path)


        #新旧数据对比
        if not os.path.exists(contract_path):
            self.dmesg('原文件 %s 不存在，不做对比'%contract_path)
        else:
            o_header,o_data=read_file_contract(contract_path)
            if o_header != header :
                self.dmesg('标题行数据与原文件标题行不一致，谨慎退出，请备份（如需要）后删除旧数据再运行')
                print header
                print l1
                exit()
            #新旧数据对比，按第一列匹配对应，检查新数据有变化的行（逐列检查）、新增行、减少行
            add_count=0
            del_count=0
            chg_count=0





            #收入更新过的行，后面以此查询并更新收入记录
            to_update_code=[]
            try:
                income_column=header.index(r'到款金额')
            except ValueError:
                self.dmesg('列头中找不到 到款金额 列，谨慎退出')
                exit()
            #新旧数据对比，按第一列匹配对应，检查新数据有变化的行（逐列检查）、新增行、减少行
            add_count=0
            del_count=0
            chg_count=0
            deleted_code=[]
            addnew_code=[]
            data_col_1=[d[0] for d in data]
            #遍历旧数据，看是否有删除或到款价格变化行
            for line in o_data:
                #删除的code
                if not line[0] in data_col_1:
                    del_count+=1
                    deleted_code.append(data[i][0])
                    continue
                #非删除code，查出其在新数据中行号n，然后检查是否有改变，把到款额有改变的行，写入 to_update_code
                n=data_col_1.index(line[0])
                if data[n]!=line:
                    chg_count+=1
                    if data[n][income_column]!=line[income_column]:
                        to_update_code.append(line[0])
            o_data_c1=[d[0] for d in o_data]
            for i in range(len(data)):
                if not data[i][0] in o_data_c1:
                    add_count+=1
                    addnew_code.append(data[i][0])
                    to_update_code.append(data[i][0])
            if not income_log_exists:
                self.dmesg('到款记录文件不存在，需要更新所有有到款的单号')
                to_update_code=[d[0] for d in data if float(d[income_column]) > 0 ]

            print '新旧数据行对比: + %s     - %s     M %s'%(add_count,del_count,chg_count)
            if add_count > 0:
                self.dmesg('新增单号如下：')
                print addnew_code
            if del_count > 0:
                self.dmesg('*** 请注意：有删除单号，相关的到款记录表数据也将被删除 ***')
                print deleted_code
            print '待更新收入行%s'%to_update_code

        self.dmesg('签单信息写入文件 %s'%path)
        f=open(path,'w+')
        f.write('%s\r\n'%('\t'.join(header)))
        for i in range(len(data)):
            f.write('%s\r\n'%('\t'.join(data[i])))
        f.flush()
        f.close()

        now=datetime.datetime.now()
        backup='%s/%s%s'%(backup_dir,'contract.csv.',now.strftime('%Y%m%d%H%M%S'))
        self.dmesg('同步备份：将文件复制到 %s'%backup)
        shutil.copyfile(path,backup)

        if len(to_update_code)==0:
            self.dmesg('没有待更新到款信息订单')
        else:
            backup_path='%s/%s%s'%(backup_dir,'income_log.csv.',now.strftime('%Y%m%d%H%M%S'))
            
            #从csv中读入 income_log，根据已删除单号 deleted_code 删除记录；再根据code查询做合并
            #self.update_income_log(to_update_code,income_log_path,backup_path)
            income_log=self.read_file_income_log(income_log_path)
            income_log=[it for it in income_log if it[0] not in deleted_code]

            total_increased=0
            total_removed=0
            for code in to_update_code:
                logs=self.retrive_income_log_by_code(code)
                #TODO 检查变化，把增加新条目记录到income_log中；如果有减少条目，则报警
                increased,removed=self.merge_income_log(logs)
                total_increased += increased
                if removed >0:
                    total_removed += removed
                    self.dmesg('警告： %s 有删除的收入记录 %s 条'%(contract_code,removed))

            #TODO 把income_log写入csv文件，并备份
            f=open(income_log_path,'w+')
            f.write("code\ttime\tincome\tcurrency\r\n")
            for i in range(len(income_log)):
                f.write("%s\r\n"%('\t'.join(income_log[i])))
            f.flush()
            f.close()
            shutil.copyfile(income_log_path,backup_path)


    def read_file_income_log(self,income_log_path):
        data=[]
        if os.path.exists(income_log_path):
            f=open(income_log_path,'r')
            header=f.readline()
            for line in f.readlines():
                line=line.strip()
                data.append(line.split('\t'))
        return data


    def retrive_income_log_by_code(self,code):
        try:
            logs=self._retrive_income_log_by_code(code)
        except:
            sleep(3)
            try:
                logs=self._retrive_income_log_by_code(code)
            except:
                sleep(3)
                try:
                    logs=self._retrive_income_log_by_code(code)
                except:
                    self.dmesg('retrive_income_log_by_code(%s) 重试3次都失败了，只好谨慎退出 '%code)
                    logs=[]
                    exit()
        return logs


    def _retrive_income_log_by_code(self,code):
        driver=self.driver
        if driver.current_url != '%s%s'%(self.config.start_url,"#/aleady-audit-contract"):
            self.dmesg('当前不在订单列表中，尝试转入')
            self.navi_to_contract_page()
        self.dmesg(driver.current_url)
        locator=(By.XPATH,"//div[@class='data-search']/div[@class='search-term']//input")
        WebDriverWait(driver, 20, 0.5).until(EC.presence_of_element_located(locator))
        ele=driver.find_elements_by_xpath("//div[@class='data-search']/div[@class='search-term']//input")
        if len(ele) < 2:
            self.dmesg('找不到div.search-term里的input框，谨慎退出')
            exit()
        idx=-1
        for i in range(len(ele)):
            if r'合同号' in ele[i].get_attribute('placeholder').encode('utf-8'):
                idx=i
                self.dmesg('找到合同号输入框 idx=%s'%idx)
                break
        self.dmesg(code)
        ele[idx].send_keys(Keys.END)
        ele[idx].send_keys(Keys.BACKSPACE*30)
        ele[idx].send_keys(code)
        sleep(3)
        ele=driver.find_elements_by_xpath("//div[@class='data-search']/div[@class='search-now']")
        ele[0].click()
        sleep(3)
        #等待表格加载完成
        locator=(By.XPATH,"//section//table[@class='el-table__body']")
        WebDriverWait(driver, 20, 0.5).until(EC.presence_of_element_located(locator))

        sleep(10)

        ele=driver.find_elements_by_xpath("//div[@class='ms-table']/section/div[contains(@class,'el-table--enable-row-transition')]/div[@class='el-table__fixed-right']//table[@class='el-table__body']/tbody/tr/td[last()]//button")
        if len(ele)!=1:
            self.dmesg('数据表格超过1条记录，非预期，谨慎退出 %s 条'%len(ele))
            exit()
        ele[0].click()
        sleep(1)

        ele=driver.find_elements_by_xpath("//div[@class='ms-table']/section/div[contains(@class,'el-table--enable-row-transition')]/div[@class='el-table__fixed-right']//table[@class='el-table__body']/tbody/tr/td[last()]//ul[@class='menu']/li")
        if len(ele)!=1:
            self.dmesg('下拉菜单项查找失败： %s 条'%len(ele))
            exit()
        ele[0].click()
        sleep(1)

        locator=(By.XPATH,"//div[@class='el-tabs__nav'][@role='tablist']/div")
        WebDriverWait(driver, 20, 0.5).until(EC.presence_of_element_located(locator))

        ele=driver.find_elements_by_xpath("//div[@class='el-tabs__nav'][@role='tablist']/div")
        ele=[e for e in ele if e.text==u'\u6b3e\u9879']
        if len(ele)!=1:
            self.dmesg('未找到 款项tab')
        ele[0].click()

        ele=driver.find_elements_by_xpath("//p[@class='ms-title'][text()='付款阶段']/following-sibling::ul/li")
        logs=[]
        for i in range(0,len(ele),2):
            hay=ele[i+1].text[4:].encode('utf-8')
            tmp=re.findall(r"^[\d\.]+",hay)
            if len(tmp)>=1:
                num=tmp[0]
            currency=hay[len(num):]
            logs.append([code, ele[i].text[4:].encode('utf-8'), num, currency])
        self.dmesg('返回列表')
        ele=driver.find_elements_by_xpath("//a[@class='operation-back'][@title='返回']")
        ele[0].click()
        return logs


    def merge_income_log(self,logs):
        #先不计算increased 与 remved了，只做简单合并 logs 到 income_log
        increased=0
        removed=0
        if len(logs)==0:
            return 0,0
        code=logs[0][0]
        income_log=self.income_log
        self.income_log=[]
        for it in income_log:
            if it[0]!=code:
                self.income_log.append(it)
            else:
                increased -= 1
        for log in logs:
            self.income_log.append(log)
            increased += 1
        return increased,0



if __name__ == '__main__':
    fetch=FetchMeetingData()
    fetch.init(config)
    fetch.login()
    fetch.navi_to_contract_page()

    now=datetime.datetime.now()
    
    contract_path='%s/%s'%(data_dir,'contract.csv')
    contract_backup_path='%s/%s%s'%(backup_dir,'contract.csv.',now.strftime('%Y%m%d%H%M%S'))
    
    income_log_path='%s/%s'%(data_dir,'income_log.csv')
    income_log_backup_path='%s/%s%s'%(backup_dir,'income_log.csv.',now.strftime('%Y%m%d%H%M%S'))

    income_log_exists=os.path.exists(income_log_path)
    to_update_code,addnew_code,deleted_code,changed_code=fetch.retrive_contract_change(
        contract_path,contract_backup_path,income_log_exists)

    print '新旧数据行对比: + %s     - %s     M %s'%(len(addnew_code),len(deleted_code),len(changed_code))
    if addnew_code:
        print '新增单号如下：'
        print addnew_code
    if deleted_code:
        print '*** 请注意：有删除单号，相关的到款记录表数据也将被删除 ***'
        print deleted_code
    print '待更新收入行%s'%to_update_code

    print to_update_code
    print type(to_update_code)

    fetch.update_income_log(to_update_code,deleted_code,income_log_path,income_log_backup_path,income_log_exists)



    #fetch.save_contract()



    """
    print fetch.retrive_income_log_by_code('E-Spon-180511838')
    print fetch.retrive_income_log_by_code('E-Spon-180416190')
    """
