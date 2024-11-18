import streamlit as st
from nltk.sentiment import SentimentIntensityAnalyzer
import glob
from datetime import datetime
import plotly.express as px

analyzer = SentimentIntensityAnalyzer()

files = glob.glob('diary/*.txt')
pos_dict = {}
neg_dict = {}
for file in files:
   with open(file, 'r', encoding='utf-8') as content:
       content = content.read()
       scores = analyzer.polarity_scores(content)
       day = file.replace('diary\\', '').split('.')[0]
       date_object = datetime.strptime(day, '%Y-%m-%d').strftime('%d %b %Y')
       pos_dict[str(date_object)] = scores['pos']
       neg_dict[str(date_object)] = scores['neg']

st.subheader('Positive')
figure = px.line(x=pos_dict.keys(), y=pos_dict.values(), labels={'x': 'Dates', 'y': 'Positive'})
st.plotly_chart(figure)
st.subheader('Negative')
figure2 = px.line(x=neg_dict.keys(), y=neg_dict.values(), labels={'x': 'Dates', 'y': 'Negative'})
st.plotly_chart(figure2)
