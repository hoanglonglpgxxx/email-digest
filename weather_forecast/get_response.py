import requests

def get_weather(city, key, is_temp, days = 1):
   """
    Get weather condition from API

   :param city: city name
   :type city: str
   :param key: api key
   :type key: str
   :param is_temp: is temperature or air condition
   :type is_temp: bool
   :param days: days of forecast
   :type days: int
   :return: dates and optional value
   :rtype: dates: list, optional_val: dict or list of dicts
   """
   base_url = "https://api.weatherapi.com/v1/forecast.json"
   params = {
       'q': city,
       'key': key,
       'aqi': 'yes',
       'days': days,
   }
   response = requests.get(base_url, params=params)
   if response and response.status_code == 200:
       forecasts = response.json()['forecast']['forecastday']
       dates = [temp['date'] for temp in forecasts]
       min_temp = [temp['day']['mintemp_c'] for temp in forecasts]
       max_temp = [temp['day']['maxtemp_c'] for temp in forecasts]
       air_quality = [temp['day']['air_quality'] for temp in forecasts]
       option_val = {
           'max_temp': max_temp,
           'min_temp': min_temp
       } if is_temp else air_quality

       return dates, option_val
   else:
       return None

# get_weather('Hanoi', '182e2d3581984aeea40103409241311',0, 3)