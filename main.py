import requests

url = 'https://newsdata.io/api/1/latest?country=vi&category=politics&apikey=pub_58695ffe53513b97d78ce05437d91b5109031'
requests = requests.get(url)
content = requests.text
print(content)