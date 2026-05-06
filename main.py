from PyQt6 import QtWidgets, uic

import sys
import yaml
import requests
import json

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("Auto Report Creator And Scrapper (ARCAS).ui", self)
        self.show()
    
        self.clear_btn.clicked.connect(self.clear_textboxes)
        self.save_btn.clicked.connect(self.save_conf)
        self.reload_btn.clicked.connect(self.load_conf)
        self.scrape.clicked.connect(self.save_fetched_commits)

        # Week buttons attached to the style func
        self.week_btn_sun.clicked.connect(lambda: self.change_week_btn_style(self.week_btn_sun))
        self.week_btn_mon.clicked.connect(lambda: self.change_week_btn_style(self.week_btn_mon))
        self.week_btn_tue.clicked.connect(lambda: self.change_week_btn_style(self.week_btn_tue))
        self.week_btn_wed.clicked.connect(lambda: self.change_week_btn_style(self.week_btn_wed))
        self.week_btn_thu.clicked.connect(lambda: self.change_week_btn_style(self.week_btn_thu))
        self.week_btn_fri.clicked.connect(lambda: self.change_week_btn_style(self.week_btn_fri))
        self.week_btn_sat.clicked.connect(lambda: self.change_week_btn_style(self.week_btn_sat))

    def create_conf(self):
        with open("config.yml", "w") as f:
            # Remember to Update this when making changes to config
            config_contents = """
            path:
                account: ''
                output: ''
                report: ''
                repo: ''
            """

            f.write(config_contents)

    def change_week_btn_style(self, button):

        style = button.styleSheet()

        if style == "QPushButton{ background-color: #292c30;}" or not style:
            button.setStyleSheet("QPushButton{ background-color: #3daee9;}")
        else:
            button.setStyleSheet("QPushButton{ background-color: #292c30;}")

    def clear_textboxes(self):
        self.lineEdit_report.setText("")
        self.lineEdit_account.setText("")
        self.lineEdit_output.setText("")
        self.lineEdit_repo_name.setText("")

    def save_conf(self):

        report = self.lineEdit_report.text()
        account = self.lineEdit_account.text()
        output = self.lineEdit_output.text()
        repo = self.lineEdit_repo_name.text()

        data = {'path':{'report':report, 'account':account, 'output':output, 'repo':repo}}
        
        yaml.dump(data, open("config.yml", "w"))

    def load_conf(self):
        config = yaml.safe_load(open("config.yml", "r"))
        self.lineEdit_report.setText(config['path']['report'])
        self.lineEdit_account.setText(config['path']['account'])
        self.lineEdit_output.setText(config['path']['output'])
        self.lineEdit_repo_name.setText(config['path']['repo'])
    
    def reset_conf(self):
        pass
    
    def connect_github_api(self):
        pass

    def fetch_commits_from_repo(self):
        # This needs to be limited since fetching all commits from a big repo is a problem
        config = yaml.safe_load(open("config.yml", "r"))
        owner = config['path']['account']
        repo = self.lineEdit_repo_name.text()

        url = "https://api.github.com/repos/" + str(owner) + "/" + str(repo) + "/commits"

        res = requests.get(url)
        return json.loads(res.text)
    
    def save_fetched_commits(self):
        # Fetches all commits
        commits = self.fetch_commits_from_repo()
        # How many days it should go back to start scraping the commits
        days_before = self.spinBox.value()

        with open("commits.md", "w") as f:
            for i in range(days_before):
                f.write(json.dumps(commits[i]["sha"], indent=4) + ": ")
                f.write(json.dumps(commits[i]["commit"]["message"], indent=4) + "\n")
    
    def warning_banner(self):
        pass

app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec()
