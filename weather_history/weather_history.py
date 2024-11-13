from flask import Flask, render_template
import pandas as pd
from handle_static_data import get_temperature, get_word_definition

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')
@app.route('/api/v1/<station>/<date>')
def about(station, date):
    temperature = get_temperature(station, date)
    return {
        'station': station,
        'date': date,
        'temperature': temperature
    }

@app.route('/api/v1/<word>')
def handle(word):
    definition = get_word_definition(word)
    return {
        'word': word,
        'definition': definition
    }

if __name__ == '__main__':
    app.run(debug=True)