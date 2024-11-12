# -*- coding: utf-8 -*-
import requests
from send_email import send

url = 'https://newsdata.io/api/1/latest?country=vi&category=politics&apikey=pub_58695ffe53513b97d78ce05437d91b5109031'
requests = requests.get(url)

content = requests.json()
msg = ''
for result in content['results']:
    msg += (f"""
    Tiêu đề: {result['title']}
    Link: {result['link']}
    """)
msg = f"""\
Subject: Today hot news

{msg}
"""
send('hoanglonglpgxxx@gmail.com', msg)