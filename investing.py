import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
import requests
import tkinter as tk
from tkinter import ttk
import config
from datetime import datetime


class Investing:
    def __init__(self):
        self.driver = None
        self.email = config.email
        self.password = config.password
        self.headers = ['Name', 'Last', 'Chg %', 'Time']
        self.data = None
        self.root = None
        self.table = None

    def login(self, driver):
        self.driver = driver
        print('opening login page')
        self.driver.get('https://www.investing.com/')
        print('waiting for page to load')
        self.driver.implicitly_wait(10)
        self.driver.execute_script('overlay.overlayLogin()')
        print('entering login details...')

        WebDriverWait(self.driver, 15).until(ec.visibility_of_element_located((
            By.ID, 'loginFormUser_email'))).send_keys(self.email)
        WebDriverWait(self.driver, 15).until(ec.visibility_of_element_located((
            By.ID, 'loginForm_password'))).send_keys(self.password)
        self.driver.execute_script('loginFunctions.submitLogin()')
        print('getting cookies...')
        self.driver.implicitly_wait(5)
        self.driver.get('https://www.investing.com/portfolio/')

    def update_data(self):
        try:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            table_rows = soup.find('table', {'class': 'js-table-sortable'}).find('tbody').find_all('tr')
            self.data = []
            for tr in table_rows:
                name = tr.find('td', {'data-column-name': 'name'}).text.strip()
                last = tr.find('td', {'data-column-name': 'last'}).text.strip()
                chg = tr.find('td', {'data-column-name': 'chgpercent'}).text.strip()
                time = tr.find('td', {'data-column-name': 'time'}).text.strip()
                self.data.append((name, last, chg, time))
        except:
            pass

    def render_window(self):
        self.root = tk.Tk()
        self.root.resizable(False, False)
        self.root.title('investing.com portfolio')
        self.table = ttk.Treeview(self.root, height=len(self.data))
        self.table.pack(side=tk.TOP, fill=tk.X)
        self.table['columns'] = self.headers
        self.table.column('#0', width=0, stretch=tk.NO)

        # format columns and add headings
        for header in self.headers:
            self.table.column(header, anchor=tk.W, width=100, minwidth=100)
            self.table.heading(header, text=header, anchor=tk.W)

        # format tags
        self.table.tag_configure('red', background='#ffcbcb')
        self.table.tag_configure('green', background='#99f3bd')

        # add data
        for i, row in enumerate(self.data):
            self.table.insert(parent='', index='end', iid=i, values=row, tags=self.get_tags(row[2]))

    @staticmethod
    def get_tags(chg):
        chg = float(chg[:-1])
        if chg > 0:
            tags = ('green',)
        elif chg < 0:
            tags = ('red',)
        else:
            tags = (None,)
        return tags

    def update_window(self):
        print(f'[{datetime.now()}] updating data and window...')
        try:
            # update data from site
            self.update_data()

            # destroy previous table
            self.table.delete(*self.table.get_children())

            # add data
            for i, row in enumerate(self.data):
                self.table.insert(parent='', index='end', iid=i, values=row, tags=self.get_tags(row[2]))

            self.root.after(1000, self.update_window)
        except:
            quit()


if __name__ == '__main__':
    print('choose a mode:')
    print('1. reminder mode')
    print('2. preview mode')
    mode = input('mode: ')
    if mode == '1':
        interval = int(input('enter an update interval in minutes: '))

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    with webdriver.Chrome(options=options) as chrome_driver:
        investing = Investing(chrome_driver)
        investing.login()

        if mode == '1':
            while True:
                investing.update_data()
                investing.render_window()
                investing.root.mainloop()
                time.sleep(interval * 60)
        elif mode == '2':
            investing.update_data()
            investing.render_window()
            investing.update_window()
            investing.root.mainloop()
        else:
            print('choose a valid mode...')
