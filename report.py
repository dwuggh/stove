#!/usr/bin/env python3

from typing import Protocol
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import time
import random


class Reporter(object):
    def __init__(self, stuid, password):
        self.stuid = stuid
        self.password = password

    def report(self, data_daily, data_report):
        loginsuccess = False
        retrycount = 1
        while (not loginsuccess) and retrycount:
            session = self.login()
            getform = session.get("https://weixine.ustc.edu.cn/2020/home")
            # print(getform.url)
            retrycount = retrycount - 1
            if getform.url != "https://weixine.ustc.edu.cn/2020/home":
                print("Login Failed! Retry...")
            else:
                print("Login Successful!")
                loginsuccess = True
        if not loginsuccess:
            return False

        data = getform.text.encode('ascii', 'ignore').decode('utf-8', 'ignore')
        soup = BeautifulSoup(data, 'html.parser')
        token = soup.find("input", {"name": "_token"})['value']

        data_daily['_token'] = token
        # print(data_daily)
        headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
            'origin': 'https://weixine.ustc.edu.cn',
            'referer': 'https://weixine.ustc.edu.cn/2020/home',
            }
        resp = session.post('https://weixine.ustc.edu.cn/2020/daliy_report',
                            data=data_daily, headers=headers)
        if resp.status_code != 200:
            print("auto report failed on reporting: response with status code %d" % resp.status_code)
            return False

        
        getform = session.get('https://weixine.ustc.edu.cn/2020/apply/daliy/i?t=3')
        data = getform.text.encode('ascii', 'ignore').decode('utf-8', 'ignore')
        soup = BeautifulSoup(data, 'html.parser')
        token = soup.find("input", {"name": "_token"})['value']

        now = datetime.now(pytz.timezone('Asia/Shanghai'))
        start = now.strftime('%Y-%m-%d %H:%M:%S')
        end = now.strftime('%Y-%m-%d ') + '23:59:59'
        data_report['_token'] = token
        data_report['start_date'] = start
        data_report['end_date'] = end
        # print(data_report)
        resp = session.post(
            'https://weixine.ustc.edu.cn/2020/apply/daliy/post',
            data=data_report,
            headers=headers
            )
        if resp.status_code != 200:
            print("auto report failed on requesting auth: response with status code %d" % resp.status_code)
            return False
        else:
            print("report success!")
            return True
        

    def login(self):
        url = "https://passport.ustc.edu.cn/login?service=http%3A%2F%2Fweixine.ustc.edu.cn%2F2020%2Fcaslogin"
        headers = {
            'origin': 'https://passport.ustc.edu.cn',
            'referer': url,
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
        }
        session = requests.Session()

        print("login...")
        # setting cookies
        resp1 = session.get('https://weixine.ustc.edu.cn/2020/login')
        resp1 = session.get('https://weixine.ustc.edu.cn/2020/caslogin')
        resp1 = session.get(url)

        data = resp1.text.encode('ascii', 'ignore').decode('utf-8', 'ignore')
        soup = BeautifulSoup(data, 'html.parser')
        CAS_LT = soup.find("input", id="CAS_LT")['value']

        data = {
            'model': 'uplogin.jsp',
            'CAS_LT': CAS_LT,
            'service': 'http://weixine.ustc.edu.cn/2020/caslogin',
            'username': self.stuid,
            'password': str(self.password),
            'warn': '',
            'showCode': '',
            'button': '',
        }

        resp = session.post('https://passport.ustc.edu.cn/login', data=data, headers=headers)
        return session


def main():
    import data
    # with open('/root/autoreport/accounts.txt') as f:
    #     lines = list(f.readlines())
    #     for i, line in enumerate(lines):
    #         id, password = line.strip().split(' ')
    #         reporter = Reporter(id, password)

    #         count = 1
    #         while count != 0:
    #             ret = reporter.report()
    #             if ret != False:
    #                 break
    #             print("Report Failed, retry...")
    #             count = count - 1
    #             if count == 0:
    #                 print("report failed for %s" % id)
                    
    #         if i < len(lines) - 1:
    #             time.sleep(random.uniform(600, 1200))
    reporter = Reporter(data.STUID, data.PASSWORD)
    count = 5
    while count != 0:
        ret = reporter.report(data.data_daily, data.data_report)
        if ret != False:
            break
        print("Report Failed, retry...")
        count = count - 1
        if count == 0:
            print("report failed for %s" % id)
            break
        time.sleep(1)
            

if __name__ == '__main__':
    random_start = False
    if random_start:
        time.sleep(random.uniform(300, 1800))
    main()

