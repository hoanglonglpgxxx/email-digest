from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')
@app.route('/api/v1/<station>/<date>')
def about(station, date):
    temperature = 25
    return {
        'station': station,
        'date': date,
        'temperature': temperature
    }

if __name__ == '__main__':
    app.run(debug=True)