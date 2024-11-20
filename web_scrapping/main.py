# Scrapping data from web
import requests
import selectorlib

URL = 'https://programmer100.pythonanywhere.com/tours/'
CHUNG_KHOAN = 'https://dantri.com.vn/kinh-doanh/chung-khoan.htm'
HEADERS={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
}

def scrape(url):
    response = requests.get(url, headers=HEADERS)
    source = response.text
    return source

def extract(source):
    extractor = selectorlib.Extractor.from_yaml_file('extract.yaml')
    values = extractor.extract(source)
    return values['articles']

if __name__ == '__main__':
    data = scrape(CHUNG_KHOAN)
    print(extract(data))