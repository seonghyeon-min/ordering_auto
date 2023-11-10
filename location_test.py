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
PlatformCode = 'webOSTV 23-S23Y-S23Y'
url = 'http://qt2-kic.smartdesk.lge.com/admin/main.lge?serverType=QA2'
cpurl = 'http://qt2-kic.smartdesk.lge.com/admin/master/ordering/ordering/retrieveAppOrderingList.lge?serverType=QA2'

cautionCP4smnt = {
    'YoutubeTV' : 95384,
    'Youtubesmnt' : 357640,
}

def getAppinfo(country) :
    #path 는 변경필요해보임
    Appdf = pd.read_excel(r"C:\Users\test\Downloads\Ordering List_for_test.xls", index_col=False) 
    certainApp = Appdf[Appdf['Country Name'] == country][['Country Name', 'Order Type', 'App Name', 'App Id', 'Order Number']].reset_index(drop=True)
    
    # scale Appid
    replace_to = {cautionCP4smnt['YoutubeTV'] : cautionCP4smnt['Youtubesmnt']}
    certainApp = certainApp.replace(replace_to)
    print(certainApp)
    print()
    
    return certainApp

def GetDriver(url) :
    print("CRALWING [] set driver for scrapying")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.implicitly_wait(3)
    driver.get(url)
    alert = Alert(driver)
    alert.accept()
    time.sleep(2.5)
    
    return driver

def AutoLogin(driver, ID, PW) :
    driver.find_element(By.ID,'USER').click() 
    pyperclip.copy(ID)
    driver.find_element(By.ID,'USER').send_keys(Keys.CONTROL,'v')
    driver.find_element(By.ID,'LDAPPASSWORD').click()
    pyperclip.copy(PW)
    driver.find_element(By.ID,'LDAPPASSWORD').send_keys(Keys.CONTROL,'v')
    driver.find_element(By.ID,'loginSsobtn').click()
    time.sleep(0.5)
    
    
def Ordering(url, driver) :
    print('[CP] start to test drag and drop func.')
    driver.get(url)
    
    driver.find_element(By.XPATH, '/html/body/div/div/form[2]/div/fieldset/div/table/tbody/tr[1]/td/span/div/button').click()
    pyperclip.copy(PlatformCode)
    driver.find_element(By.XPATH, '/html/body/div/div/form[2]/div/fieldset/div/table/tbody/tr[1]/td/span/div/ul/li[1]/div/input').send_keys(Keys.CONTROL, 'v')
    time.sleep(1.5)
    # /html/body/div/div/form[2]/div/fieldset/div/table/tbody/tr[1]/td/span/div/ul/li[28]/a/label
    driver.find_element(By.XPATH, '/html/body/div/div/form[2]/div/fieldset/div/table/tbody/tr[1]/td/span/div/ul/li[28]/a/label').click()
    driver.find_element(By.XPATH, '/html/body/div/div/form[2]/div/div[1]/h3').click()
    driver.find_element(By.XPATH, '/html/body/div/div/form[2]/div/fieldset/div/table/tbody/tr[3]/td[1]/select').click()
    driver.find_element(By.XPATH, '/html/body/div/div/form[2]/div/fieldset/div/table/tbody/tr[3]/td[1]/select/option[2]').click()
    driver.find_element(By.XPATH, '/html/body/div/div/form[2]/div/fieldset/div/div/button').click()
    time.sleep(1.5)
    
    nono = driver.current_url
    driver.find_element(By.XPATH, f'/html/body/div/div/form[2]/div/div[3]/table/tbody/tr[2]/td[4]/a').click()
    while driver.current_url == nono :
        print('page loading...')
    print('[CP] page loaded')
    time.sleep(3.5)

    actions = ActionChains(driver)  
    dropped = driver.find_element(By.XPATH, '//*[@id="target1"]/li[1]')
    finish = dropped.location
    size = dropped.size

    print()
    # if any app is existed in drop area,
    dropedApps = driver.find_element(By.ID, 'target1')
    LendropApps = len(dropedApps.find_elements(By.TAG_NAME, 'li'))
    
    if LendropApps >= 1 :
        print('if')
        print()
        for idx in range(1, LendropApps+1) :
            dragged = driver.find_element(By.XPATH, f'//*[@id="target1"]/li[{idx}]/span[2]')
            dropped = driver.find_element(By.XPATH, '//*[@id="candidate1"]')
            actions.move_to_element(dragged).click_and_hold().move_to_element(dropped).release().perform()

    for idx in range(2, 11) : 
        dragged = driver.find_element(By.XPATH, f'//*[@id="candidate1"]/li[{idx}]')
        text = driver.find_element(By.XPATH, f'//*[@id="candidate1"]/li[{idx}]/span[2]').text
        name, id = re.sub(r' \([^)]*\)', '', text), re.compile('\(([^)]+)').findall(text)[0]
        start = dragged.location
        
        print(f'[DEBUG] [HOME] -- CP : {name}, ID : {id}, start to drag and drop...')
        print(f'[DEBUG] [HOME] -- CP size : {size}')
        print(f"[DEBUG] [HOME] -- start location : {start}, finish location : {finish}, expected location : {finish['y']-start['y']}")
        
        actions.drag_and_drop_by_offset(dragged, finish['x']-start['x'], finish['y']-start['y']).perform()
        
        time.sleep(3.5)
        try:
            alert = Alert(driver)
            time.sleep(1)
            alert.accept() 
            print(f'[DEBUG] [HOME] -- Alert accepted. ')
        except NoAlertPresentException:
            print(f'[DEBUG] [HOME] -- Alert is not presented.')
            print()


driver = GetDriver(url)
AutoLogin(driver, USER_ID, USER_PW)
time.sleep(2.5)
Ordering(cpurl, driver)