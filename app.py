import json
from pathlib import Path
from flask import Flask, jsonify, render_template

app = Flask(__name__)
DATA_FILE = Path(__file__).parent / 'noticeboard_data.json'


def load_data():
  if DATA_FILE.exists():
    try:
      return json.loads(DATA_FILE.read_text(encoding='utf-8'))
    except Exception:
      pass
  return {'college_en': 'YIRGALEM POLYTECHNIC COLLEGE', 'notices': []}


@app.route('/')
def home():
  data = load_data()
  return render_template('index.html', data=data)


@app.route('/api/data')
def get_data():
  return jsonify(load_data())


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)