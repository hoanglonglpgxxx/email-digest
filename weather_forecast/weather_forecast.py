import streamlit as st
import plotly.express as px
from get_response import get_weather

api_key = '182e2d3581984aeea40103409241311'

st.title('Weather Forecast for upcoming days')
place = st.text_input('Place: ')
# Max 3 cause free API version only allow max 3 days
days = st.slider('Forecast days', min_value=1, max_value=3, help='Select number of forecasted days')
options = st.selectbox('Select data to view',
                       ('Temperature', 'Sky'))

if place:
    result = get_weather(place, api_key, 1 if options == 'Temperature' else 0, days)
    if result:
        dates, optional_val = result
        st.subheader(f'{options.capitalize()} for the next {days} days in {place}')

        st.text_area(label='Text area test', value=optional_val if options == 'Temperature' else 'Analyzing data....')

        if days > 1:
            if options == 'Temperature':
                figure = px.line(x=dates, y=optional_val['max_temp'], labels={'x': 'Dates', 'y': 'Temp (C)'})
                st.plotly_chart(figure)
            else:
                # Combine data into a single DataFrame
                import pandas as pd
                optional_val_df = []
                for index, i in enumerate(optional_val):
                    # For key,value in i.items(), make new dict that has key = key....title() and value
                    transformed_dict = {key.replace('_', ' ' if key != 'pm2_5' else '.').replace('-', ' ').title(): value for key, value in i.items()}


                    df = pd.DataFrame(list(transformed_dict.items()), columns=['Pollutant', 'Value'])
                    df['Ngày'] = dates[index]
                    optional_val_df.append(df)

                df_combined = pd.concat(optional_val_df)

                # Create a grouped bar chart
                fig = px.bar(df_combined, x='Pollutant', y='Value', color='Ngày', barmode='group',
                             title='Air Quality Data Comparison')
                st.plotly_chart(fig)

    else:
        st.subheader(f'No available data for city {place}')