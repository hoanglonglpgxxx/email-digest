from flask import Flask, render_template
from handle_static_data import get_temperature, get_word_definition, get_stations, get_annual_temp

app = Flask(__name__)

@app.route('/')
def home():
    stations = get_stations()[['STAID', 'STANAME                                 ']]
    return render_template('index.html', data=stations.to_html())

@app.route('/api/v1/<station>/<date>')
def about(station, date):
    temperature = get_temperature(station, date)
    return {
        'station': station,
        'date': date,
        'temperature': temperature
    }

@app.route('/api/v1/<station>')
def all_data(station):
    temperature = get_temperature(station)

    return temperature

@app.route('/api/v1/annual/<station>/<year>')
def yearly(station, year):
    temperature = get_annual_temp(station, year)

    return temperature


@app.route('/api/v1/<word>')
def handle(word):
    definition = get_word_definition(word)
    return {
        'word': word,
        'definition': definition
    }

if __name__ == '__main__':
    app.run(debug=True)