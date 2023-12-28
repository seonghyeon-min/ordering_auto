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


# --- this server is only for QA2 --- #
# [caution] Appid is different between QA2 and Prod Server 
cautionCP4smnt = {
    'YoutubeTV' : 95384,
    'Youtubesmnt' : 357640,
}

# --- FUNCTION FREQUENTLY --- #
def ClickEvent(driver, contribute, path) :
    driver.find_element(contribute, path).click()
    
def SendKeyEvent(driver, contribute, path) :
    driver.find_element(contribute, path).send_keys(Keys.CONTROL, 'v')
    

# --- Get App standard ordering dataframe --- #
def getAppinfo(country) :
    Appdf = pd.read_excel(r"C:\Users\test\Downloads\Ordering List_for_test.xls", index_col=False) 
    CountryOrdering = Appdf[Appdf['Country Name'] == country][['Country Name', 'Order Type', 'App Name', 'App Id', 'Order Number']].reset_index(drop=True)
    
    # scale Appid only for webos23 platform 
    if 'webOSTV 23' in PlatformCode.split('-') :
        replace_to = {cautionCP4smnt['YoutubeTV'] : cautionCP4smnt['Youtubesmnt']}
        CountryOrdering = CountryOrdering.replace(replace_to)
        print(f"{time.ctime()} [DEBUG] COMPLETE TO SCALE JOB")
    print("[DATAFRAME] -- SHOW DATAFRAME OF CP ORDERING -- ")
    print(CountryOrdering)
    print()

    return CountryOrdering

# --- driver object get --- #
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
    # --- input Platform code --- #
    # pyperclip.copy(PlatformCode)
    # SendKeyEvent(driver, By.XPATH, '/html/body/div/div/form[2]/div/fieldset/div/table/tbody/tr[1]/td/span/div/ul/li[1]/div/input')
    idx = -1
    PlatformLength = len(driver.find_element(By.XPATH, '/html/body/div/div/form[2]/div/fieldset/div/table/tbody/tr[1]/td/span/div/ul').find_elements(By.TAG_NAME, 'li'))
    print(f'{time.ctime()} [DEBUG] Current time')
    for num in range(2, PlatformLength+1) :
        CandPlatformCode = driver.find_element(By.XPATH, f'/html/body/div/div/form[2]/div/fieldset/div/table/tbody/tr[1]/td/span/div/ul/li[{num}]/a/label').text
        if PlatformCode == CandPlatformCode :
            idx = num
            print(f'{time.ctime()} [DEBUG] ProductPlatformCode : {PlatformCode}({idx}), FOUND')
            break
    if idx == -1 :
        print(f'{time.ctime()} [DEBUG] ProductPlatformCode IS NOT EXISTED.')
        exit()    
    time.sleep(1.5)
    # /html/body/div/div/form[2]/div/fieldset/div/table/tbody/tr[1]/td/span/div/ul/li[28]/a/label
    ClickEvent(driver, By.XPATH, f'/html/body/div/div/form[2]/div/fieldset/div/table/tbody/tr[1]/td/span/div/ul/li[{idx}]/a/label')
    ClickEvent(driver, By.XPATH, '/html/body/div/div/form[2]/div/div[1]/h3')
    ClickEvent(driver, By.XPATH, '/html/body/div/div/form[2]/div/fieldset/div/table/tbody/tr[3]/td[1]/select')
    # ClickEvent(driver, By.XPATH, '/html/body/div/div/form[2]/div/fieldset/div/table/tbody/tr[3]/td[1]/select/option[1]') #request
    ClickEvent(driver, By.XPATH, '/html/body/div/div/form[2]/div/fieldset/div/table/tbody/tr[3]/td[1]/select/option[2]') #draft    
    ClickEvent(driver, By.XPATH, '/html/body/div/div/form[2]/div/div[2]/div[1]/select')
    ClickEvent(driver, By.XPATH, '/html/body/div/div/form[2]/div/div[2]/div[1]/select/option[7]')

    # ClickEvent(driver, By.XPATH, '/html/body/div/div/form[2]/div/fieldset/div/div/button')
    time.sleep(1.5)

    # --- PAGINATION GROUP --- #
    Pagnation = list(driver.find_element(By.XPATH, '/html/body/div/div/form[2]/div/nav/ul').text)
    Pagelst = ''.join(Pagnation).split('\n')
    
    print(f'{time.ctime()} [DEBUG] PageList : {Pagelst}')
    
    if 'Next' in Pagelst : 
        startpageidx = int(Pagelst[Pagelst.index('1')])
        endpageidx = int(Pagelst.index('Next')-1)

    else : 
        startpageidx = int(Pagelst[Pagelst.index('1')])
        endpageidx = int(Pagelst[-1])     
    
    print(f'{time.ctime()} [DEBUG] Ready to set page from {startpageidx} to {endpageidx}')
    
    for page in range(startpageidx, endpageidx+1) :
        try :
            pageSelector = f'/html/body/div/div/form[2]/div/nav/ul/li[{page}]/a'
        except :
            pageSelector = '/html/body/div/div/form[2]/div/nav/ul/li/a'
            
        ClickEvent(driver, By.XPATH, pageSelector)
        time.sleep(0.5)

        tr = len(driver.find_element(By.XPATH, '/html/body/div/div/form[2]/div/div[3]/table/tbody').find_elements(By.TAG_NAME, 'tr'))       
        
        for num in range(tr, 0, -1) :
            time.sleep(2.5)
            country = driver.find_element(By.XPATH, f'/html/body/div/div/form[2]/div/div[3]/table/tbody/tr[{num}]/td[2]').text
            cpApp = getAppinfo(country)
            
            if cpApp.empty :
                print()
                print(f'{time.ctime()} [DEBUG] : {country} DATABASE IS EMPTY !!')
                print()
                continue 
            
            currentwindow = driver.current_url
            ClickEvent(driver, By.XPATH, f'/html/body/div/div/form[2]/div/div[3]/table/tbody/tr[{num}]/td[4]/a')
            while driver.current_url == currentwindow :
                print('page loading...')
            print(f'{time.ctime()} [CP] page loaded')
            print()
            time.sleep(3.5)
            
            # --- SPLIT DATAFRAME TO HOME, PREMIUM --- #
            cpAppHome = cpApp[cpApp['Order Type']== 'HOME']
            cpAppPremium = cpApp[cpApp['Order Type'] == 'PREMIUM']
            
            cpAppHomelst = cpAppHome[['App Name', 'App Id']].values.tolist()
            cpAppPremiumlst = cpAppPremium[['App Name', 'App Id']].values.tolist()
            
            cpAppHomedict = dict([(name, id) for name, id in zip(cpAppHome['App Name'], cpAppHome['App Id'])])
            cpAppPremiumdict = dict([(name, id) for name, id in zip(cpAppPremium['App Name'], cpAppPremium['App Id'])])    
            cpAppOnlyPredict = dict([(name, id) for name, id in cpAppPremiumdict.items() if [name, id] not in cpAppHomelst])
            
            print(f"{time.ctime()} [DEBUG] [HOME] CP ORDERING FOR {country} : {cpAppHomedict}")
            print(f"{time.ctime()} [DEBUG] [PREMIUM] CP ORDERING FOR {country} : {cpAppPremiumdict}")
            print(f"{time.ctime()} [DEBUG] [onlyPREMIUM] CP ORDERING FOR {country} : {cpAppOnlyPredict}")
        
            print()
            
            # --- START TO DRAG AND DROP EVENT --- #
            actions = ActionChains(driver)
            dropedApps = driver.find_element(By.ID, 'target1')
            dropArea = driver.find_element(By.XPATH, '//*[@id="candidate1"]')
            LendropApps = len(dropedApps.find_elements(By.TAG_NAME, 'li'))
            
            if LendropApps >= 1 : # if any apps are existed at target area, move them to candidate area after verifying..
                PreVerifyAppslst = []
                print()
                print(f'{time.ctime()} [DEBUG] [HOME] PREVERIFY WHETHER APPS SHOULD BE MOVED TO CANDIDATE AREA OR NOT')
                for idx in range(1, LendropApps+1) :
                    text = driver.find_element(By.XPATH, f'//*[@id="target1"]/li[{idx}]/span[2]').text
                    name, id = re.sub(r' \([^)]*\)', '', text), re.compile('\(([^)]+)').findall(text)[0]
                    PreVerifyAppslst.append([name, int(id)])
                
                if PreVerifyAppslst == cpAppHomelst :
                    print(f'{time.ctime()} [DEBUG] [HOME] THERE IS NO NEED TO DO THIS JOB !!')
                    driver.find_element(By.XPATH, '//*[@id="orderingForm"]/div[2]/div[8]/div[2]/button[1]').click()
                    time.sleep(0.5)
                    alert = Alert(driver)
                    alert.accept() # text : 
                    time.sleep(0.5)
                    alert.accept() # text : 
                    print(f'{time.ctime()} [CP] {country} Ordering has been comfirmed')
                    print()
                    continue
                
                else :
                    for idx in range(LendropApps, 0, -1):
                        print('{time.ctime()} [DEBUG] [HOME] MOVE APPS TO CANDIDATE AREA')
                        dragged = driver.find_element(By.XPATH, f'//*[@id="target1"]/li[{idx}]/span[2]')
                        actions.move_to_element(dragged).click_and_hold().move_to_element(dropArea).release().perform()
                        
                        try :
                            alert = Alert(driver)
                            time.sleep(1)
                            alert.accept()
                            print('{time.ctime()} [DEBUG] [HOME] ALERT HAS HAPPENED AND ACCEPTED')
                            print()
            
                        except NoAlertPresentException :
                            print('{time.ctime()} [DEBUG] [HOME] ALERT HAS NOT BEEN PRESENTED')
                            print()
                    
                    candidateLength = len(driver.find_element(By.ID, 'candidate1').find_elements(By.TAG_NAME, 'li'))
                    targetCPlength = len(cpAppHomedict)    
                    
                    if targetCPlength > 5 :
                        candidateCPdict = dict()
                        for cp, id in dict(list(cpAppHomedict.items())[:4]).items() :
                            candidateCPdict[cp] = id
                        for cp, id in dict(list(cpAppHomedict.items())[:3:-1]).items():
                            candidateCPdict[cp] = id
                            
                        cpAppHomedict = candidateCPdict
                    
                    print(f'{time.ctime()} [DEBUG] GET READY TO SET DROPPPING AND DROPPING')
                    print(f'{time.ctime()} [DEBUG] STANDARD DATABASE : {cpAppHomedict} ')
                    print()
            
        
            # --- HOME --- #
                    for cp, cp_id in cpAppHomedict.items() :
                        print(f'{time.ctime()} [DEBUG] [HOME] {cp}({cp_id}), START TO DRAG AND DROP')
                        
                        for idx in range(1, candidateLength+1) :
                            text = driver.find_element(By.XPATH, f'//*[@id="candidate1"]/li[{idx}]/span[2]').text
                            name, id = re.sub(r' \([^)]*\)', '', text), re.compile('\(([^)]+)').findall(text)[0]
                    
                            if name == cp and str(id) == str(cp_id) : 
                                print(f'{time.ctime()} [DEBUG] [HOME] Found {name}({id})')
                                actions = ActionChains(driver)
                                dragged = driver.find_element(By.XPATH, f'//*[@id="candidate1"]/li[{idx}]/span[2]')
                                dropped = driver.find_element(By.XPATH, '//*[@id="target1"]')
                                actions.move_to_element(dragged).click_and_hold().move_to_element(dropped).release().perform()

                                alert = Alert(driver)
                                time.sleep(1)
                                try :
                                    alert.accept()
                                    print(f'{time.ctime()} [DEBUG] [HOME] -- Alert accepted. ')
                                    print(f'{time.ctime()} [DEBUG] [HOME] -- {name}({id}) Dropped')
                                    
                                except NoAlertPresentException:
                                    print(f'{time.ctime()} [DEBUG] [HOME] -- Alert is not presented.')
                                    print()
                                    
                                break
                    
            # --- PREMIUM --- #
            dropPremiumArea = driver.find_element(By.XPATH, '//*[@id="candidate2"]')
            premiumlength = len(driver.find_element(By.XPATH, '//*[@id="target2"]').find_elements(By.TAG_NAME, 'li'))
            candidatePremiumlength = len(driver.find_element(By.XPATH, '//*[@id="candidate2"]').find_elements(By.TAG_NAME, 'li'))   
    
            if cpAppOnlyPredict == {} :
                print()
                print("{time.ctime()} [DEBUG] [PREMIUM] -- THERE IS NO NEED TO DRAG AND DROP CASE, HOME APPS == PREMIUM APPS")
                print()
                
            else :
                for idx in range(premiumlength, targetCPlength, -1) :
                    dragged = driver.find_element(By.XPATH, f'//*[@id="target2"]/li[{idx}]/span[2]')
                    actions.move_to_element(dragged).click_and_hold().move_to_element(dropPremiumArea).release().perform()
                    try :
                        alert = Alert(driver)
                        time.sleep(1)
                        alert.accept()
                        print(f'{time.ctime()} [DEBUG] [PREMIUM] -- Alert accepted. ')
                            
                    except NoAlertPresentException:
                        print(f'{time.ctime()} [DEBUG] [PREMIUM] -- Alert is not presented.')
                        print()
                        
                        
                for cp, cp_id in cpAppOnlyPredict.items() :
                    print(f'{time.ctime()} [DEBUG] [PREMIUM] {cp}({cp_id}), START TO DRAG AND DROP')
                    
                    for idx in range(1, candidatePremiumlength+1) :
                        text = driver.find_element(By.XPATH, f'//*[@id="candidate2"]/li[{idx}]/span[2]').text
                        name, id = re.sub(r' \([^)]*\)', '', text), re.compile('\(([^)]+)').findall(text)[0]
                        
                        if name == cp and str(id) == str(cp_id) : 
                            print(f'{time.ctime()} [DEBUG] [PREMIUM] Found {name}({id})')
                            actions = ActionChains(driver)
                            dragged = driver.find_element(By.XPATH, f'//*[@id="candidate2"]/li[{idx}]/span[2]')
                            dropped = driver.find_element(By.XPATH, '//*[@id="target2"]')
                            actions.move_to_element(dragged).click_and_hold().move_to_element(dropped).release().perform()

                            alert = Alert(driver)
                            time.sleep(1)
                            try :
                                alert.accept()
                                print(f'{time.ctime()} [DEBUG] [PREMIUM] -- Alert accepted. ')
                                print(f'{time.ctime()} [DEBUG] [PREMIUM] -- {name}({id}) Dropped')
                                
                            except NoAlertPresentException:
                                print(f'{time.ctime()} [DEBUG] [PREMIUM] -- Alert is not presented.')
                                print()
                                
                            break
                        
                        
            # --- Verify --- #
            dropAppslength = len(driver.find_element(By.ID, 'target1').find_elements(By.TAG_NAME, 'li'))
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
            print(f'{time.ctime()} [DEBUG] \n')
            print(f'[HOME] Database : {cpAppHomelst} \n[HOME] dropApplst : {afterdropHomeApplst} \n')
            print(f'[PREMIUM] Database : {cpAppPremiumlst} \n[PREMIUM] dropApplst : {afterdropPreApplst} \n')
            print()
            
            if cpAppHomelst == afterdropHomeApplst and cpAppPremiumlst == afterdropPreApplst:
                print(f'[CP] {time.ctime()} : MATCHING ')
                # driver.find_element(By.XPATH, '//*[@id="orderingForm"]/div[2]/div[8]/div[1]/button[3]').click() # save
                driver.find_element(By.XPATH, '//*[@id="orderingForm"]/div[2]/div[8]/div[2]/button[1]').click() # confirm
                time.sleep(0.5)
                driver.find_element(By.XPATH, '//*[@id="popup-todayChangeList"]/div/div/div[3]/button').click()
                time.sleep(0.5)
                #show up pop-up
                alert = Alert(driver)
                alert.accept()
                print(f'[CP] {time.ctime()} {country} Ordering has been comfirmed')
                print()
                    
            else :
                print(f'[RESULT] {time.ctime()} : UNMATCHING ')
                print()
                
            time.sleep(2.5)
            driver.back()
                    
driver = GetDriver(url)
AutoLogin(driver, USER_ID, USER_PW)
time.sleep(2.5)
Ordering(cpurl, driver)
