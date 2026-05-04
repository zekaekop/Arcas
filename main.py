from PyQt6 import QtWidgets, uic

import sys
import yaml

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("Auto Report Creator And Scrapper (ARCAS).ui", self)
        self.show()
    
        self.clear_btn.clicked.connect(self.clear_textboxes)
        self.save_btn.clicked.connect(self.save_conf)
        self.reload_btn.clicked.connect(self.load_conf)

    def clear_textboxes(self):
        self.lineEdit_report.setText("")
        self.lineEdit_account.setText("")
        self.lineEdit_output.setText("")

    def save_conf(self):

        report = self.lineEdit_report.text()
        account = self.lineEdit_account.text()
        ouput = self.lineEdit_output.text()

        data = {'path':{'report':report, 'account':account, 'output':ouput}}
        
        yaml.dump(data, open("config.yml", "w"))

    def load_conf(self):
        config = yaml.safe_load(open("config.yml", "r"))
        self.lineEdit_report.setText(config['path']['report'])
        self.lineEdit_account.setText(config['path']['account'])
        self.lineEdit_output.setText(config['path']['output'])
    
    def reset_conf(self):
        pass
    
app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec()
