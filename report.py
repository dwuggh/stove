#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import time
import random
import sys
import re


class Reporter(object):
    def __init__(self, stuid, password, photo):
        self.stuid = stuid
        self.password = password
        self.ua = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
        self.photo = photo
        

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
        headers = {
            'user-agent': self.ua,
            'origin': 'https://weixine.ustc.edu.cn',
            'referer': 'https://weixine.ustc.edu.cn/2020/home',
            }
        resp = session.post('https://weixine.ustc.edu.cn/2020/daliy_report',
                            data=data_daily, headers=headers)
        if resp.status_code != 200:
            print("auto report failed on reporting: response with status code %d" % resp.status_code)
            return False

        print("上传行程卡...")
        self.upload_img(session, token, self.photo)
        
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
        resp = session.post(
            'https://weixine.ustc.edu.cn/2020/apply/daliy/ipost',
            data=data_report,
            headers=headers
            )
        status = self.check_status(session)
        if resp.status_code != 200:
            print("auto report failed on requesting auth: response with status code %d" % resp.status_code)
            return False
        elif not status == '在校可跨校区':
            print("autoreport might not work as expected: your status is %s" % status)
            return False
        else:
            print("report success!")
            return True
        


    def login(self):
        url = "https://passport.ustc.edu.cn/login?service=http%3A%2F%2Fweixine.ustc.edu.cn%2F2020%2Fcaslogin"
        headers = {
            'origin': 'https://passport.ustc.edu.cn',
            'referer': url,
            'user-agent': self.ua
        }
        session = requests.Session()

        session.headers.update({
            'user-agent': self.ua
        })

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

        session.post('https://passport.ustc.edu.cn/login', data=data, headers=headers)
        return session

    def check_status(self, session):
        resp = session.get('https://weixine.ustc.edu.cn/2020/apply_total', headers={
            'user-agent': self.ua
        })
        soup = BeautifulSoup(resp.text, 'html.parser')
        res = list(soup.find(id="table-box").find_all('p')[2])[1].string
        return res
        

    def upload_img(self, session, token, img):
        # get gid and sign
        resp = session.get("https://weixine.ustc.edu.cn/2020/upload/xcm")
        data = resp.text.encode('ascii', 'ignore').decode('utf-8', 'ignore')
        gid = re.search(r"(?<='gid': ').*?(?=')", data).group()
        sign = re.search(r"(?<='sign': ').*?(?=')", data).group()
        # print(gid)
        # print(sign)


        with open(img, 'rb') as f:
            # content = f.read()
            data = {
                "_token": token,
                "gid": gid,
                "sign": sign,
                "t": 1,
                # form data of webuploader
                "id": "WU_FILE_0",
                "name": "photo.jpg",
                "type": "image/jpeg",
                "lastModifiedDate": datetime.now().strftime("%a %b %d %Y %H:%M:%S") + " GMT+0800 (China Standard Time)",
                # "size": len(content),
                # "file": content
                
                }
            resp = session.post('https://weixine.ustc.edu.cn/2020img/api/upload_for_student', data=data,
                                files={
                                    "file": f
                                }
                                # headers=headers
                                )
            # print(resp.request.header)
            print(resp.json())


def main():
    import data
    reporter = Reporter(data.STUID, data.PASSWORD, data.photo)
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
    argv = sys.argv
    argc = len(argv)
    if argc > 1:
        t = int(argv[1])
        time.sleep(random.uniform(0, t))
    main()

