import streamlit as st
import plotly.express as px
from data_handling import handle_data

options = {
    'GDP': 'gdp',
    'Social Support': 'social_support',
    'Life Expectancy': 'life_expectancy',
}

st.title('In search for happiness')
x_axis_label = st.selectbox('Select data of X-axis', options.keys())
y_axis_label = st.selectbox('Select data of Y-axis', options.keys())

x_axis = options[x_axis_label]
y_axis = options[y_axis_label]

if x_axis and y_axis:
    st.subheader(f'{x_axis.capitalize()} and {y_axis.capitalize()}')

    x_axis_dict = handle_data(x_axis)
    y_axis_dict = handle_data(y_axis)

    figure = px.scatter(x=x_axis_dict,
                     y=y_axis_dict,
                     labels={
                         'x': x_axis_label,
                         'y': y_axis_label
                     })

    st.plotly_chart(figure)
