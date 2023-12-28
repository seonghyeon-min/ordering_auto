from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoAlertPresentException, UnexpectedAlertPresentException, WebDriverException
import re
import time
import pyperclip
import pandas as pd

USER_ID = 'seonghyeon.min'
USER_PW = 'alstjdgus@4416'
PlatformCode = 'webOSTV 6.0-W21Z-W21Z'
url = 'http://qt2-kic.smartdesk.lge.com/admin/main.lge?serverType=QA2'
cpurl = 'http://qt2-kic.smartdesk.lge.com/admin/master/ordering/ordering/retrieveAppOrderingList.lge?serverType=QA2'

def ClickEvent(driver, contribute, path) :
    driver.find_element(contribute, path).click()
    
def SendKeyEvent(driver, contribute, path) :
    driver.find_element(contribute, path).send_keys(Keys.CONTROL, 'v')
    
def GetDriver(url) :
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.implicitly_wait(3)
    driver.get(url)
    alert = Alert(driver)
    alert.accept()
    
    time.sleep(2.5)
    
    return driver

def AutoLogin(driver, ID, PW) :
    ClickEvent(driver, By.ID, 'USER')
    pyperclip.copy(ID)
    SendKeyEvent(driver, By.ID, 'USER')
    ClickEvent(driver, By.ID, 'LDAPPASSWORD')
    pyperclip.copy(PW)
    SendKeyEvent(driver, By.ID, 'LDAPPASSWORD')
    ClickEvent(driver, By.ID, 'loginSsobtn')
    
    time.sleep(0.5)
    
def Ordering(url, driver) :
    print('[CP] START TO TEST DRAG AND DROP FUNC.')
    driver.get(url)
    
    
    # --- SET CONTRIBUE --- #
    ClickEvent(driver, By.XPATH, '/html/body/div/div/form[2]/div/fieldset/div/table/tbody/tr[1]/td/span/div/button')
    pyperclip.copy(PlatformCode)
    SendKeyEvent(driver, By.XPATH, '/html/body/div/div/form[2]/div/fieldset/div/table/tbody/tr[1]/td/span/div/ul/li[1]/div/input')
    
    time.sleep(1.5)
    # /html/body/div/div/form[2]/div/fieldset/div/table/tbody/tr[1]/td/span/div/ul/li[28]/a/label
    ClickEvent(driver, By.XPATH, '/html/body/div/div/form[2]/div/fieldset/div/table/tbody/tr[1]/td/span/div/ul/li[64]/a/label')
    ClickEvent(driver, By.XPATH, '/html/body/div/div/form[2]/div/div[1]/h3')
    ClickEvent(driver, By.XPATH, '/html/body/div/div/form[2]/div/fieldset/div/table/tbody/tr[3]/td[1]/select')
    ClickEvent(driver, By.XPATH, '/html/body/div/div/form[2]/div/fieldset/div/table/tbody/tr[3]/td[1]/select/option[2]') # draft
    
    
    ClickEvent(driver, By.XPATH, '/html/body/div/div/form[2]/div/div[2]/div[1]/select')
    ClickEvent(driver, By.XPATH, '/html/body/div/div/form[2]/div/div[2]/div[1]/select/option[7]')

    # ClickEvent(driver, By.XPATH, '/html/body/div/div/form[2]/div/fieldset/div/div/button')
    time.sleep(1.5)
    
    Pagnation = list(driver.find_element(By.XPATH, '/html/body/div/div/form[2]/div/nav/ul').text)
    Pagelst = ''.join(Pagnation).split('\n')
    
    print(f'[DEBUG] PageList : {Pagelst}')
    
    if 'Next' in Pagelst : 
        startpageidx = int(Pagelst[Pagelst.index('1')])
        endpageidx = int(Pagelst.index('Next')-1)

    else : 
        startpageidx = int(Pagelst[Pagelst.index('1')])
        endpageidx = int(Pagelst[-1])     
    
    print(f'[DEBUG] Ready to set page from {startpageidx} to {endpageidx}')
    
    for page in range(startpageidx, endpageidx+1) :
        try :
            pageSelector = f'/html/body/div/div/form[2]/div/nav/ul/li[{page}]/a'
        except :
            pageSelector = '/html/body/div/div/form[2]/div/nav/ul/li/a'
            
        ClickEvent(driver, By.XPATH, pageSelector)
        time.sleep(0.5)
        
        tr = len(driver.find_element(By.XPATH, '/html/body/div/div/form[2]/div/div[3]/table/tbody').find_elements(By.TAG_NAME, 'tr'))
        
        for num in range(tr, 0, -1) :
            print(num)
            currentwindow = driver.current_url
            
            ClickEvent(driver, By.XPATH, f'/html/body/div/div/form[2]/div/div[3]/table/tbody/tr[{num}]/td[4]/a')
            # /html/body/div/div/form[2]/div/div[3]/table/tbody/tr[58]/td[4]/a
            while driver.current_url == currentwindow :
                print('page loading...')
            print('[CP] page loaded')
            print()
            time.sleep(0.5)
            driver.find_element(By.XPATH, '//*[@id="orderingForm"]/div[2]/div[8]/div[2]/button[1]').click()
            time.sleep(0.5)
            driver.find_element(By.XPATH, '//*[@id="popup-todayChangeList"]/div/div/div[3]/button').click()
            time.sleep(0.5)
            #show up pop-up
            alert = Alert(driver)
            alert.accept()
            print(f'[CP] Ordering has been comfirmed')
            print()
            driver.back()
            
driver = GetDriver(url)
AutoLogin(driver, USER_ID, USER_PW)
time.sleep(2.5)
Ordering(cpurl, driver)
