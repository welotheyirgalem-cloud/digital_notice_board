import json
from pathlib import Path
from flask import Flask, jsonify, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'yirgalem_polytechnic_secret_key'  # Enables session security
DATA_FILE = Path(__file__).parent / 'noticeboard_data.json'


def load_data():
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding='utf-8'))
        except Exception:
            pass
    return {'college_en': 'YIRGALEM POLYTECHNIC COLLEGE', 'notices': []}


def save_data(data):
    DATA_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding='utf-8')


@app.route('/')
def home():
    data = load_data()
    return render_template('index.html', data=data)


@app.route('/api/data')
def get_data():
    return jsonify(load_data())


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Admin credentials check
        if username == 'admin' and password == 'admin123':
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid username or password!'
            
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    data = load_data()
    return render_template('dashboard.html', data=data)


@app.route('/add_notice', methods=['POST'])
def add_notice():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    title = request.form.get('title')
    content = request.form.get('content')
    category = request.form.get('category', 'General')
    
    if title and content:
        data = load_data()
        new_notice = {
            'id': len(data['notices']) + 1,
            'title': title,
            'content': content,
            'category': category
        }
        data['notices'].append(new_notice)
        save_data(data)
        
    return redirect(url_for('dashboard'))


@app.route('/delete_notice/<int:notice_id>', methods=['POST'])
def delete_notice(notice_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    data = load_data()
    data['notices'] = [n for n in data['notices'] if n.get('id') != notice_id]
    save_data(data)
    
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
