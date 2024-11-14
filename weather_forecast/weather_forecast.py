import streamlit as st
import plotly.express as px
from get_response import get_weather

api_key = '182e2d3581984aeea40103409241311'


st.title('Weather Forecast for upcoming days')
place = st.text_input('Place: ')
days = st.slider('Forecast days', min_value=1, max_value=3, help='Select number of forecasted days')
options = st.selectbox('Select data to view',
                       ('Temperature', 'Sky'))

if place:
    result = get_weather(place, api_key, days)
    if result:
        dates, temperatures = result
        st.subheader(f'{options.capitalize()} for the next {days} days in {place}')

        st.text_area(label='Text area test', value=temperatures)

        if days > 1:
            figure = px.line(x=dates, y=temperatures['max_temp'], labels={'x': 'Dates', 'y': 'Temp (C)'})

            st.plotly_chart(figure)
    else:
        st.subheader(f'No available data for city {place}')