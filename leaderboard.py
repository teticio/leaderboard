import os
import pytz
import argparse
import pandas as pd
from time import sleep
import subprocess as sp
from zipfile import ZipFile
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('competition', type=str, help='Kaggle competition name')
    parser.add_argument('-low', action='store_true', help='Lower score is better')
    parser.add_argument('--user', type=str, help='Flourish user name')
    parser.add_argument('--password', type=str, help='Flourish password')
    parser.add_argument('--project', type=str, help='Flourish project number (https://app.flourish.studio/@flourish/bar-chart-race)')
    parser.add_argument('--every', type=int, help='Repeat every x minutes')
    args = parser.parse_args()
    competition = args.competition
    low = args.low
    user = args.user
    password = args.password
    project = args.project
    every_x_mins = 5 if args.every is None else args.every
    
    try:
        leaderboard = pd.read_csv(f'{competition}-leaderboard.csv', index_col='TeamName')
        first_time = False
    except:
        first_time = True

    while True:
        now = datetime.now(pytz.timezone('Europe/London'))
        command = ['kaggle', 'competitions', 'leaderboard', competition, '--download']
        p = sp.Popen(command, stderr=sp.PIPE)
        if p.returncode != 0:
            output = p.communicate()[1].decode()
        with ZipFile(f'{competition}.zip') as zf:
            zf.extractall()
        df = pd.read_csv(f'{competition}-publicleaderboard.csv')
        df = df.drop(columns=['TeamId', 'SubmissionDate']).groupby('TeamName').agg('min' if low else 'max').sort_values(['Score'], ascending=low)
        if first_time:
            leaderboard = pd.DataFrame(index = df.index)
            first_time = False
        for index, row in df.iterrows():
            if row.name not in leaderboard.index:
                leaderboard = leaderboard.append(pd.Series([], index=None, name=row.name)).fillna(0)
            leaderboard.loc[leaderboard.index == row.name, now.strftime('%a %H:%M')] = row.Score
        leaderboard.to_csv(f'{competition}-leaderboard.csv')

        if user is not None and password is not None and project is not None:
            timeout = 5
            try:
                driver = webdriver.Chrome()
                driver.get('https://flourish.studio/')
                WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, "//*[@class='menu-item'][text()='Sign in']"))).click()
                WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, "//input[@name='email']"))).send_keys(user)
                WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, "//input[@name='password']"))).send_keys(password)
                WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, "//input[@class='btn'][@type='submit']"))).click()
                driver.get(f'https://app.flourish.studio/visualisation/{project}/edit')
                WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, "//button[@value='data']"))).click()
                WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, "//*[contains(@class, 'btn')][@data-action='add-data']"))).click()
                WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))).send_keys(os.getcwd() + f'/{competition}-leaderboard.csv')
                WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, "//*[contains(@class, 'btn')][text()='Import publicly']"))).click()
                WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, "//*[contains(@class, 'btn')][text()='Next, select the columns 👉']"))).click()
                WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'export')]"))).click()
                WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'republish-btn')]"))).click()
                WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, "//h3[@class='publish-status'][text()='Published']")))
            except Exception as e:
                print(e)
                pass
            driver.quit()

        while (datetime.now(pytz.timezone('Europe/London')) - now) < timedelta(minutes=every_x_mins):
            sleep(1)