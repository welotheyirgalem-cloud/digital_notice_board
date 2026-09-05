import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from pathlib import Path
import json
import shutil
import os
from datetime import datetime
import threading

try:
    from PIL import Image, ImageTk, ImageEnhance
except ImportError:
    raise SystemExit('Install Pillow first: python -m pip install pillow')

try:
    from tkvideo import tkvideo
except ImportError:
    tkvideo = None

try:
    from flask import Flask, render_template_string, send_from_directory
except ImportError:
    raise SystemExit('Install Flask first: python -m pip install flask')

# ============================================
# BASE DIRECTORY SETUP
# ============================================
BASE = Path(__file__).resolve().parent
DATA = BASE / 'noticeboard_data.json'
LOGOS = BASE / 'logos'
VIDEOS = BASE / 'videos'
IMAGES = BASE / 'images'

for folder in [LOGOS, VIDEOS, IMAGES]:
    folder.mkdir(exist_ok=True)

DEFAULT = {
    'admin_password': 'admin123',
    'college_en': 'YIRGALEM POLYTECHNIC COLLEGE',
    'college_am': 'የይርጋለም ፖሊ ቴክኒክ ኮሌጅ',
    'college_local': 'IRGALAME POOLITEKINIKE KOLLEEJE',
    'headline_en': 'DIGITAL NOTICE BOARD',
    'headline_am': 'ዲጂታል ማስታወቂያ ሰሌዳ',
    'motto': 'SKILLS AND INNOVATION FOR BETTER GENERATION!',
    'motto_position': 'BOTTOM',
    'font_en': 'Segoe UI',
    'font_am': 'Abyssinica SIL',
    'font_size_header': 17,
    'font_size_body': 11,
    'bg_image': '',
    'bg_darkness': 70,
    'scroll_speed': 80,
    'email': 'yirgalempoly@gmail.com',
    'phone': '+251 462251413',
    'left_logo': '',
    'right_logo': '',
    'notices': [
        {
            'title': 'Student Registration',
            'date': '26/12/2018 E.C',
            'body': 'All students are requested to complete registration before the deadline.',
            'type': 'text',
            'image': '',
            'video': '',
            'active': True
        }
    ]
}

def load_data():
    try:
        if DATA.exists():
            with open(DATA, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
            for k, v in DEFAULT.items():
                loaded.setdefault(k, v)
            return loaded
    except Exception as e:
        print(f"Error loading data: {e}")
    return DEFAULT

def save_data(data):
    try:
        with open(DATA, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
        return False

d = load_data()

# ============================================
# FLASK WEB SERVER SETUP FOR MOBILE ACCESS
# ============================================
web_app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ data.college_en }} - Digital Notice Board</title>
    <style>
        body { background-color: #0f172a; color: #f8fafc; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 15px; }
        .header { background-color: #1e293b; padding: 15px; display: flex; align-items: center; justify-content: space-between; border-radius: 8px; margin-bottom: 15px; border: 1px solid #334155; }
        .header-content { text-align: center; flex-grow: 1; }
        .header h1 { font-size: 1.2rem; margin: 5px 0; color: #f8fafc; }
        .header h2 { font-size: 1rem; margin: 5px 0; color: #38bdf8; }
        .header p.local { font-size: 0.85rem; color: #f59e0b; margin: 3px 0; }
        .header p.motto { font-size: 0.85rem; color: #f59e0b; font-style: italic; margin: 5px 0; }
        .logo-img { height: 75px; width: auto; max-width: 90px; object-fit: contain; }
        .marquee { background-color: #0284c7; padding: 10px; text-align: center; font-weight: bold; border-radius: 6px; margin-bottom: 15px; }
        .card { background-color: #1e293b; border: 1px solid #334155; border-radius: 8px; margin-bottom: 15px; overflow: hidden; }
        .card-header { background-color: #334155; padding: 10px 15px; display: flex; justify-content: space-between; align-items: center; }
        .card-body { padding: 15px; font-size: 0.95rem; color: #e2e8f0; line-height: 1.4; }
        .card-img { max-width: 100%; height: auto; border-radius: 4px; margin-bottom: 10px; display: block; }
    </style>
</head>
<body>
    <div class="header">
        {% if data.left_logo %}
            <img src="/media/{{ data.left_logo_rel }}" class="logo-img" alt="Left Logo">
        {% else %}
            <img src="/static/logo.png" class="logo-img" alt="Logo" onerror="this.style.display='none'">
        {% endif %}

        <div class="header-content">
            {% if data.motto_position == 'TOP' %}<p class="motto">“{{ data.motto }}”</p>{% endif %}
            <h1>{{ data.college_en }}</h1>
            <h2>{{ data.college_am }}</h2>
            <p class="local">{{ data.college_local }}</p>
            {% if data.motto_position != 'TOP' %}<p class="motto">“{{ data.motto }}”</p>{% endif %}
        </div>

        {% if data.right_logo %}
            <img src="/media/{{ data.right_logo_rel }}" class="logo-img" alt="Right Logo">
        {% endif %}
    </div>

    <div class="marquee">
        📢 {{ data.headline_en }} | {{ data.headline_am }}
    </div>

    <div>
        {% for notice in data.notices %}
        {% if notice.get('active', True) %}
        <div class="card">
            <div class="card-header">
                <strong>[{{ notice.type.upper() }}] {{ notice.title }}</strong>
                <small>{{ notice.date }}</small>
            </div>
            <div class="card-body">
                {% if notice.image_rel %}
                <img src="/media/{{ notice.image_rel }}" class="card-img" alt="Notice Image">
                {% endif %}
                <p>{{ notice.body }}</p>
            </div>
        </div>
        {% endif %}
        {% endfor %}
    </div>
</body>
</html>
"""

@web_app.route('/')
def index():
    current_data = load_data()
    # Create relative paths for media serving in web view
    if current_data.get('left_logo'):
        current_data['left_logo_rel'] = Path(current_data['left_logo']).relative_to(BASE).as_posix()
    if current_data.get('right_logo'):
        current_data['right_logo_rel'] = Path(current_data['right_logo']).relative_to(BASE).as_posix()
        
    for n in current_data.get('notices', []):
        if n.get('image'):
            try:
                n['image_rel'] = Path(n['image']).relative_to(BASE).as_posix()
            except Exception:
                n['image_rel'] = ''
                
    return render_template_string(HTML_TEMPLATE, data=current_data)

@web_app.route('/media/<path:filename>')
def serve_media(filename):
    return send_from_directory(BASE, filename)


# ============================================
# MAIN TKINTER APPLICATION
# ============================================
class DigitalNoticeBoard:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()  # Hide main window until admin authenticates
        
        if not self.authenticate_admin():
            self.root.destroy()
            return
            
        self.root.deiconify()  # Show window after successful login
        self.root.title('Yirgalem Polytechnic College - Digital Notice Board v2.0 (Admin Mode)')
        self.root.geometry('1400x900')
        self.root.configure(bg='#1e1e2e')
        
        self.card_images = []
        self.video_players = []
        self.bg_photo = None
        self.auto_scroll_active = True
        self.scroll_direction = 1
        self.scroll_delay = int(d.get('scroll_speed', 80))
        
        self.init_app()
        self.start_auto_scroll()

    def authenticate_admin(self):
        saved_pwd = d.get('admin_password', 'admin123')
        pwd_input = simpledialog.askstring("Admin Authentication", "Enter Admin Password:", show='*')
        
        if pwd_input is None:
            return False
            
        if pwd_input == saved_pwd:
            messagebox.showinfo("Login Success", "Welcome, Administrator!")
            return True
        else:
            messagebox.showerror("Access Denied", "Incorrect Admin Password!")
            return False

    def change_admin_password(self):
        curr_pwd = simpledialog.askstring("Security", "Enter Current Password:", show='*')
        if curr_pwd == d.get('admin_password', 'admin123'):
            new_pwd = simpledialog.askstring("Security", "Enter New Password:", show='*')
            if new_pwd:
                d['admin_password'] = new_pwd
                save_data(d)
                messagebox.showinfo("Success", "Admin password updated successfully!")
        else:
            messagebox.showerror("Error", "Incorrect current password!")

    def init_app(self):
        self.main_container = ttk.PanedWindow(self.root, orient='horizontal')
        self.main_container.pack(fill='both', expand=True)
        
        self.create_editor_panel()
        self.create_preview_panel()
        self.refresh_display()

    def create_editor_panel(self):
        editor_container = ttk.Frame(self.main_container)
        self.main_container.add(editor_container, weight=1)

        canvas = tk.Canvas(editor_container, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(editor_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, padding=10)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # ADMIN CONTROL HEADER
        ttk.Label(scrollable_frame, text='🔒 ADMIN SETTINGS', font=('Segoe UI', 11, 'bold')).pack(anchor='w', pady=(5, 2))
        ttk.Button(scrollable_frame, text='🔑 Change Admin Password', command=self.change_admin_password).pack(fill='x', pady=(0, 8))

        ttk.Separator(scrollable_frame, orient='horizontal').pack(fill='x', pady=5)

        ttk.Label(scrollable_frame, text='⚙️ HEADER SETTINGS', font=('Segoe UI', 11, 'bold')).pack(anchor='w', pady=5)
        
        self.vars = {}
        
        ttk.Label(scrollable_frame, text='English Header:', font=('Segoe UI', 8)).pack(anchor='w')
        self.vars['college_en'] = tk.StringVar(value=d.get('college_en', ''))
        ttk.Entry(scrollable_frame, textvariable=self.vars['college_en']).pack(fill='x', pady=(0, 3))

        ttk.Label(scrollable_frame, text='Amharic Header:', font=('Segoe UI', 8)).pack(anchor='w')
        self.vars['college_am'] = tk.StringVar(value=d.get('college_am', ''))
        ttk.Entry(scrollable_frame, textvariable=self.vars['college_am']).pack(fill='x', pady=(0, 3))

        ttk.Label(scrollable_frame, text='Local/Phonetic Header:', font=('Segoe UI', 8)).pack(anchor='w')
        self.vars['college_local'] = tk.StringVar(value=d.get('college_local', ''))
        ttk.Entry(scrollable_frame, textvariable=self.vars['college_local']).pack(fill='x', pady=(0, 3))

        ttk.Separator(scrollable_frame, orient='horizontal').pack(fill='x', pady=8)

        # FONT SELECTION SECTION
        ttk.Label(scrollable_frame, text='🔤 FONT & STYLING SETTINGS', font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        ttk.Label(scrollable_frame, text='English Font:', font=('Segoe UI', 8)).pack(anchor='w')
        self.font_en_var = tk.StringVar(value=d.get('font_en', 'Segoe UI'))
        en_fonts = ['Segoe UI', 'Arial', 'Times New Roman', 'Trebuchet MS', 'Tahoma', 'Verdana', 'Impact']
        ttk.Combobox(scrollable_frame, textvariable=self.font_en_var, values=en_fonts, state='readonly').pack(fill='x', pady=(0, 3))

        ttk.Label(scrollable_frame, text='Amharic Font:', font=('Segoe UI', 8)).pack(anchor='w')
        self.font_am_var = tk.StringVar(value=d.get('font_am', 'Abyssinica SIL'))
        am_fonts = ['Abyssinica SIL', 'Nyala', 'Ebrima', 'Ethiopic Yebse', 'Segoe UI', 'Arial']
        ttk.Combobox(scrollable_frame, textvariable=self.font_am_var, values=am_fonts, state='readonly').pack(fill='x', pady=(0, 3))

        font_size_frame = ttk.Frame(scrollable_frame)
        font_size_frame.pack(fill='x', pady=3)
        
        ttk.Label(font_size_frame, text='Header Size:', font=('Segoe UI', 8)).pack(side='left')
        self.h_size_var = tk.IntVar(value=d.get('font_size_header', 17))
        ttk.Spinbox(font_size_frame, from_=10, to=32, textvariable=self.h_size_var, width=5).pack(side='left', padx=5)

        ttk.Label(font_size_frame, text='Body Size:', font=('Segoe UI', 8)).pack(side='left', padx=(10, 0))
        self.b_size_var = tk.IntVar(value=d.get('font_size_body', 11))
        ttk.Spinbox(font_size_frame, from_=8, to=24, textvariable=self.b_size_var, width=5).pack(side='left', padx=5)

        ttk.Separator(scrollable_frame, orient='horizontal').pack(fill='x', pady=8)

        bg_btn_frame = ttk.Frame(scrollable_frame)
        bg_btn_frame.pack(fill='x', pady=4)
        ttk.Button(bg_btn_frame, text='🖼️ Upload Background Image', command=self.select_bg_image).pack(fill='x')

        ttk.Label(scrollable_frame, text='🌑 Background Darkness (%)', font=('Segoe UI', 8)).pack(anchor='w', pady=(4, 0))
        self.darkness_var = tk.IntVar(value=d.get('bg_darkness', 70))
        darkness_scale = ttk.Scale(scrollable_frame, from_=0, to=100, variable=self.darkness_var, command=lambda v: self.update_darkness_label())
        darkness_scale.pack(fill='x')
        self.lbl_darkness_val = ttk.Label(scrollable_frame, text=f"{self.darkness_var.get()}%", font=('Segoe UI', 8))
        self.lbl_darkness_val.pack(anchor='e')

        ttk.Label(scrollable_frame, text='Motto:', font=('Segoe UI', 8)).pack(anchor='w')
        self.vars['motto'] = tk.StringVar(value=d.get('motto', ''))
        ttk.Entry(scrollable_frame, textvariable=self.vars['motto']).pack(fill='x', pady=(0, 3))

        ttk.Label(scrollable_frame, text='Motto Position:', font=('Segoe UI', 8)).pack(anchor='w')
        self.motto_pos_var = tk.StringVar(value=d.get('motto_position', 'BOTTOM'))
        motto_cb = ttk.Combobox(scrollable_frame, textvariable=self.motto_pos_var, values=['TOP', 'BOTTOM'], state='readonly')
        motto_cb.pack(fill='x', pady=(0, 5))

        for key, label in [('headline_en', 'Headline (EN)'), ('headline_am', 'Headline (AM)'), ('phone', 'Phone'), ('email', 'Email')]:
            ttk.Label(scrollable_frame, text=label, font=('Segoe UI', 8)).pack(anchor='w')
            self.vars[key] = tk.StringVar(value=d.get(key, ''))
            ttk.Entry(scrollable_frame, textvariable=self.vars[key]).pack(fill='x', pady=(0, 3))

        btn_logo_frame = ttk.Frame(scrollable_frame)
        btn_logo_frame.pack(fill='x', pady=4)
        ttk.Button(btn_logo_frame, text='🖼️ Left Logo', command=lambda: self.select_logo('left_logo')).pack(side='left', expand=True, fill='x', padx=2)
        ttk.Button(btn_logo_frame, text='🖼️ Right Logo', command=lambda: self.select_logo('right_logo')).pack(side='left', expand=True, fill='x', padx=2)

        ttk.Button(scrollable_frame, text='💾 Save Settings', command=self.save_settings).pack(fill='x', pady=5)

        ttk.Separator(scrollable_frame, orient='horizontal').pack(fill='x', pady=8)

        ttk.Label(scrollable_frame, text='⚡ Auto-Scroll Speed (Faster ◄ ► Slower)', font=('Segoe UI', 8, 'bold')).pack(anchor='w')
        self.speed_var = tk.IntVar(value=d.get('scroll_speed', 80))
        speed_scale = ttk.Scale(scrollable_frame, from_=10, to=200, variable=self.speed_var, command=self.on_speed_change)
        speed_scale.pack(fill='x')
        
        self.scroll_btn = ttk.Button(scrollable_frame, text='⏹ STOP AUTO-SCROLL', command=self.toggle_auto_scroll)
        self.scroll_btn.pack(fill='x', pady=5)

        ttk.Separator(scrollable_frame, orient='horizontal').pack(fill='x', pady=8)
        
        ttk.Label(scrollable_frame, text='📌 MANAGE NOTICES', font=('Segoe UI', 11, 'bold')).pack(anchor='w', pady=5)
        
        btn_box = ttk.Frame(scrollable_frame)
        btn_box.pack(fill='x', pady=5)
        ttk.Button(btn_box, text='➕ Add', command=self.add_notice).pack(side='left', expand=True, fill='x', padx=2)
        ttk.Button(btn_box, text='✏️ Edit', command=self.edit_notice).pack(side='left', expand=True, fill='x', padx=2)
        ttk.Button(btn_box, text='🗑️ Delete', command=self.delete_notice).pack(side='left', expand=True, fill='x', padx=2)

        self.tree = ttk.Treeview(scrollable_frame, columns=('Title', 'Type', 'Status'), show='headings', height=5)
        self.tree.heading('Title', text='Title')
        self.tree.heading('Type', text='Type')
        self.tree.heading('Status', text='Status')
        self.tree.column('Title', width=110)
        self.tree.column('Type', width=45)
        self.tree.column('Status', width=55)
        self.tree.pack(fill='x', expand=True, pady=5)

    def create_preview_panel(self):
        self.board_bg = tk.Frame(self.main_container, bg='#0f172a')
        self.main_container.add(self.board_bg, weight=3)

        self.header_frame = tk.Frame(self.board_bg, bg='#1e293b', height=160)
        self.header_frame.pack(fill='x', side='top', padx=10, pady=10)

        self.lbl_l_logo = tk.Label(self.header_frame, bg='#1e293b')
        self.lbl_l_logo.pack(side='left', padx=15)

        self.title_box = tk.Frame(self.header_frame, bg='#1e293b')
        self.title_box.pack(side='left', expand=True)

        self.lbl_motto_top = tk.Label(self.title_box, fg='#94a3b8', bg='#1e293b')
        self.lbl_c_en = tk.Label(self.title_box, fg='#f8fafc', bg='#1e293b')
        self.lbl_c_am = tk.Label(self.title_box, fg='#38bdf8', bg='#1e293b')
        self.lbl_c_local = tk.Label(self.title_box, fg='#f59e0b', bg='#1e293b')
        self.lbl_motto_bottom = tk.Label(self.title_box, fg='#94a3b8', bg='#1e293b')

        self.lbl_r_logo = tk.Label(self.header_frame, bg='#1e293b')
        self.lbl_r_logo.pack(side='right', padx=15)

        self.marquee_frame = tk.Frame(self.board_bg, bg='#0284c7', height=35)
        self.marquee_frame.pack(fill='x', padx=10)
        self.lbl_headline = tk.Label(self.marquee_frame, fg='white', bg='#0284c7')
        self.lbl_headline.pack(pady=4)

        self.body_canvas = tk.Canvas(self.board_bg, bg='#0f172a', highlightthickness=0)
        self.body_scroll = ttk.Scrollbar(self.board_bg, orient='vertical', command=self.body_canvas.yview)
        self.cards_frame = tk.Frame(self.body_canvas, bg='#0f172a')
        
        self.cards_frame.bind('<Configure>', lambda e: self.body_canvas.configure(scrollregion=self.body_canvas.bbox('all')))
        self.body_canvas.create_window((0, 0), window=self.cards_frame, anchor='nw')
        self.body_canvas.configure(yscrollcommand=self.body_scroll.set)
        
        self.body_canvas.pack(side='left', fill='both', expand=True, padx=(10, 0), pady=10)
        self.body_scroll.pack(side='right', fill='y', padx=(0, 10), pady=10)

    def update_darkness_label(self):
        self.lbl_darkness_val.config(text=f"{self.darkness_var.get()}%")

    def on_speed_change(self, val):
        self.scroll_delay = int(float(val))

    def start_auto_scroll(self):
        if self.auto_scroll_active:
            top, bottom = self.body_canvas.yview()
            if bottom >= 1.0:
                self.scroll_direction = -1
            elif top <= 0.0:
                self.scroll_direction = 1

            self.body_canvas.yview_scroll(self.scroll_direction, "units")

        self.root.after(self.scroll_delay, self.start_auto_scroll)

    def toggle_auto_scroll(self):
        self.auto_scroll_active = not self.auto_scroll_active
        if self.auto_scroll_active:
            self.scroll_btn.config(text='⏹ STOP AUTO-SCROLL')
        else:
            self.scroll_btn.config(text='▶ START AUTO-SCROLL')

    def select_bg_image(self):
        f = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if f:
            dest = IMAGES / Path(f).name
            shutil.copy(f, dest)
            d['bg_image'] = str(dest)
            save_data(d)
            self.refresh_display()

    def select_logo(self, target_key):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if file_path:
            dest = LOGOS / Path(file_path).name
            shutil.copy(file_path, dest)
            d[target_key] = str(dest)
            save_data(d)
            self.refresh_display()

    def save_settings(self):
        for key in self.vars:
            d[key] = self.vars[key].get()
        d['motto_position'] = self.motto_pos_var.get()
        d['font_en'] = self.font_en_var.get()
        d['font_am'] = self.font_am_var.get()
        d['font_size_header'] = self.h_size_var.get()
        d['font_size_body'] = self.b_size_var.get()
        d['bg_darkness'] = self.darkness_var.get()
        d['scroll_speed'] = self.speed_var.get()

        if save_data(d):
            messagebox.showinfo('Success', 'Header & Styling settings saved!')
            self.refresh_display()

    def refresh_display(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for notice in d.get('notices', []):
            status = '[ON]' if notice.get('active', True) else '[OFF]'
            self.tree.insert('', 'end', values=(notice.get('title'), notice.get('type'), status))

        font_en = d.get('font_en', 'Segoe UI')
        font_am = d.get('font_am', 'Abyssinica SIL')
        size_h = int(d.get('font_size_header', 17))
        size_b = int(d.get('font_size_body', 11))

        self.lbl_c_en.config(text=d.get('college_en', ''), font=(font_en, size_h, 'bold'))
        self.lbl_c_am.config(text=d.get('college_am', ''), font=(font_am, max(size_h - 2, 10), 'bold'))
        self.lbl_c_local.config(text=d.get('college_local', ''), font=(font_en, max(size_h - 6, 9), 'italic'))
        
        self.lbl_motto_top.config(font=(font_en, max(size_h - 7, 9), 'italic'))
        self.lbl_motto_bottom.config(font=(font_en, max(size_h - 7, 9), 'italic'))

        self.lbl_motto_top.pack_forget()
        self.lbl_c_en.pack_forget()
        self.lbl_c_am.pack_forget()
        self.lbl_c_local.pack_forget()
        self.lbl_motto_bottom.pack_forget()

        m_text = f"“{d.get('motto', '')}”"
        if d.get('motto_position') == 'TOP':
            self.lbl_motto_top.config(text=m_text)
            self.lbl_motto_top.pack()
            self.lbl_c_en.pack()
            self.lbl_c_am.pack()
            self.lbl_c_local.pack()
        else:
            self.lbl_c_en.pack()
            self.lbl_c_am.pack()
            self.lbl_c_local.pack()
            self.lbl_motto_bottom.config(text=m_text)
            self.lbl_motto_bottom.pack(pady=2)

        self.lbl_headline.config(
            text=f"📢 {d.get('headline_en', '')} | {d.get('headline_am', '')}",
            font=(font_en, 12, 'bold')
        )

        self.load_logo_img(d.get('left_logo'), self.lbl_l_logo)
        self.load_logo_img(d.get('right_logo'), self.lbl_r_logo)

        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        self.card_images.clear()
        self.video_players.clear()

        for n in d.get('notices', []):
            if not n.get('active', True):
                continue

            card = tk.Frame(self.cards_frame, bg='#1e293b', bd=1, relief='solid', highlightthickness=0, cursor='hand2')
            card.pack(fill='x', expand=True, padx=15, pady=8)

            c_head = tk.Frame(card, bg='#334155')
            c_head.pack(fill='x')
            
            n_type = n.get('type', 'text').upper()
            tk.Label(c_head, text=f"[{n_type}] {n.get('title', '')}", font=(font_en, 12, 'bold'), fg='#f1f5f9', bg='#334155', anchor='w').pack(side='left', padx=10, pady=5)
            tk.Label(c_head, text=n.get('date', ''), font=(font_en, 9), fg='#cbd5e1', bg='#334155').pack(side='right', padx=10)

            img_path = n.get('image', '')
            if img_path and Path(img_path).exists():
                try:
                    img = Image.open(img_path)
                    img.thumbnail((500, 250))
                    photo = ImageTk.PhotoImage(img)
                    self.card_images.append(photo)
                    img_lbl = tk.Label(card, image=photo, bg='#1e293b')
                    img_lbl.pack(pady=5)
                except Exception as err:
                    print(f"Error loading image: {err}")

            body_lbl = tk.Label(card, text=n.get('body', ''), font=(font_am if any(ord(char) > 127 for char in n.get('body', '')) else font_en, size_b), fg='#e2e8f0', bg='#1e293b', justify='left', wraplength=700, anchor='w')
            body_lbl.pack(fill='x', padx=12, pady=10)

    def load_logo_img(self, path_str, label_widget):
        if path_str and Path(path_str).exists():
            try:
                img = Image.open(path_str).resize((80, 80), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                label_widget.config(image=photo)
                label_widget.image = photo
                return
            except Exception as e:
                print(f"Error loading image: {e}")
        label_widget.config(image='', text='')

    def add_notice(self):
        self.notice_dialog()

    def edit_notice(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning('Warning', 'Select a notice to edit')
            return
        idx = self.tree.index(selected[0])
        self.notice_dialog(edit_index=idx)

    def delete_notice(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning('Warning', 'Select a notice to delete')
            return
        idx = self.tree.index(selected[0])
        del d['notices'][idx]
        save_data(d)
        self.refresh_display()

    def notice_dialog(self, edit_index=None):
        dlg = tk.Toplevel(self.root)
        dlg.title('Notice Editor')
        dlg.geometry('480x620')
        dlg.grab_set()
        
        notice_data = d['notices'][edit_index] if edit_index is not None else {}
        is_active = notice_data.get('active', True)

        ttk.Label(dlg, text='Title:').pack(anchor='w', padx=10, pady=(10, 0))
        t_entry = ttk.Entry(dlg)
        t_entry.insert(0, notice_data.get('title', ''))
        t_entry.pack(fill='x', padx=10)

        ttk.Label(dlg, text='Date:').pack(anchor='w', padx=10, pady=(5, 0))
        d_entry = ttk.Entry(dlg)
        d_entry.insert(0, notice_data.get('date', datetime.now().strftime('%d/%m/%Y')))
        d_entry.pack(fill='x', padx=10)

        ttk.Label(dlg, text='Notice Type:').pack(anchor='w', padx=10, pady=(5, 0))
        type_var = tk.StringVar(value=notice_data.get('type', 'text'))
        type_cb = ttk.Combobox(dlg, textvariable=type_var, values=['text', 'image', 'video'], state='readonly')
        type_cb.pack(fill='x', padx=10)

        # ON/OFF Notice Switch
        switch_var = tk.BooleanVar(value=is_active)
        
        def update_switch_text():
            if switch_var.get():
                switch_btn.config(text="🟢 NOTICE DISPLAY: ON (ACTIVE)", bg="#16a34a", fg="white")
            else:
                switch_btn.config(text="🔴 NOTICE DISPLAY: OFF (HIDDEN)", bg="#dc2626", fg="white")

        def toggle_switch():
            switch_var.set(not switch_var.get())
            update_switch_text()

        ttk.Label(dlg, text='Notice Status (Display Switch):').pack(anchor='w', padx=10, pady=(8, 0))
        switch_btn = tk.Button(dlg, font=('Segoe UI', 9, 'bold'), command=toggle_switch, relief='flat', pady=4)
        switch_btn.pack(fill='x', padx=10, pady=2)
        update_switch_text()

        img_var = tk.StringVar(value=notice_data.get('image', ''))
        vid_var = tk.StringVar(value=notice_data.get('video', ''))

        def browse_img():
            f = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
            if f:
                dest = IMAGES / Path(f).name
                shutil.copy(f, dest)
                img_var.set(str(dest))

        def browse_vid():
            f = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi *.mkv")])
            if f:
                dest = VIDEOS / Path(f).name
                shutil.copy(f, dest)
                vid_var.set(str(dest))

        def import_doc():
            f = filedialog.askopenfilename(filetypes=[
                ("Document Files", "*.txt *.docx *.pdf"),
                ("Text Files", "*.txt"),
                ("Word Documents", "*.docx"),
                ("PDF Files", "*.pdf")
            ])
            if f:
                ext = Path(f).suffix.lower()
                content = ""
                try:
                    if ext == '.txt':
                        with open(f, 'r', encoding='utf-8', errors='ignore') as file:
                            content = file.read()
                    elif ext == '.docx':
                        try:
                            import docx
                            doc = docx.Document(f)
                            content = "\n".join([p.text for p in doc.paragraphs if p.text])
                        except ImportError:
                            import zipfile
                            import xml.etree.ElementTree as ET
                            with zipfile.ZipFile(f) as z:
                                xml_content = z.read('word/document.xml')
                                tree = ET.fromstring(xml_content)
                                paragraphs = []
                                for p in tree.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
                                    texts = [node.text for node in p.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if node.text]
                                    if texts:
                                        paragraphs.append("".join(texts))
                                content = "\n".join(paragraphs)
                    elif ext == '.pdf':
                        import pypdf
                        reader = pypdf.PdfReader(f)
                        content = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
                    
                    if content:
                        b_text.delete('1.0', tk.END)
                        b_text.insert('1.0', content)
                        messagebox.showinfo('Import Success', 'Text loaded into description box successfully!')
                except Exception as err:
                    messagebox.showerror('Error', f'Could not read file.\nDetails: {err}')

        media_frame = ttk.Frame(dlg)
        media_frame.pack(fill='x', padx=10, pady=5)
        ttk.Button(media_frame, text='📷 Image', command=browse_img).pack(side='left', expand=True, fill='x', padx=2)
        ttk.Button(media_frame, text='🎥 Video', command=browse_vid).pack(side='left', expand=True, fill='x', padx=2)
        ttk.Button(media_frame, text='📄 Import Doc', command=import_doc).pack(side='left', expand=True, fill='x', padx=2)

        ttk.Label(dlg, text='Content / Description:').pack(anchor='w', padx=10, pady=(5, 0))
        b_text = tk.Text(dlg, height=7)
        b_text.insert('1.0', notice_data.get('body', ''))
        b_text.pack(fill='both', expand=True, padx=10, pady=5)

        def save():
            new_n = {
                'title': t_entry.get(),
                'date': d_entry.get(),
                'type': type_var.get(),
                'body': b_text.get('1.0', tk.END).strip(),
                'image': img_var.get(),
                'video': vid_var.get(),
                'active': switch_var.get()
            }
            if edit_index is not None:
                d['notices'][edit_index] = new_n
            else:
                d['notices'].append(new_n)
            save_data(d)
            self.refresh_display()
            dlg.destroy()

        ttk.Button(dlg, text='💾 Save Notice', command=save).pack(pady=10)

if __name__ == '__main__':
    flask_thread = threading.Thread(target=lambda: web_app.run(host='0.0.0.0', port=5000, debug=False))
    flask_thread.daemon = True
    flask_thread.start()

    root = tk.Tk()
    app = DigitalNoticeBoard(root)
    root.mainloop()