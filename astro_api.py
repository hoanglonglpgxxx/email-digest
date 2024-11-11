import requests
import streamlit as st
key = 'YffXdnwSpAFpcOzhS7KD8vvHHdU3dYL1kjXMa1fc'

url = f'https://api.nasa.gov/planetary/apod?api_key={key}'
response = requests.get(url)
data = response.json()
st.title(data['title'])

# Extract the image URL
image_url = data['url']

# Download the image
img_response = requests.get(image_url)
img_filepath = 'nasa_apod_image.jpg'

# Save the image to a file
with open(img_filepath, 'wb') as file:
    file.write(img_response.content)

st.image(img_filepath)

st.write(data['explanation'])