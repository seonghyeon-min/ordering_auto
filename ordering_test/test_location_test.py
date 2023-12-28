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
    print("[DEBUG] -- SHOW DATAFRAME OF CP ORDERING -- ")
    print()
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
    country = driver.find_element(By.XPATH, f'/html/body/div/div/form[2]/div/div[3]/table/tbody/tr[2]/td[2]').text
    cpAppdf = getAppinfo(country)
    
    # cp App DataFrame
    cpAppHome = cpAppdf[cpAppdf['Order Type'] == 'HOME']
    cpAppPremium = cpAppdf[cpAppdf['Order Type'] == 'PREMIUM']
    
    cpAppHomelst = cpAppHome[['App Name', 'App Id']].values.tolist()
    cpAppPremiumlst = cpAppPremium[['App Name', 'App Id']].values.tolist()
    
    cpAppHomedict = dict([(name, id) for name, id in zip(cpAppHome['App Name'], cpAppHome['App Id'])])
    cpAppPremiumdict = dict([(name, id) for name, id in zip(cpAppPremium['App Name'], cpAppPremium['App Id'])])    
    cpAppOnlyPredict = dict([(name, id) for name, id in cpAppPremiumdict.items() if [name, id] not in cpAppHomelst])
    
    print(f"[DEBUG] [HOME] CP ORDERING FOR {country} : {cpAppHomedict}")
    print(f"[DEBUG] [PREMIUM] CP ORDERING FOR {country} : {cpAppPremiumdict}")
    print(f"[DEBUG] [onlyPREMIUM] CP ORDERING FOR {country} : {cpAppOnlyPredict}")
    
    nono = driver.current_url
    driver.find_element(By.XPATH, f'/html/body/div/div/form[2]/div/div[3]/table/tbody/tr[2]/td[4]/a').click()
    while driver.current_url == nono :
        print('page loading...')
    print('[CP] page loaded')
    time.sleep(3.5)

    print()
    
    # if any app is existed in Home drop area,
    actions = ActionChains(driver)  
    dropedApps = driver.find_element(By.ID, 'target1')
    dropArea = driver.find_element(By.XPATH, '//*[@id="candidate1"]')
    LendropApps = len(dropedApps.find_elements(By.TAG_NAME, 'li'))
    
    if LendropApps >= 1 :
        print('[DEBUG] [HOME] REVERT')
        print()
        for idx in range(1, LendropApps+1) :
            dragged = driver.find_element(By.XPATH, f'//*[@id="target1"]/li[{idx}]/span[2]')
            actions.move_to_element(dragged).click_and_hold().move_to_element(dropArea).release().perform()
            
            try :
                alert = Alert(driver)
                time.sleep(1)
                alert.accept()
                print(f'[DEBUG] [HOME] -- Alert accepted. ')
                    
            except NoAlertPresentException:
                print(f'[DEBUG] [HOME] -- Alert is not presented.')
                print()
            
    # # fisrt app dropped at target area.
    # dropFirstApps = driver.find_element(By.XPATH, '//*[@id="candidate1"]/li[1]/span[2]')
    # actions.move_to_element(dropFirstApps).click_and_hold().move_to_element(dropedApps).release().perform()

    candidateLength = len(driver.find_element(By.ID, 'candidate1').find_elements(By.TAG_NAME, 'li'))
    targetCPlength = len(cpAppHomedict)    
    
    if targetCPlength > 5 :
        candidateCPdict = dict()
        for cp, id in dict(list(cpAppHomedict.items())[:4]).items() :
            candidateCPdict[cp] = id
        
        for cp, id in dict(list(cpAppHomedict.items())[:3:-1]).items():
            candidateCPdict[cp] = id
        
        
        cpAppHomedict = candidateCPdict
        
        print(f'[DEBUG] SET TO DROP AND DROP DATABASE')
        print(f'[DEBUG] DATABASE : {candidateCPdict} ')
        print()

    # Home area
    for cp, cp_id in cpAppHomedict.items():
        print(f'[DEBUG] [HOME] -- CP : {cp}, ID : {cp_id}, start to drag and drop...')
        
        for idx in range(1, candidateLength+1) :
            text = driver.find_element(By.XPATH, f'//*[@id="candidate1"]/li[{idx}]/span[2]').text
            name, id = re.sub(r' \([^)]*\)', '', text), re.compile('\(([^)]+)').findall(text)[0]
            
            if name == cp and str(id) == str(cp_id) : 
                print(f'[DEBUG] [HOME] Found {name}({id}) to drag and drop at target area')
                actions = ActionChains(driver)
                dragged = driver.find_element(By.XPATH, f'//*[@id="candidate1"]/li[{idx}]/span[2]')
                dropped = driver.find_element(By.XPATH, '//*[@id="target1"]')
                actions.move_to_element(dragged).click_and_hold().move_to_element(dropped).release().perform()

                print(f'[DEBUG] [HOME] Dragged size : {dragged.size}')
                alert = Alert(driver)
                time.sleep(1)
                try :
                    alert.accept()
                    print(f'[DEBUG] [HOME] -- Alert accepted. ')
                    print(f'[DEBUG] [HOME] -- {name}({id}) Dropped')
                    
                except NoAlertPresentException:
                    print(f'[DEBUG] [HOME] -- Alert is not presented.')
                    print()
                    
                break
    
    # Premium area
    dropPremiumArea = driver.find_element(By.XPATH, '//*[@id="candidate2"]')
    premiumlength = len(driver.find_elements(By.XPATH, '//*[@id="target2"]').find_element(By.TAG_NAME, 'li'))
    candidatePremiumlength = len(driver.find_elements(By.XPATH, '//*[@id="candidate2"]').find_element(By.TAG_NAME, 'li'))   
    
    if cpAppOnlyPredict == {} :
        print()
        print("[DEBUG] [PREMIUM] -- THERE IS NO NEED TO DRAG AND DROP CASE, HOME APPS == PREMIUM APPS")
        print()

    else : 
        # check Apps where they were dropped at the premium area,
        for idx in range(targetCPlength+1, premiumlength+1) :
            dragged = driver.find_element(By.XPATH, f'//*[@id="target2"]/li[{idx}]/span[2]')
            actions.move_to_element(dragged).click_and_hold().move_to_element(dropPremiumArea).release().perform()
            try :
                alert = Alert(driver)
                time.sleep(1)
                alert.accept()
                print(f'[DEBUG] [HOME] -- Alert accepted. ')
                    
            except NoAlertPresentException:
                print(f'[DEBUG] [HOME] -- Alert is not presented.')
                print()
    
        for cp, cp_id in cpAppOnlyPredict.items() :
            print(f'[DEBUG] [PREMIUM] -- CP : {cp}, ID : {cp_id}, start to drag and drop...')
            
            for idx in range(1, candidatePremiumlength+1) :
                text = driver.find_element(By.XPATH, f'//*[@id="candidate2"]/li[{idx}]/span[2]').text
                name, id = re.sub(r' \([^)]*\)', '', text), re.compile('\(([^)]+)').findall(text)[0]
                
                if name == cp and str(id) == str(cp_id) : 
                    print(f'[DEBUG] [PREMIUM] Found {name}({id}) to drag and drop at target area')
                    actions = ActionChains(driver)
                    dragged = driver.find_element(By.XPATH, f'//*[@id="candidate2"]/li[{idx}]/span[2]')
                    dropped = driver.find_element(By.XPATH, '//*[@id="target2"]')
                    actions.move_to_element(dragged).click_and_hold().move_to_element(dropped).release().perform()

                    alert = Alert(driver)
                    time.sleep(1)
                    try :
                        alert.accept()
                        print(f'[DEBUG] [PREMIUM] -- Alert accepted. ')
                        print(f'[DEBUG] [PREMIUM] -- {name}({id}) Dropped')
                        
                    except NoAlertPresentException:
                        print(f'[DEBUG] [PREMIUM] -- Alert is not presented.')
                        print()
                        
                    break
                
    # Verfiy 
    dropApps = driver.find_element(By.ID, 'target1')
    dropAppslength = len(dropApps.find_elements(By.TAG_NAME, 'li'))
    afterdropHomeApplst = []
    
    dropPreAppsLength = len(driver.find_element(By.XPATH, '//*[@id="target2"]').find_elements(By.TAG_NAME, 'li'))
    afterdropPreApplst = []
    
    for idx in range(1, dropAppslength+1) :
        text = driver.find_element(By.XPATH, f'//*[@id="target1"]/li[{idx}]/span[2]').text
        name, id = re.sub(r' \([^)]*\)', '', text), re.compile('\(([^)]+)').findall(text)[0]
        afterdropHomeApplst.append([name, int(id)])
        
    for idx in range(1, dropPreAppsLength+1) :
        text = driver.find_element(By.XPATH, f'//*[@id="target2"]/li[{idx}]/span[2]').text
        name, id = re.sub(r' \([^)]*\)', '', text), re.compile('\(([^)]+)').findall(text)[0]        
        afterdropPreApplst.append([name, int(id)])        
        
    print()
    print(f'[DEUBG] ========================================================================================================================= ')
    print(f'[HOME] Database : {cpAppHomelst} \n[HOME] dropApplst : {afterdropHomeApplst} \n')
    print(f'[PREMIUM] Database : {cpAppPremiumlst} \n[PREMIUM] dropApplst : {afterdropPreApplst} \n')
    print()
    
    if cpAppHomelst == afterdropHomeApplst and  cpAppPremiumlst == afterdropPreApplst:
        print(f'[CP] {time.ctime()} : MATCHING ')
        # driver.find_element(By.XPATH, '//*[@id="orderingForm"]/div[2]/div[8]/div[2]/button[1]').click()
        # time.sleep(0.5)
        # driver.find_element(By.XPATH, '//*[@id="popup-todayChangeList"]/div/div/div[3]/button').click()

        # time.sleep(0.5)
        # #show up pop-up
        # alert = Alert(driver)
        # alert.accept()
        print(f'[CP] {country} Ordering has been comfirmed')
        print()
            
    else :
        print(f'[RESULT] {time.ctime()} : UNMATCHING ')
        print()

driver = GetDriver(url)
AutoLogin(driver, USER_ID, USER_PW)
time.sleep(2.5)
Ordering(cpurl, driver)