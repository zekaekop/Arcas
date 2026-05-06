from PyQt6 import QtWidgets, uic
from groq import Groq

import sys
import os

import yaml
import requests
import json

import PyPDF2
from datetime import datetime, timedelta, timezone

# PDF lib for custom templates
# https://github.com/pymupdf/pymupdf
# import pymupdf

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("Auto Report Creator And Scrapper (ARCAS).ui", self)
        self.show()
    
        self.clear_btn.clicked.connect(self.clear_textboxes)
        self.save_btn.clicked.connect(self.save_conf)
        self.reload_btn.clicked.connect(self.load_conf)

        self.scrape.clicked.connect(self.scrape_btn_clicked)
        self.ai_gen_btn.clicked.connect(self.ai_generate_btn_clicked)

        # Week buttons
        self.week_btn_sun.clicked.connect(lambda: self.toggle_week_btn(self.week_btn_sun))
        self.week_btn_mon.clicked.connect(lambda: self.toggle_week_btn(self.week_btn_mon))
        self.week_btn_tue.clicked.connect(lambda: self.toggle_week_btn(self.week_btn_tue))
        self.week_btn_wed.clicked.connect(lambda: self.toggle_week_btn(self.week_btn_wed))
        self.week_btn_thu.clicked.connect(lambda: self.toggle_week_btn(self.week_btn_thu))
        self.week_btn_fri.clicked.connect(lambda: self.toggle_week_btn(self.week_btn_fri))
        self.week_btn_sat.clicked.connect(lambda: self.toggle_week_btn(self.week_btn_sat))

        # Week buttons and toggles
        self.week_buttons = {
            'Sun': 0,
            'Mon': 0,
            'Tue': 0,
            'Wed': 0,
            'Thu': 0,
            'Fri': 0,
            'Sat': 0
        }

        self.load_conf()

        # its better to authenticate since you wont be rate limited after 60 requests
        config = yaml.safe_load(open("config.yml", "r"))

        self.username = "Eko_cli"

        self.token = config["user"]["token"]
        self.api_key = config["user"]["ai_token"]
    
    def ai_report(self, user_template_pdf_path):
        # Use your own Deepseek or any other AI model api key below
        template_prompt = "Your job is to read and understand the commit history of an user and create a similiar report the user has given. Also Create the report with its associate language"

        # This is really usefull to convert pdf files into text soo the AI can see this
        with open(user_template_pdf_path, 'rb') as f: 
            pdf_reader = PyPDF2.PdfReader(f)
            text_content = ""
            for page in pdf_reader.pages:
                text_content += page.extract_text()
            user_template_pdf = text_content

        with open("commits.md", "r") as f:
            user_commit_log = f.read()
        
        client = Groq(api_key=self.api_key,)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": str(template_prompt) + " user: Commit  History: " + str(user_commit_log) + "And Template PDF:" + str(user_template_pdf),
                }
            ],
            model="llama-3.3-70b-versatile",
        )

        print(str(template_prompt) + " user: Commit  History: " + str(user_commit_log) + "And Template PDF:" + str(user_template_pdf))
        print("\n")
        print(chat_completion)

        with open("AI_report.md", "w") as f:
            f.write(chat_completion.choices[0].message.content)

    def toggle_week_btn(self, button):
        # Toggles the state of the weeks buttons index 0 is btn and 1 is the state
        self.week_buttons[button.text()] ^= 1
        self.change_week_btn_style(button)
        print(self.week_buttons)

    def create_conf(self):
        with open("config.yml", "w") as f:
            # Remember to Update this when making changes to config
            config_contents = """
            path:
                account: ''
                output: ''
                report: ''
                repo: ''
            user:
                token: ''
                ai_token: ''
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
    
    def fetch_commits_from_repo(self):
        # This needs to be limited since fetching all commits from a big repo is a problem
        config = yaml.safe_load(open("config.yml", "r"))
        owner = self.lineEdit_account.text()
        repo = self.lineEdit_repo_name.text()

        url = "https://api.github.com/repos/" + str(owner) + "/" + str(repo) + "/commits"

        res = requests.get(url, auth=(self.username, self.token))
        return json.loads(res.text)
    
    def fetch_commit_contents(self, commit_url):
        url = commit_url
        
        res = requests.get(url, auth=(self.username, self.token))
        return json.loads(res.text)

    def save_fetched_commits(self):
        # Fetches all commits
        commits = self.fetch_commits_from_repo()
        # How many days it should go back to start scraping the commits
        days_before = self.spinBox.value()

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_before)

        with open("commits.md", "w") as f:
            for commit in commits:

                commit_date = datetime.fromisoformat(commit["commit"]["author"]["date"].replace('Z', '+00:00'))

                if commit_date >= cutoff_date:
                    f.write(json.dumps(commit["sha"], indent=4) + ": ")
                    f.write(json.dumps(commit["commit"]["message"], indent=4) + " \n ")

                    commit_detail = self.fetch_commit_contents(commit["url"])

                    for file_change in commit_detail.get("files", []):
                        if not file_change.get("filename").endswith(".ui"):
                            patch = file_change.get("patch")
                            if patch:
                                for line in patch.split("\n"):
                                    if line.startswith("+") and not line.startswith("+++"):
                                        f.write(json.dumps(line, indent=4) + "\n")

                    # this is a nice trick, it adds 80 characters of =, you can just multiply strings
                    # f.write("\n" + "="*80 + "\n\n") nevermind it doesnt look that nice
                    f.write("\n\n")
    
    def scrape_btn_clicked(self):
        self.save_fetched_commits()
    
    def ai_generate_btn_clicked(self):
        # checks if its not empty or null
        if self.lineEdit_report.text() != None or self.lineEdit_report.text() == "":
            self.ai_report(self.lineEdit_report.text())
        else:
            self.warning_banner("You must include a report template path, to be able to generate")

    def warning_banner(self, warning):
        # this is primative but just print it
        print(warning)

app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec()
