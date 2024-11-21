# Scrapping data from web
from time import strftime
import requests
import selectorlib
from send_email import send

URL = 'https://programmer100.pythonanywhere.com/tours/'
CHUNG_KHOAN = 'https://dantri.com.vn/kinh-doanh/chung-khoan.htm'
BASE_DOMAIN = 'https://dantri.com.vn'
HEADERS={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
}

def scrape(url):
    response = requests.get(url, headers=HEADERS)
    source = response.text
    extractor = selectorlib.Extractor.from_yaml_file('extract.yaml')
    datas = extractor.extract(source)
    return datas['articles']

def extract(datas):
    content = ''
    for data in datas:
        data['href'] = BASE_DOMAIN + data['href']
        content+= f"""
            Tiêu đề: {data['title']}
            Nội dung: {data['content']}
            Link: {data['href']}
            """
    return content

if __name__ == '__main__':
    data = scrape(CHUNG_KHOAN)
    content = f"""\
Subject: Today hot news - {strftime('%d %b %Y')}

{extract(data)}
"""
    send('hoanglonglpgxxx@gmail.com', content)