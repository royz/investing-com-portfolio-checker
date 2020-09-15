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


class Investing:
    def __init__(self):
        self.driver = None
        self.email = config.email
        self.password = config.password
        self.headers = ['Name', 'Last', 'Chg %', 'Time']
        self.data = None
        self.root = None
        self.table = None

    def login(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(options=options)
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
        print('updating data...')
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

        # add data
        for i, row in enumerate(self.data):
            self.table.insert(parent='', index='end', iid=i, values=row)

    def update_window(self):
        print('updating...')
        try:
            # update data from site
            self.update_data()

            # destroy previous table
            for wd in self.root.winfo_children():
                wd.destroy()

            # add the updated table
            self.table = ttk.Treeview(self.root, height=len(self.data))
            self.table.pack(side=tk.TOP, fill=tk.X)
            self.table['columns'] = self.headers
            self.table.column('#0', width=0, stretch=tk.NO)

            # format columns and add headings
            for header in self.headers:
                self.table.column(header, anchor=tk.W, width=100, minwidth=100)
                self.table.heading(header, text=header, anchor=tk.W)

            # add data
            for i, row in enumerate(self.data):
                self.table.insert(parent='', index='end', iid=i, values=row)

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

    investing = Investing()
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
