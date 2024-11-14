import requests

def get_weather(city, key, days = 1):
    base_url = "https://api.weatherapi.com/v1/forecast.json"
    params = {
        'q': city,
        'key': key,
        'aqi': 'no',
        'days': days,
    }
    response = requests.get(base_url, params=params)
    print(response)
    if response and response.status_code == 200:
        forecasts = response.json()['forecast']['forecastday']
        dates = [temp['date'] for temp in forecasts]
        min_temp = [temp['day']['mintemp_c'] for temp in forecasts]
        max_temp = [temp['day']['maxtemp_c'] for temp in forecasts]
        return dates, {
            'max_temp': max_temp,
            'min_temp': min_temp
        }
    else:
        return None
