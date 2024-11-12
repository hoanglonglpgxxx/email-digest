from flask import Flask, render_template
import pandas as pd
from handle_static_data import handle_data

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')
@app.route('/api/v1/<station>/<date>')
def about(station, date):
    temperature = 25
    handle_data(station)
    return {
        'station': station,
        'date': date,
        'temperature': temperature
    }

@app.route('/api/v1/<word>')
def handle(word):
    return {
        'word': word,
        'definition': 'test'
    }

if __name__ == '__main__':
    app.run(debug=True)