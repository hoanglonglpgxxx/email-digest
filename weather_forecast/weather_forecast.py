import streamlit as st
import requests

def get_weather(city, api_key):
    base_url = "http://api.weatherapi.com/v1/current.json"
    params = {
        'q': city,
        'key': api_key,
        'aqi': 'no'
    }
    response = requests.get(base_url, params=params)
    return response.json()

api_key = '182e2d3581984aeea40103409241311'
city = 'London'

st.title('Weather Forecast for upcoming days')
place = st.text_input('Place: ')
days = st.slider('Forecast days', min_value=1, max_value=5, help='Select number of forecasted days')
options = st.selectbox('Select data to view',
                       ('Temperature', 'Sky'))

weather_data = get_weather(place, api_key)

st.subheader(f'{options.capitalize()} for the next {days} days in {place}')

st.text_area(label='', value=weather_data)