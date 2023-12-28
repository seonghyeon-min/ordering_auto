import os, sys
import time
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from OrderingFunc import *

GUI_FILE_NAME = 'gui'
os.system('python -m PyQt5.uic.pyuic -x ' + GUI_FILE_NAME + '.ui -o ' + GUI_FILE_NAME + '.py')

from gui import Ui_MainWindow
from pandasModel import *

# USER_ID = 'seonghyeon.min'
# USER_PW = 'alstjdgus@4416'
# QA2
url = 'http://qt2-kic.smartdesk.lge.com/admin/main.lge?serverType=QA2'
cpurl = 'http://qt2-kic.smartdesk.lge.com/admin/master/ordering/ordering/retrieveAppOrderingList.lge?serverType=QA2'

# --- this test.py is only for QA2 SERVER --- #
# [caution] Appid is different between QA2 and Prod Server 
cautionCP4smnt = {
    'YoutubeTV' : 95384,
    'Youtubesmnt' : 357640,
}
    
class Form(QMainWindow, Ui_MainWindow) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        self.viewDataFrame = pd.DataFrame()
        
        # ---- signal ---- #
        self.btnOpen.clicked.connect(self.openFile)
        self.btnWork.clicked.connect(self.workOrdering)
        self.btnVerify.clicked.connect(self.Verify)
        self.btnClose.clicked.connect(self.Close)

    def Viewdf(self) :
        pass

    def openFile(self):
        show_filter = "All File(*.*);;txt File(*.txt);;Excel File(*.xlsx);;Excel File(*.xls)"
        init_filter = "All File(*.*)"
        opt = QFileDialog.Option()
        filepath, filter_type = QFileDialog.getOpenFileName(filter=show_filter, initialFilter=init_filter, options=opt)
        file_name = filepath
        if file_name == '' :
            QMessageBox.warning(self, 'FileNotFoundError', 'Please Select the File.')
            return 
        self.Appdf = pd.read_excel(file_name, index_col=False)
        QMessageBox.information(self, 'Completion', 'It is ready to do Ordering. \nyou can press the "Ordering" button')
        
    def VerifyDataframe(self, df):
        workdf = df
        workdf['Result'] = np.where((workdf['TV_App Name'] == workdf['SMNT_App Name']) & (workdf['TV_App Id'] == workdf['SMNT_App Id']), 'True', 'False')
        
        return workdf
    
    def workOrdering(self):
        # --- platform code check --- #
        if self.platline.text() == '' or self.accountline.text() == '' or self.pwline.text() == '' :
            QMessageBox.warning(self, 'Error', 'Please Fill out Platform code, SDP Account')
        elif self.platline.text() != '' and not self.Appdf.empty :
            self.plfCode = self.platline.text()
            driver = GetDriver(url)
            Appdf = self.Appdf
            plfCode = self.plfCode
            USER_ID, USER_PW = self.accountline.text(), self.pwline.text()
            AutoLogin(driver, USER_ID, USER_PW)
            time.sleep(1)

            try :
                Verifylst = Ordering(cpurl, driver, Appdf, plfCode)
            except UnexpectedAlertPresentException :
                print(f'{time.ctime()} Login Failed.')
                QMessageBox.warning(self, 'Error', 'Login Error has happened, \nPlease check your SDP Account.')
                return
            except :
                print(f'{time.ctime()} Any cause has happened\n Please try again')
                QMessageBox.warning(self, 'Error', 'Any cause happen\n Please try again.')
                return
            else :
                if Verifylst == -1 :
                    QMessageBox.warning(self, 'Error', 'Platform Code is not founded, \nPlease check platform code..')
                    return

            QMessageBox.information(self, 'Complete', 'CP ordering of automation has been finished. \nif you want to verify them, press "Verify" button.')
            self.viewDataFrame = pd.DataFrame(Verifylst, columns=['Country Name', 'Order Type', 'TV_App Name', 'TV_App Id', 'SMNT_App Name', 'SMNT_App Id'])
            
            # Verifydf = pd.DataFrame(Verifylst, columns=['Country Name', 'Order Type', 'TV_App Name', 'TV_App Id', 'SMNT_App Name', 'SMNT_App Id'])
            # Viewdf = self.VerifyDataframe(Verifydf)
            # model = pandasModel(Viewdf)
            # self.ResultTable.setModel(model)
            
        else :
            QMessageBox.warning(self, 'Error', 'Please Check Platform code or Ordering File or SDP Account')
            
    def Verify(self):
        if self.viewDataFrame.empty :
            QMessageBox.information(self, 'Warning', 'DataFrame is not presented.')
        else :
            self.viewDataFrame = self.VerifyDataframe(self.viewDataFrame) # re-define 
            model = pandasModel(self.viewDataFrame)
            self.ResultTable.setModel(model)
    
    def Close(self) :
        exit()
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Form()
    w.show()
    sys.exit(app.exec_())
