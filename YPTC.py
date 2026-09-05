import os
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'super-secret-key'

# የዋና ፎልደሮች እና የJSON ፋይል መንገድ
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'noticeboard_data.json')

UPLOAD_FOLDER_IMAGES = os.path.join(BASE_DIR, 'images')
UPLOAD_FOLDER_VIDEOS = os.path.join(BASE_DIR, 'videos')

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'webm', 'ogg'}

app.config['UPLOAD_FOLDER_IMAGES'] = UPLOAD_FOLDER_IMAGES
app.config['UPLOAD_FOLDER_VIDEOS'] = UPLOAD_FOLDER_VIDEOS
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # እስከ 50MB ይቀበላል

# ፎልደሮቹ ከሌሉ በራስ-ሰር እንዲፈጠሩ ማድረግ
os.makedirs(UPLOAD_FOLDER_IMAGES, exist_ok=True)
os.makedirs(UPLOAD_FOLDER_VIDEOS, exist_ok=True)

@app.route('/')
@app.route('/dashboard')
def dashboard():
    """የመነሻ ወይም ዳሽቦርድ ገጽ"""
    notices = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                notices = data.get('notices', [])
            except json.JSONDecodeError:
                notices = []
    return f"<h1>Dashboard</h1><p>Total Notices: {len(notices)}</p><a href='/add'>Add New Notice</a>"

@app.route('/add', methods=['GET', 'POST'])
@app.route('/upload', methods=['GET', 'POST'])
def add_notice():
    if request.method == 'POST':
        # 1. ከ add.html ፎርም የሚመጡ መረጃዎችን መቀበል
        title_en = request.form.get('title_en', '')
        content_en = request.form.get('content_en', '')
        title_am = request.form.get('title_am', '')
        content_am = request.form.get('content_am', '')
        media_type = request.form.get('media_type', 'none')
        
        image_name = ""
        video_name = ""

        # 2. የተላከ ፋይል ካለ ማስተናገድ
        if media_type != 'none' and 'media_file' in request.files:
            file = request.files['media_file']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
                
                if media_type == 'image' and ext in ALLOWED_IMAGE_EXTENSIONS:
                    save_path = os.path.join(app.config['UPLOAD_FOLDER_IMAGES'], filename)
                    file.save(save_path)
                    image_name = filename
                elif media_type == 'video' and ext in ALLOWED_VIDEO_EXTENSIONS:
                    save_path = os.path.join(app.config['UPLOAD_FOLDER_VIDEOS'], filename)
                    file.save(save_path)
                    video_name = filename
                else:
                    flash('የተሳሳተ የፋይል አይነት ነው የተመረጠው!')
                    return redirect(request.url)

        # 3. አዲሱን ማስታወቂያ ማዘጋጀት
        new_notice = {
            'title_en': title_en,
            'content_en': content_en,
            'title_am': title_am,
            'content_am': content_am,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'type': media_type,
            'image': image_name,
            'video': video_name,
            'thumbnail': ''
        }

        # 4. JSON ፋይሉን ማንበብ እና ማዘመን
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = {'notices': []}
        else:
            data = {'notices': []}

        if 'notices' not in data:
            data['notices'] = []

        data['notices'].append(new_notice)

        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        flash('ማስታወቂያው በትክክል ተመዝግቧል!')
        return redirect(url_for('add_notice'))

    return render_template('add.html')

if __name__ == '__main__':
    print("Server starting at http://127.0.0.1:5000/add ...")
    app.run(host='0.0.0.0', port=5000, debug=True)