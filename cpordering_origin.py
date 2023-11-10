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

# only for QA2 server-test to change data at dataframe 
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
    
    # <! -- pagination group --!> #
    Pagnation = list(driver.find_element(By.XPATH, '/html/body/div/div/form[2]/div/nav/ul').text)
    Pagelst = ''.join(Pagnation).split('\n')
    
    print(f'    [DEBUG] PageList : {Pagelst}')
    
    if 'Next' in Pagelst : 
        startpageidx = int(Pagelst[Pagelst.index('1')])
        endpageidx = int(Pagelst.index('Next')-1)

    else : 
        startpageidx = int(Pagelst[Pagelst.index('1')])
        endpageidx = int(Pagelst[-1])     
    
    print(f'    [DEBUG] Ready to set page from {startpageidx} to {endpageidx}')
    
    # ============================================================================================= #
    
    for page in range(startpageidx, endpageidx+1) :
        try :
            pageSelector = f'/html/body/div/div/form[2]/div/nav/ul/li[{page}]/a'
        except :
            pageSelector = '/html/body/div/div/form[2]/div/nav/ul/li/a'
            
        driver.find_element(By.XPATH, pageSelector).click()
        time.sleep(0.5)

        table = driver.find_element(By.XPATH, '/html/body/div/div/form[2]/div/div[3]/table/tbody')
        tr = len(table.find_elements(By.TAG_NAME, 'tr'))
        
        for num in range(1, tr+1) :
        # 1. Get country info
            country = driver.find_element(By.XPATH, f'/html/body/div/div/form[2]/div/div[3]/table/tbody/tr[{num}]/td[2]').text
            cpApp = getAppinfo(country)
            
            if cpApp.empty :
                print()
                print(f'    [DEBUG] : {country} DATABASE IS EMPTY !!')
                print()
                driver.back()
                continue  
            
            nono = driver.current_url
            driver.find_element(By.XPATH, f'/html/body/div/div/form[2]/div/div[3]/table/tbody/tr[{num}]/td[4]/a').click()
            while driver.current_url == nono :
                print('page loading...')
            print('[CP] page loaded')
            time.sleep(3.5)

        # 2. Home/Preminum area 
            cpAppHome = cpApp[cpApp['Order Type'] == 'HOME']
            cpAppPremium = cpApp[cpApp['Order Type'] == 'PREMIUM']
            
            cpApphomelst = cpAppHome[['App Name', 'App Id']].values.tolist()
            cpAppPremiumlst = cpAppPremium[['App Name', 'App Id']].values.tolist()

            
            cpAppHomedict = dict([(name, id) for name, id in zip(cpAppHome['App Name'], cpAppHome['App Id'])])
            cpAppPremiumdict = dict([(name, id) for name, id in zip(cpAppPremium['App Name'], cpAppPremium['App Id'])])
            cpAppOnlyPremiumdict = dict([(name, id) for name, id in cpAppPremiumlst if [name, id] not in cpApphomelst])
            
            print(f"[CP] [HOMEAREA] CP ORDERING FOR {country} : {cpAppHomedict}     ")
            print(f"[CP] [PREMINUM] CP ORDERING FOR {country} : {cpAppPremiumdict}  ")
            print(f"[CP] [ONLYPREMINUM] CP ORDERING FOR {country} : {cpAppOnlyPremiumdict}  ")
            print()
            
        # [exception] drop 하려는 앱들이 이미 cpApplist 에 있으면 pass ( 시간 단축 )
        # [HOME]
            dropApps = driver.find_element(By.ID, 'target1')
            dropAppslength = len(dropApps.find_elements(By.TAG_NAME, 'li'))
            beforedropAppslst = []
            afterdropApplst = []
            beforedropAppsdict = {}

            for idx in range(1, dropAppslength+1) :
                text = driver.find_element(By.XPATH, f'//*[@id="target1"]/li[{idx}]/span[2]').text
                name, id = re.sub(r' \([^)]*\)', '', text), re.compile('\(([^)]+)').findall(text)[0]
                beforedropAppslst.append([name, int(id)])
                beforedropAppsdict[name] = int(id)
                
                            
            dragApps = driver.find_element(By.ID, 'candidate1')
            dragAppslength = len(dragApps.find_elements(By.TAG_NAME, 'li'))
            

        # [PREMIUM]
            dropPMApps = driver.find_element(By.ID, 'target2')
            dropPMAppslength = len(dropPMApps.find_elements(By.TAG_NAME, 'li'))
            beforedropPMlst = []
            afterdropPMlst = []
            beforedropPMdict = {}
            
            for idx in range(1, dropPMAppslength+1) :
                text = driver.find_element(By.XPATH, f'//*[@id="target2"]/li[{idx}]/span[2]').text
                name, id = re.sub(r' \([^)]*\)', '', text), re.compile('\(([^)]+)').findall(text)[0]
                beforedropPMlst.append([name, int(id)])
                beforedropPMdict[name] = int(id)
                
            dragPMApps = driver.find_element(By.ID, 'candidate2')
            dragPMAppslength = len(dragPMApps.find_elements(By.TAG_NAME, 'li'))
            
            print(f'    [DEBUG] ORIGIN : {beforedropAppsdict},\n    [DEBUG] REVERSE : {dict(reversed(beforedropAppsdict.items()))}')
            print()
            # [exception] if cp which isn't in list is dropped area  (뺄때는 order 거꾸로 가야한다!!!) 부터 시작..
            for name, cp in dict(reversed(beforedropAppsdict.items())).items() :
                if name not in cpAppHomedict.keys() :

                    order = list(beforedropAppsdict.keys()).index(name) + 1
                    
                    print(f'    [DEBUG] [HOME] -- {name} SHOULD NOT BE HERE')
                    print(f'    [DEUBG] [HOME] -- {name} ({cp}) INDEX IS {order}')
                    
                    actions = ActionChains(driver)
                    
                    dragged = driver.find_element(By.XPATH, f'//*[@id="target1"]/li[{order}]/span[2]')
                    dropped = driver.find_element(By.XPATH, '//*[@id="candidate1"]')
                    
                    actions.move_to_element(dragged).click_and_hold().move_to_element(dropped).release().perform()

                    try :
                        alert = Alert(driver)
                        time.sleep(1)
                        alert.accept()
                        print(f'    [DEBUG] [HOME] -- Alert accepted. ')
                        print()
                        
                    except UnexpectedAlertPresentException:
                        alert.accept()
                        print(f'    [DEBUG] [HOME] -- Alert accepted. ')
                        print()
                        
                    except NoAlertPresentException:
                        print(f'    [DEBUG] [HOME] -- Alert is not presented.')
                        print()
                else :
                    print(f'    [DEUBG] [HOME] -- {name} do not need to be modified')
                    print()
                        
                time.sleep(1.5)
                
            
            
            drop2ndApps = driver.find_element(By.ID, 'target1')
            drop2ndAppslength = len(drop2ndApps.find_elements(By.TAG_NAME, 'li'))    
            before2ndDropAppsdict = {}
            
            for idx in range(1, drop2ndAppslength+1) :
                text = driver.find_element(By.XPATH, f'//*[@id="target1"]/li[{idx}]/span[2]').text
                name, id = re.sub(r' \([^)]*\)', '', text), re.compile('\(([^)]+)').findall(text)[0]
                before2ndDropAppsdict[name] = int(id)

            # HOME AREA (drag and drop)            
            for cp, cp_id in cpAppHomedict.items() :
                print(f'    [DEBUG] [HOME] -- Searcing : {cp}, {cp_id} ...')
        
                # [exception] if cp to drop is already existed
                if (cp, cp_id) in beforedropAppsdict.items() :
                    print(f'[TEST] [{cp}, {cp_id}] do not need to be dropped')
                    print()
                    continue
                
                # [exception] if cp to drop is already existed, But cp_id is wrong 
                if cp in before2ndDropAppsdict.keys() and cp_id != before2ndDropAppsdict[cp] :
                    print(f'    [DEBUG] [HOME] -- : {before2ndDropAppsdict}, {before2ndDropAppsdict.keys()}')
                    order = list(before2ndDropAppsdict.keys()).index(cp) + 1
                    print(f'    [DEBUG] [HOME] -- : {cp} ORDER == {order}')
                    actions = ActionChains(driver)

                    # caution of contact info
                    dragged = driver.find_element(By.XPATH, f'//*[@id="target1"]/li[{order}]/span[2]')
                    dropped = driver.find_element(By.XPATH, '//*[@id="candidate1"]')
                    
                    start = dragged.location
                    finish = dropped.location
                    
                    print(f'    [DEBUG] [HOME] -- start location : {start}, finish location : {finish} ')
                    actions.move_to_element(dragged).click_and_hold().move_to_element(dropped).release().perform()
                    try :
                        alert = Alert(driver)
                        time.sleep(1)
                        alert.accept()
                        print(f'    [DEBUG] [HOME] -- Alert accepted. ')
                        print() 
                        
                    except NoAlertPresentException:
                        print(f'    [DEBUG] [HOME] -- Alert is not presented.')
                        print()
                        
                    print(f'[TEST] Complete to Drag and Drop of {cp} ...')

                for idx in range(1, dragAppslength+1) :
                    text = driver.find_element(By.XPATH, f'//*[@id="candidate1"]/li[{idx}]/span[2]').text
                    id_regex = re.compile('\(([^)]+)')
                    cpid = id_regex.findall(text)[0]
                    title= re.sub(r' \([^)]*\)', '', text)

                    if str(cp_id) == str(cpid) :
                        print(f'    [DEBUG] [HOME] -- [ {cp} ({cp_id}) ] == [ {title} ({cpid}) ] ----------   ')
                        actions = ActionChains(driver)
                        print(f'[TEST] Drag and Drop of {cp} : {cpid} ......')
                        
                        # [exception] if cp to drop is already existed
                        try :
                            dragged = driver.find_element(By.XPATH, f'//*[@id="candidate1"]/li[{idx}]')
                        except :
                            print('    [DEBUG] [HOME] -- already existed in dropped area or have to check something regarding cp to try dragging')
                            break
                        else :
                            dropped = driver.find_element(By.XPATH, '//*[@id="target1"]')
                            
                            start = dragged.location
                            finish = dropped.location
                    
                            print(f'    [DEBUG] [HOME] -- start location : {start}, finish location : {finish} ')
                            actions.move_to_element(dragged).click_and_hold().move_to_element(dropped).release().perform()
                            time.sleep(1.5)
                            print(f'[TEST] Complete to Drag and Drop of {cp} ...')
                            # cp moved
                            break
                        
                time.sleep(3) # just check if drag and drop test is passed or not.
                
                
                
            # PREMIUM AREA (drag and drop)
            # [exception] if home == premium ? pass
            if cpAppOnlyPremiumdict == {}  : # O(1)
                print()
                print("    [DEBUG] [PREMIUM] -- THERE IS NO NEED TO DRAG AND DROP CASE, HOME APPS == PREMIUM APPS")
                print()

            else :
                for cp, cpid in cpAppOnlyPremiumdict.items() :
                    
                    # [exception] if cp to drop is already existed
                    if (cp, cpid) in beforedropPMdict.items() :
                        print(f'[TEST] [{cp}, {cp_id}] do not need to be dropped')
                        print()
                        continue
                    
                    # [exception] if cp to drop is already existed, But cp_id is wrong  
                    if cp in beforedropPMdict.keys() and cpid != beforedropPMdict[cp] :
                        print(f'    [DEBUG] [PREMIUM] -- : {beforedropPMdict}, {beforedropPMdict.keys()}')
                        order = list(beforedropPMdict.keys()).index(cp) + 1
                        print(f'    [DEBUG] [PREMIUM] -- : {cp} ORDER == {order}')
                        actions = ActionChains(driver)

                        dragged = driver.find_element(By.XPATH, f'//*[@id="target2"]/li[{order}]/span[2]')
                        dropped = driver.find_element(By.XPATH, '//*[@id="candidate2"]')
                        
                        actions.move_to_element(dragged).click_and_hold().move_to_element(dropped).release().perform()
                        alert = Alert(driver)
                        if alert :
                            alert.accept()
                        time.sleep(1.5)
                        
                        print(f'[TEST] Complete to Drag and Drop of {cp} ...')
                        print()
                        
                    # [exception] if cp which isn't in list is dropped area
                        
                    for idx in range(1, dragPMAppslength+1) :
                        text = driver.find_element(By.XPATH, f'//*[@id="target2"]/li[{idx}]/span[2]').text
                        name, dragid = re.sub(r' \([^)]*\)', '', text), re.compile('\(([^)]+)').findall(text)[0]

                        if str(dragid) == str(cpid) :
                            print(f'    [DEBUG] [PREMIUM] -- [ {cp} ({cpid}) ] == [ {name} ({dragid}) ] ----------   ')
                            print(f'[TEST] Drag and Drop of {name} : {dragid} ......')
                            
                            actions = ActionChains(driver)
                            
                            # [exception] if cp to drop is already existed again?
                            try :
                                dragged = driver.find_element(By.XPATH, f'//*[@id="candidate2"]/li[{idx}]')
                            except :
                                print('    [DEBUG] [PREMIUM] -- already existed in dropped area or have to check something regarding cp to try dragging')
                                break
                            else : 
                                dropped = driver.find_element(By.XPATH, '//*[@id="target2"]')
                                actions.move_to_element(dragged).click_and_hold().move_to_element(dropped).release().perform()
                                time.sleep(1.5)
                                print(f'[TEST] Complete to Drag and Drop of {cp} ...')
                                # cp moved
                                break
                    
                    time.sleep(3) # just check if drag and drop test is passed or not.            
                    
        # 3. Verify database and draaged area.   
            dropApps = driver.find_element(By.ID, 'target1')
            dropAppslength = len(dropApps.find_elements(By.TAG_NAME, 'li'))
            
            dropPMApps = driver.find_element(By.ID, 'target2')
            dropPMAppslength = len(dropPMApps.find_elements(By.TAG_NAME, 'li'))
            
            for idx in range(1, dropAppslength+1) :
                text = driver.find_element(By.XPATH, f'//*[@id="target1"]/li[{idx}]/span[2]').text
                name, id = re.sub(r' \([^)]*\)', '', text), re.compile('\(([^)]+)').findall(text)[0]
                afterdropApplst.append([name, int(id)])
                
            for idx in range(1, dropPMAppslength+1) :
                text = driver.find_element(By.XPATH, f'//*[@id="target2"]/li[{idx}]/span[2]').text
                name, id = re.sub(r' \([^)]*\)', '', text), re.compile('\(([^)]+)').findall(text)[0]
                afterdropPMlst.append([name, int(id)])
                
            # ! --- compare --- !
            print()
            print(f'    [DEUBG] ========================================================================================================================= ')
            print(f'    [HOME] Database : {cpApphomelst} \n    [HOME] dropApplst : {afterdropApplst} \n')
            print(f'    [PREM] Database : {cpAppPremiumlst} \n    [PREM] dropApplst : {afterdropPMlst} ')
            print(f'    ================================================================================================================================= ')
            
            print()
            
            if cpApphomelst == afterdropApplst and cpAppPremiumlst == afterdropPMlst :
                print(f'[CP] {time.ctime()} : MATCHING ')
                # database와 matching 이 된다면, confirm 로 status 변경해줘야함 까지가 마무리 단계!
                driver.find_element(By.XPATH, '//*[@id="orderingForm"]/div[2]/div[8]/div[2]/button[1]').click()
                time.sleep(0.5)
                driver.find_element(By.XPATH, '//*[@id="popup-todayChangeList"]/div/div/div[3]/button').click()
                time.sleep(0.5)
                #show up pop-up
                alert = Alert(driver)
                alert.accept()
                
                print(f'[CP] {country} Ordering has been comfirmed')
                print()
                
            else :
                print(f'[RESULT] {time.ctime()} : UNMATCHING ')
                print()
                
            time.sleep(3.5)
            driver.back()

driver = GetDriver(url)
AutoLogin(driver, USER_ID, USER_PW)
time.sleep(2.5)
Ordering(cpurl, driver)