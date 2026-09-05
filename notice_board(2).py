import json
import os
import platform
import shutil
import subprocess
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

try:
    from PIL import Image, ImageTk
except ImportError:
    raise SystemExit('Install Pillow first: python -m pip install pillow')

try:
    import docx
except ImportError:
    docx = None

BASE = Path(__file__).resolve().parent
DATA = BASE / 'noticeboard_data.json'
LOGOS = BASE / 'logos'
PROFILES = BASE / 'profiles'
LOGOS.mkdir(exist_ok=True)
PROFILES.mkdir(exist_ok=True)

DEFAULT = {
    'admin_password': '1234',
    'display_mode': 'LOCAL DISPLAY',
    'local_ip': '192.168.1.100:8080',
    'remote_ip': '10.240.0.15:9000',
    'timezone': 'EAT (UTC+3)',
    'college_en': 'YIRGALEM POLYTECHNIC COLLEGE',
    'college_am': 'ይርጋለም ፖሊ ቴክኒክ ኮሌጅ',
    'college_sid': 'IRGALAME POOLITEKNIKKE KOLLEEJ',
    'motto': 'SKILLS AND INNOVATION FOR BETTER GENERATION!',
    'headline_en': 'DIGITAL NOTICE BOARD',
    'headline_am': 'ዲጂታል ማስታወቂያ ሰሌዳ',
    'left_logo': '',
    'right_logo': '',
    'font_am_family': 'Nyala',
    'font_am_size': '12',
    'font_en_family': 'Segoe UI',
    'font_en_size': '11',
    'bottom_ticker_news': '🔴 ሰበር ዜና / URGENT NEWS: Welcome to Yirgalem Polytechnic College Digital Notice Board!',
    'email': 'yirgalempoly@gmail.com',
    'po_box': 'P.O. Box: 188',
    'phone': '+251 462251413',
    'address': 'Yirgalem, Sidama Region, Ethiopia',
    'college_situation': {
        'status_am': 'ወቅታዊ ሁኔታ: የትምህርትና ስልጠና ሂደት በሰላም እየተካሄደ ይገኛል።',
        'status_en': 'Academic activities & technical training in progress.',
        'trainees': '3,500+',
        'staff': '145',
        'projects': '12 Prototypes',
    },
    'prepared_profile': {
        'name': 'In. TEMESGEN SAMUA ASSEFA',
        'role': 'System Admin & Presenter',
        'photo': '',
    },
    'exhibits': [
        {
            'title': 'Solar Bird Deterrent System',
            'type': 'VIDEO',
            'file': '',
        },
        {
            'title': 'WAN Digital Notice Board',
            'type': 'DOC',
            'file': '',
        },
    ],
    'notices': [
        {
            'title': 'Student Registration',
            'date': '26/12/2018 E.C',
            'display_time': '10',
            'body': 'Students are informed to complete registration according to the college schedule.',
            'media_type': 'TEXT',
            'file_path': '',
        },
        {
            'title': 'Innovation Exhibition',
            'date': 'Upcoming',
            'display_time': '15',
            'body': 'Annual technology prototype exhibition.',
            'media_type': 'TEXT',
            'file_path': '',
        },
    ],
}


def load():
    if DATA.exists():
        try:
            d_loaded = json.loads(DATA.read_text(encoding='utf-8'))
            DEFAULT.update(d_loaded)
        except Exception:
            pass
    return DEFAULT


d = load()


def save():
    DATA.write_text(
        json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8'
    )


def read_docx_lines(file_path):
    if not file_path or not Path(file_path).exists():
        return ''
    if docx is None:
        return '[Docx Error: python-docx not installed]'
    try:
        doc = docx.Document(file_path)
        return '\n'.join(
            [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        )
    except Exception as e:
        return f'[Docx Error: {str(e)}]'


class NoticeEditDialog(tk.Toplevel):
    def __init__(self, parent, notice_data=None):
        super().__init__(parent)
        self.title('Edit Notice' if notice_data else 'Add New Notice')
        self.geometry('450x520')
        self.resizable(False, False)
        self.grab_set()

        self.result = None
        self.notice = notice_data or {
            'title': '',
            'date': time.strftime('%d/%m/%Y'),
            'display_time': '10',
            'media_type': 'TEXT',
            'body': '',
            'file_path': '',
        }

        self.build_ui()

    def build_ui(self):
        pad = {'padx': 10, 'pady': 4}

        tk.Label(
            self, text='Notice Title / Headline:', font=('Segoe UI', 9, 'bold')
        ).pack(anchor='w', **pad)
        self.ent_title = tk.Entry(self, font=('Segoe UI', 10))
        self.ent_title.insert(0, self.notice.get('title', ''))
        self.ent_title.pack(fill='x', **pad)

        tk.Label(self, text='Date:', font=('Segoe UI', 9, 'bold')).pack(
            anchor='w', **pad
        )
        self.ent_date = tk.Entry(self, font=('Segoe UI', 10))
        self.ent_date.insert(0, self.notice.get('date', ''))
        self.ent_date.pack(fill='x', **pad)

        row_f = tk.Frame(self)
        row_f.pack(fill='x', **pad)

        tk.Label(
            row_f, text='Notice Type:', font=('Segoe UI', 9, 'bold')
        ).grid(row=0, column=0, sticky='w')
        self.cmb_type = ttk.Combobox(
            row_f,
            values=['TEXT', 'DOC', 'PDF', 'VIDEO', 'IMAGE'],
            state='readonly',
            width=12,
        )
        self.cmb_type.set(self.notice.get('media_type', 'TEXT'))
        self.cmb_type.grid(row=1, column=0, padx=(0, 10), sticky='w')

        tk.Label(
            row_f, text='Play Time (Sec):', font=('Segoe UI', 9, 'bold')
        ).grid(row=0, column=1, sticky='w')
        self.spn_time = tk.Spinbox(
            row_f, from_=3, to=300, width=10, font=('Segoe UI', 10)
        )
        self.spn_time.delete(0, 'end')
        self.spn_time.insert(0, str(self.notice.get('display_time', '10')))
        self.spn_time.grid(row=1, column=1, sticky='w')

        tk.Label(
            self, text='Attached Media/File Path:', font=('Segoe UI', 9, 'bold')
        ).pack(anchor='w', **pad)
        f_frame = tk.Frame(self)
        f_frame.pack(fill='x', **pad)
        self.ent_file = tk.Entry(f_frame, font=('Segoe UI', 9))
        self.ent_file.insert(0, self.notice.get('file_path', ''))
        self.ent_file.pack(side='left', fill='x', expand=True, padx=(0, 5))
        tk.Button(
            f_frame, text='Browse...', command=self.browse_file
        ).pack(side='right')

        tk.Label(
            self, text='Notice Content / Body:', font=('Segoe UI', 9, 'bold')
        ).pack(anchor='w', **pad)
        self.txt_body = tk.Text(self, height=6, font=('Nyala', 11))
        self.txt_body.insert('1.0', self.notice.get('body', ''))
        self.txt_body.pack(fill='both', expand=True, **pad)

        btn_f = tk.Frame(self)
        btn_f.pack(fill='x', pady=10)
        tk.Button(
            btn_f,
            text='💾 Done',
            bg='#00FF66',
            font=('Segoe UI', 9, 'bold'),
            command=self.save_data,
        ).pack(side='right', padx=10)
        tk.Button(btn_f, text='Cancel', command=self.destroy).pack(
            side='right'
        )

    def browse_file(self):
        p = filedialog.askopenfilename()
        if p:
            self.ent_file.delete(0, 'end')
            self.ent_file.insert(0, str(Path(p).resolve()))
            ext = Path(p).suffix.lower()
            if ext in ['.docx', '.doc']:
                self.cmb_type.set('DOC')
            elif ext == '.pdf':
                self.cmb_type.set('PDF')
            elif ext in ['.mp4', '.avi', '.mkv']:
                self.cmb_type.set('VIDEO')
            elif ext in ['.png', '.jpg', '.jpeg', '.webp']:
                self.cmb_type.set('IMAGE')

    def save_data(self):
        title = self.ent_title.get().strip()
        if not title:
            messagebox.showerror('Error', 'Notice Title is required!')
            return

        self.result = {
            'title': title,
            'date': self.ent_date.get().strip(),
            'media_type': self.cmb_type.get(),
            'display_time': self.spn_time.get().strip(),
            'file_path': self.ent_file.get().strip(),
            'body': self.txt_body.get('1.0', 'end-1c').strip(),
        }
        self.destroy()


class ExhibitEditDialog(tk.Toplevel):
    def __init__(self, parent, exhibit_data=None):
        super().__init__(parent)
        self.title('Edit Exhibition Item' if exhibit_data else 'Add Exhibition Item')
        self.geometry('420x260')
        self.resizable(False, False)
        self.grab_set()

        self.result = None
        self.exhibit = exhibit_data or {
            'title': '',
            'type': 'VIDEO',
            'file': '',
        }

        self.build_ui()

    def build_ui(self):
        pad = {'padx': 10, 'pady': 6}

        tk.Label(
            self, text='Exhibit Project Title:', font=('Segoe UI', 9, 'bold')
        ).pack(anchor='w', **pad)
        self.ent_title = tk.Entry(self, font=('Segoe UI', 10))
        self.ent_title.insert(0, self.exhibit.get('title', ''))
        self.ent_title.pack(fill='x', **pad)

        tk.Label(
            self, text='Exhibit Media Type:', font=('Segoe UI', 9, 'bold')
        ).pack(anchor='w', **pad)
        self.cmb_type = ttk.Combobox(
            self,
            values=['VIDEO', 'IMAGE', 'DOC', 'PDF', 'SIMULATION'],
            state='readonly',
        )
        self.cmb_type.set(self.exhibit.get('type', 'VIDEO'))
        self.cmb_type.pack(fill='x', **pad)

        tk.Label(
            self, text='Attached File Path:', font=('Segoe UI', 9, 'bold')
        ).pack(anchor='w', **pad)
        f_frame = tk.Frame(self)
        f_frame.pack(fill='x', **pad)
        self.ent_file = tk.Entry(f_frame, font=('Segoe UI', 9))
        self.ent_file.insert(0, self.exhibit.get('file', ''))
        self.ent_file.pack(side='left', fill='x', expand=True, padx=(0, 5))
        tk.Button(
            f_frame, text='Browse...', command=self.browse_file
        ).pack(side='right')

        btn_f = tk.Frame(self)
        btn_f.pack(fill='x', pady=15)
        tk.Button(
            btn_f,
            text='💾 Save Item',
            bg='#00FF66',
            font=('Segoe UI', 9, 'bold'),
            command=self.save_data,
        ).pack(side='right', padx=10)
        tk.Button(btn_f, text='Cancel', command=self.destroy).pack(
            side='right'
        )

    def browse_file(self):
        p = filedialog.askopenfilename()
        if p:
            self.ent_file.delete(0, 'end')
            self.ent_file.insert(0, str(Path(p).resolve()))

    def save_data(self):
        title = self.ent_title.get().strip()
        if not title:
            messagebox.showerror('Error', 'Exhibit Title is required!')
            return

        self.result = {
            'title': title,
            'type': self.cmb_type.get(),
            'file': self.ent_file.get().strip(),
        }
        self.destroy()


class App:
    def __init__(self, r):
        self.r = r
        self.r.title('Yirgalem Polytechnic College - Bright LED Board')
        self.r.geometry('1366x768')
        self.r.configure(bg='#000000')

        self.offset = 0
        self.total = 1
        self.paused = False
        self.logo_angle = 0
        self.current_notice_idx = 0
        self.notice_timer_start = time.time()
        self.blink_state = False
        self.current_exhibit_idx = 0

        self.ticker_x = 1200
        self.ticker_blink_toggle = False

        self.entries = {}
        self.profile_img_ph = None

        self.setup_fonts()
        self.make_top_navigation()
        self.make_editor()
        self.make_preview()
        self.refresh()
        self.update_clock()
        self.animate_and_blink_logos()
        self.scroll()
        self.animate_ticker()

    def setup_fonts(self):
        am_fam = d.get('font_am_family', 'Nyala')
        am_sz = int(d.get('font_am_size', '12'))
        en_fam = d.get('font_en_family', 'Segoe UI')
        en_sz = int(d.get('font_en_size', '11'))

        self.font_header_am = (am_fam, am_sz + 2, 'bold')
        self.font_header_en = (en_fam, en_sz + 3, 'bold')
        self.font_body_am = (am_fam, am_sz, 'bold')
        self.font_body_en = (en_fam, en_sz, 'bold')
        self.font_ticker = (am_fam, am_sz + 1, 'bold')

    def check_password(self):
        pwd = tk.simpledialog.askstring(
            'Admin Security', 'Enter Admin Password:', show='*'
        )
        if pwd == d.get('admin_password', '1234'):
            return True
        messagebox.showerror('Access Denied', 'Incorrect Admin Password!')
        return False

    def launch_file(self, file_path):
        if not file_path or not Path(file_path).exists():
            if messagebox.askyesno(
                'File Error',
                f'ፋይሉ አልተገኘም:\n{file_path}\n\nአዲስ ፋይል መምረጥ ይፈልጋሉ?',
            ):
                p = filedialog.askopenfilename()
                if p:
                    file_path = str(Path(p).resolve())
                else:
                    return
            else:
                return

        try:
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':
                subprocess.call(('open', file_path))
            else:
                subprocess.call(('xdg-open', file_path))
        except Exception as e:
            messagebox.showerror(
                'Execution Error', f'ፋይሉን መክፈት አልተቻለም:\n{str(e)}'
            )

    def make_top_navigation(self):
        self.nav_bar = tk.Frame(
            self.r,
            bg='#050A14',
            height=36,
            highlightthickness=1,
            highlightbackground='#00FFFF',
        )
        self.nav_bar.pack(side='top', fill='x')

        self.lbl_route_banner = tk.Label(
            self.nav_bar,
            text=f"ROUTE: REMOTE DISPLAY (IP-TV) | LOCAL: {d['local_ip']} | REMOTE: {d['remote_ip']}",
            bg='#002244',
            fg='#00FFFF',
            font=('Consolas', 8, 'bold'),
            padx=6,
            pady=2,
            relief='ridge',
        )
        self.lbl_route_banner.pack(side='left', padx=5, pady=3)

        self.btn_admin_mode = tk.Button(
            self.nav_bar,
            text='🔒 ADMIN PANEL',
            bg='#0055FF',
            fg='white',
            font=('Segoe UI', 8, 'bold'),
            command=self.show_admin_view,
        )
        self.btn_admin_mode.pack(side='left', padx=3, pady=3)

        self.btn_customer_mode = tk.Button(
            self.nav_bar,
            text='📺 LED DISPLAY',
            bg='#00FF66',
            fg='black',
            font=('Segoe UI', 8, 'bold'),
            command=self.show_customer_view,
        )
        self.btn_customer_mode.pack(side='left', padx=3, pady=3)

        self.display_route_var = tk.StringVar(
            value=d.get('display_mode', 'LOCAL DISPLAY')
        )
        self.route_dropdown = ttk.Combobox(
            self.nav_bar,
            textvariable=self.display_route_var,
            values=[
                'WEB SERVER (WAN)',
                'LOCAL DISPLAY (HDMI 1)',
                'REMOTE DISPLAY (IP-TV)',
            ],
            state='readonly',
            width=18,
        )
        self.route_dropdown.pack(side='left', padx=5, pady=3)

        self.lbl_clock = tk.Label(
            self.nav_bar,
            text='',
            bg='#050A14',
            fg='#FFFF00',
            font=('Consolas', 9, 'bold'),
        )
        self.lbl_clock.pack(side='right', padx=(5, 10))

        self.blink_canvas = tk.Canvas(
            self.nav_bar,
            width=14,
            height=14,
            bg='#050A14',
            highlightthickness=0,
        )
        self.blink_canvas.pack(side='right', padx=2)
        self.led_circle = self.blink_canvas.create_oval(
            2, 2, 12, 12, fill='#00FF00', outline='#FFFFFF', width=1
        )

    def update_clock(self):
        current_time = time.strftime('%I:%M:%S %p')
        tz = d.get('timezone', 'EAT (UTC+3)')
        self.lbl_clock.config(text=f'🕒 {current_time} | {tz}')
        self.r.after(1000, self.update_clock)

    def animate_and_blink_logos(self):
        self.blink_state = not self.blink_state
        self.logo_angle = (self.logo_angle + 15) % 360
        glow_color = '#00FF00' if self.blink_state else '#003300'
        self.blink_canvas.itemconfig(self.led_circle, fill=glow_color)
        self.render_logos(self.logo_angle)
        self.r.after(200, self.animate_and_blink_logos)

    def render_logos(self, angle):
        for cv, key in [
            (self.l_canvas, 'left_logo'),
            (self.r_canvas, 'right_logo'),
        ]:
            cv.delete('all')
            if d[key] and Path(d[key]).exists():
                try:
                    im = Image.open(d[key]).convert('RGBA')
                    im = im.rotate(angle)
                    im.thumbnail((70, 70))
                    ph = ImageTk.PhotoImage(im)
                    cv.create_image(37, 37, image=ph)
                    cv.image = ph
                except Exception:
                    cv.create_text(
                        37,
                        37,
                        text='[LOGO]',
                        fill='#00FFFF',
                        font=('Consolas', 9, 'bold'),
                    )
            else:
                cv.create_text(
                    37,
                    37,
                    text='[LOGO]',
                    fill='#00FFFF',
                    font=('Consolas', 9, 'bold'),
                )

    def show_admin_view(self):
        if self.check_password():
            self.admin_outer.pack(side='left', fill='y')
            self.r.attributes('-fullscreen', False)

    def show_customer_view(self):
        self.admin_outer.pack_forget()
        self.r.attributes('-fullscreen', True)

    def make_editor(self):
        self.admin_outer = tk.Frame(
            self.r,
            bg='#EAEAEA',
            highlightthickness=1,
            highlightbackground='#CCCCCC',
        )
        self.admin_outer.pack(side='left', fill='y')

        self.admin_canvas = tk.Canvas(
            self.admin_outer, width=330, bg='#EAEAEA', highlightthickness=0
        )
        self.admin_scrollbar = ttk.Scrollbar(
            self.admin_outer,
            orient='vertical',
            command=self.admin_canvas.yview,
        )
        self.left_frame = tk.Frame(
            self.admin_canvas, bg='#EAEAEA', padx=8, pady=8
        )

        self.left_frame.bind(
            '<Configure>',
            lambda e: self.admin_canvas.configure(
                scrollregion=self.admin_canvas.bbox('all')
            ),
        )
        self.admin_canvas.create_window(
            (0, 0), window=self.left_frame, anchor='nw'
        )
        self.admin_canvas.configure(yscrollcommand=self.admin_scrollbar.set)

        self.admin_canvas.pack(side='left', fill='both', expand=True)
        self.admin_scrollbar.pack(side='right', fill='y')

        # Section 1: Edit Notices Tool
        tk.Label(
            self.left_frame,
            text='📢 EDIT NOTICES TOOL',
            font=('Segoe UI', 10, 'bold'),
            bg='#EAEAEA',
            fg='#003366',
        ).pack(anchor='w', pady=(0, 2))

        table_frame = tk.Frame(self.left_frame, bg='#FFFFFF', bd=1, relief='solid')
        table_frame.pack(fill='x', pady=2)

        columns = ('title', 'type', 'sec')
        self.notice_tree = ttk.Treeview(
            table_frame, columns=columns, show='headings', height=4
        )
        self.notice_tree.heading('title', text='Title')
        self.notice_tree.heading('type', text='Type')
        self.notice_tree.heading('sec', text='Sec')
        self.notice_tree.column('title', width=130)
        self.notice_tree.column('type', width=55)
        self.notice_tree.column('sec', width=35)
        self.notice_tree.pack(fill='both', expand=True)

        self.populate_notice_tree()

        btn_f = tk.Frame(self.left_frame, bg='#EAEAEA')
        btn_f.pack(fill='x', pady=3)

        tk.Button(
            btn_f,
            text='➕ Add',
            bg='#E1F5FE',
            font=('Segoe UI', 8),
            command=self.add_new_notice,
        ).pack(side='left', expand=True, fill='x', padx=(0, 1))
        tk.Button(
            btn_f,
            text='✏️ Edit',
            bg='#FFF9C4',
            font=('Segoe UI', 8),
            command=self.edit_selected_notice,
        ).pack(side='left', expand=True, fill='x', padx=1)
        tk.Button(
            btn_f,
            text='🗑️ Del',
            bg='#FFCDD2',
            font=('Segoe UI', 8),
            command=self.delete_selected_notice,
        ).pack(side='left', expand=True, fill='x', padx=(1, 0))

        tk.Frame(self.left_frame, height=1, bg='#BBBBBB').pack(fill='x', pady=5)

        # Section 2: College Technology Exhibition Manager Tool
        tk.Label(
            self.left_frame,
            text='🔬 EXHIBITION MANAGER TOOL',
            font=('Segoe UI', 10, 'bold'),
            bg='#EAEAEA',
            fg='#003366',
        ).pack(anchor='w', pady=(0, 2))

        ex_table_frame = tk.Frame(
            self.left_frame, bg='#FFFFFF', bd=1, relief='solid'
        )
        ex_table_frame.pack(fill='x', pady=2)

        ex_cols = ('title', 'type')
        self.exhibit_tree = ttk.Treeview(
            ex_table_frame, columns=ex_cols, show='headings', height=3
        )
        self.exhibit_tree.heading('title', text='Exhibit Title')
        self.exhibit_tree.heading('type', text='Type')
        self.exhibit_tree.column('title', width=150)
        self.exhibit_tree.column('type', width=65)
        self.exhibit_tree.pack(fill='both', expand=True)

        self.populate_exhibit_tree()

        ex_btn_f = tk.Frame(self.left_frame, bg='#EAEAEA')
        ex_btn_f.pack(fill='x', pady=3)

        tk.Button(
            ex_btn_f,
            text='➕ Add Exhibit',
            bg='#E1F5FE',
            font=('Segoe UI', 8),
            command=self.add_new_exhibit,
        ).pack(side='left', expand=True, fill='x', padx=(0, 1))
        tk.Button(
            ex_btn_f,
            text='✏️ Edit',
            bg='#FFF9C4',
            font=('Segoe UI', 8),
            command=self.edit_selected_exhibit,
        ).pack(side='left', expand=True, fill='x', padx=1)
        tk.Button(
            ex_btn_f,
            text='🗑️ Del',
            bg='#FFCDD2',
            font=('Segoe UI', 8),
            command=self.delete_selected_exhibit,
        ).pack(side='left', expand=True, fill='x', padx=(1, 0))

        tk.Frame(self.left_frame, height=1, bg='#BBBBBB').pack(fill='x', pady=5)

        # Section 3: College Situation & Status Editor
        tk.Label(
            self.left_frame,
            text='🏫 COLLEGE SITUATION & STATES',
            font=('Segoe UI', 10, 'bold'),
            bg='#EAEAEA',
            fg='#003366',
        ).pack(anchor='w', pady=(0, 2))

        sit = d.get('college_situation', {})

        tk.Label(
            self.left_frame,
            text='Status Amharic:',
            font=('Segoe UI', 8),
            bg='#EAEAEA',
        ).pack(anchor='w')
        self.ent_sit_am = tk.Entry(self.left_frame, font=('Nyala', 9))
        self.ent_sit_am.insert(0, sit.get('status_am', ''))
        self.ent_sit_am.pack(fill='x', pady=(0, 2))

        tk.Label(
            self.left_frame,
            text='Status English:',
            font=('Segoe UI', 8),
            bg='#EAEAEA',
        ).pack(anchor='w')
        self.ent_sit_en = tk.Entry(self.left_frame, font=('Segoe UI', 8))
        self.ent_sit_en.insert(0, sit.get('status_en', ''))
        self.ent_sit_en.pack(fill='x', pady=(0, 2))

        st_grid = tk.Frame(self.left_frame, bg='#EAEAEA')
        st_grid.pack(fill='x', pady=2)

        tk.Label(
            st_grid, text='Trainees:', bg='#EAEAEA', font=('Segoe UI', 8)
        ).grid(row=0, column=0, sticky='w')
        self.ent_sit_trainees = tk.Entry(st_grid, width=11, font=('Segoe UI', 8))
        self.ent_sit_trainees.insert(0, sit.get('trainees', '3,500+'))
        self.ent_sit_trainees.grid(row=1, column=0, padx=(0, 4))

        tk.Label(
            st_grid, text='Staff:', bg='#EAEAEA', font=('Segoe UI', 8)
        ).grid(row=0, column=1, sticky='w')
        self.ent_sit_staff = tk.Entry(st_grid, width=11, font=('Segoe UI', 8))
        self.ent_sit_staff.insert(0, sit.get('staff', '145'))
        self.ent_sit_staff.grid(row=1, column=1)

        tk.Label(
            self.left_frame,
            text='Projects / Prototypes:',
            font=('Segoe UI', 8),
            bg='#EAEAEA',
        ).pack(anchor='w', pady=(2, 0))
        self.ent_sit_projects = tk.Entry(self.left_frame, font=('Segoe UI', 8))
        self.ent_sit_projects.insert(0, sit.get('projects', '12 Prototypes'))
        self.ent_sit_projects.pack(fill='x', pady=(0, 2))

        tk.Frame(self.left_frame, height=1, bg='#BBBBBB').pack(fill='x', pady=5)

        # Section 4: Prepared Profile / Presenter Tool
        tk.Label(
            self.left_frame,
            text='👤 PREPARED BY PROFILE',
            font=('Segoe UI', 10, 'bold'),
            bg='#EAEAEA',
            fg='#003366',
        ).pack(anchor='w', pady=(0, 2))

        prof = d.get('prepared_profile', {})

        tk.Label(
            self.left_frame,
            text='Presenter Name:',
            font=('Segoe UI', 8),
            bg='#EAEAEA',
        ).pack(anchor='w')
        self.ent_prof_name = tk.Entry(self.left_frame, font=('Segoe UI', 8))
        self.ent_prof_name.insert(0, prof.get('name', ''))
        self.ent_prof_name.pack(fill='x', pady=(0, 2))

        tk.Label(
            self.left_frame,
            text='Role / Title:',
            font=('Segoe UI', 8),
            bg='#EAEAEA',
        ).pack(anchor='w')
        self.ent_prof_role = tk.Entry(self.left_frame, font=('Segoe UI', 8))
        self.ent_prof_role.insert(0, prof.get('role', ''))
        self.ent_prof_role.pack(fill='x', pady=(0, 2))

        tk.Button(
            self.left_frame,
            text='Upload Presenter Photo',
            bg='#F0F0F0',
            font=('Segoe UI', 8),
            pady=1,
            command=self.upload_presenter_photo,
        ).pack(fill='x', pady=(2, 4))

        tk.Frame(self.left_frame, height=1, bg='#BBBBBB').pack(fill='x', pady=5)

        # Section 5: Red News Ticker & Address Bar Editor
        tk.Label(
            self.left_frame,
            text='📰 TICKER & CONTACT ADDRESS',
            font=('Segoe UI', 10, 'bold'),
            bg='#EAEAEA',
            fg='#003366',
        ).pack(anchor='w', pady=(0, 2))

        address_fields = [
            ('Bottom Red News Ticker', 'bottom_ticker_news'),
            ('Phone Number', 'phone'),
            ('Email Address', 'email'),
            ('P.O. Box', 'po_box'),
            ('Location Address', 'address'),
        ]

        for lbl_t, key in address_fields:
            tk.Label(
                self.left_frame,
                text=lbl_t,
                font=('Segoe UI', 8),
                bg='#EAEAEA',
            ).pack(anchor='w')
            e = tk.Entry(self.left_frame, font=('Segoe UI', 8))
            e.insert(0, d.get(key, ''))
            e.pack(fill='x', pady=(0, 2))
            self.entries[key] = e

        tk.Frame(self.left_frame, height=2, bg='#003366').pack(fill='x', pady=8)

        # Section 6: Unified Save Modifications Button
        btn_save_all = tk.Button(
            self.left_frame,
            text='💾 SAVE ALL MODIFICATIONS',
            bg='#00FF66',
            fg='#000000',
            font=('Segoe UI', 10, 'bold'),
            pady=6,
            command=self.save_all_modifications,
        )
        btn_save_all.pack(fill='x', pady=(0, 10))

    def populate_notice_tree(self):
        for item in self.notice_tree.get_children():
            self.notice_tree.delete(item)
        for n in d.get('notices', []):
            self.notice_tree.insert(
                '',
                'end',
                values=(
                    n.get('title', ''),
                    n.get('media_type', 'TEXT'),
                    n.get('display_time', '10'),
                ),
            )

    def populate_exhibit_tree(self):
        for item in self.exhibit_tree.get_children():
            self.exhibit_tree.delete(item)
        for ex in d.get('exhibits', []):
            self.exhibit_tree.insert(
                '',
                'end',
                values=(
                    ex.get('title', ''),
                    ex.get('type', 'VIDEO'),
                ),
            )

    def add_new_exhibit(self):
        dlg = ExhibitEditDialog(self.r)
        self.r.wait_window(dlg)
        if dlg.result:
            d['exhibits'].append(dlg.result)
            self.populate_exhibit_tree()
            self.refresh()

    def edit_selected_exhibit(self):
        selected = self.exhibit_tree.selection()
        if not selected:
            messagebox.showwarning(
                'Selection Error', 'Select an exhibition item to edit.'
            )
            return
        idx = self.exhibit_tree.index(selected[0])
        exhibit_data = d['exhibits'][idx]

        dlg = ExhibitEditDialog(self.r, exhibit_data=exhibit_data)
        self.r.wait_window(dlg)

        if dlg.result:
            d['exhibits'][idx] = dlg.result
            self.populate_exhibit_tree()
            self.refresh()

    def delete_selected_exhibit(self):
        selected = self.exhibit_tree.selection()
        if not selected:
            messagebox.showwarning(
                'Selection Error', 'Select an exhibit from the table.'
            )
            return
        idx = self.exhibit_tree.index(selected[0])
        d['exhibits'].pop(idx)
        self.populate_exhibit_tree()
        self.refresh()

    def save_all_modifications(self):
        d['college_situation']['status_am'] = self.ent_sit_am.get().strip()
        d['college_situation']['status_en'] = self.ent_sit_en.get().strip()
        d['college_situation']['trainees'] = self.ent_sit_trainees.get().strip()
        d['college_situation']['staff'] = self.ent_sit_staff.get().strip()
        d['college_situation']['projects'] = self.ent_sit_projects.get().strip()

        d['prepared_profile']['name'] = self.ent_prof_name.get().strip()
        d['prepared_profile']['role'] = self.ent_prof_role.get().strip()

        for key, entry in self.entries.items():
            d[key] = entry.get().strip()

        save()
        self.refresh()
        messagebox.showinfo('Success', 'All Admin Modifications Saved Successfully!')

    def upload_presenter_photo(self):
        p = filedialog.askopenfilename(
            filetypes=[('Images', '*.png *.jpg *.jpeg *.webp')]
        )
        if p:
            dest = PROFILES / ('presenter' + Path(p).suffix.lower())
            shutil.copy2(p, dest)
            d['prepared_profile']['photo'] = str(dest.resolve())
            save()
            self.refresh()

    def add_new_notice(self):
        dlg = NoticeEditDialog(self.r)
        self.r.wait_window(dlg)
        if dlg.result:
            d['notices'].append(dlg.result)
            self.populate_notice_tree()
            self.refresh()

    def edit_selected_notice(self):
        selected = self.notice_tree.selection()
        if not selected:
            messagebox.showwarning(
                'Selection Error', 'Select a notice from the table to edit.'
            )
            return
        idx = self.notice_tree.index(selected[0])
        notice_data = d['notices'][idx]

        dlg = NoticeEditDialog(self.r, notice_data=notice_data)
        self.r.wait_window(dlg)

        if dlg.result:
            d['notices'][idx] = dlg.result
            self.populate_notice_tree()
            self.refresh()

    def delete_selected_notice(self):
        selected = self.notice_tree.selection()
        if not selected:
            messagebox.showwarning(
                'Selection Error', 'Select a notice from table first.'
            )
            return
        idx = self.notice_tree.index(selected[0])
        if len(d['notices']) > 1:
            d['notices'].pop(idx)
            self.populate_notice_tree()
            self.refresh()

    def make_preview(self):
        self.p = tk.Frame(self.r, bg='#000000')
        self.p.pack(side='right', fill='both', expand=True, padx=4, pady=4)

        # 1. Top Header Frame
        self.h = tk.Frame(
            self.p,
            bg='#051026',
            height=110,
            highlightthickness=2,
            highlightbackground='#00FFFF',
        )
        self.h.pack(fill='x', side='top')
        self.h.pack_propagate(False)

        self.l_canvas = tk.Canvas(
            self.h,
            width=70,
            height=70,
            bg='#000000',
            highlightthickness=1,
            highlightbackground='#00FFFF',
        )
        self.l_canvas.pack(side='left', padx=8, pady=4)

        self.r_canvas = tk.Canvas(
            self.h,
            width=70,
            height=70,
            bg='#000000',
            highlightthickness=1,
            highlightbackground='#00FFFF',
        )
        self.r_canvas.pack(side='right', padx=8, pady=4)

        c = tk.Frame(self.h, bg='#051026')
        c.pack(expand=True, fill='both')

        self.ce = tk.Label(
            c, bg='#051026', fg='#00FFFF', font=self.font_header_en
        )
        self.ce.pack(pady=(1, 0))
        self.ca = tk.Label(
            c, bg='#051026', fg='#FFFF00', font=self.font_header_am
        )
        self.ca.pack(pady=(1, 0))
        self.cs = tk.Label(
            c, bg='#051026', fg='#00FF66', font=self.font_body_en
        )
        self.cs.pack(pady=(1, 0))

        self.mo = tk.Label(
            c,
            bg='#000000',
            fg='#FF9900',
            font=self.font_body_en,
            pady=1,
        )
        self.mo.pack(fill='x', padx=4, pady=1)

        # 2. Headline Banner
        self.banner = tk.Frame(
            self.p,
            bg='#003366',
            height=24,
            highlightthickness=1,
            highlightbackground='#00FFFF',
        )
        self.banner.pack(fill='x', side='top', pady=2)
        self.banner_lbl = tk.Label(
            self.banner,
            bg='#003366',
            fg='#FFFFFF',
            font=self.font_body_am,
        )
        self.banner_lbl.pack(expand=True)

        # 3. Bottom Scrolling Ticker (Packed BEFORE body to pin to bottom)
        self.bottom_ticker_frame = tk.Frame(
            self.p,
            bg='#110000',
            height=26,
            highlightthickness=1,
            highlightbackground='#FF0000',
        )
        self.bottom_ticker_frame.pack(fill='x', side='bottom', pady=(1, 0))
        self.bottom_ticker_frame.pack_propagate(False)

        self.ticker_canvas = tk.Canvas(
            self.bottom_ticker_frame,
            bg='#000000',
            highlightthickness=0,
        )
        self.ticker_canvas.pack(fill='both', expand=True)

        self.ticker_text_item = self.ticker_canvas.create_text(
            1000,
            13,
            text='',
            font=self.font_ticker,
            fill='#FF0000',
            anchor='w',
        )

        # 4. Bottom College Address Bar (Packed BEFORE body to pin to bottom)
        self.footer_frame = tk.Frame(self.p, bg='#000000')
        self.footer_frame.pack(fill='x', side='bottom', pady=(1, 0))

        self.address_bar = tk.Label(
            self.footer_frame,
            bg='#000000',
            fg='#00FF00',
            font=('Segoe UI', 8, 'bold'),
            pady=2,
            highlightthickness=1,
            highlightbackground='#00FF00',
        )
        self.address_bar.pack(fill='x')

        # 5. Middle Body Display Container
        self.body_frame = tk.Frame(self.p, bg='#000000')
        self.body_frame.pack(fill='both', expand=True, pady=2)

        self.paned = ttk.PanedWindow(self.body_frame, orient='horizontal')
        self.paned.pack(fill='both', expand=True)

        # Left Main Notice Board Screen
        self.notice_frame = tk.Frame(self.paned, bg='#000000')
        self.paned.add(self.notice_frame, weight=7)

        self.c = tk.Canvas(
            self.notice_frame,
            bg='#0A1526',
            highlightthickness=2,
            highlightbackground='#00FFFF',
        )
        self.c.pack(fill='both', expand=True)

        # Right Compact Sidebar Screen
        self.right_frame = tk.Frame(self.paned, bg='#000000')
        self.paned.add(self.right_frame, weight=3)

        # A. Compact Technology Exhibition Component
        self.exhibition_tool = tk.Frame(
            self.right_frame,
            bg='#051026',
            highlightthickness=2,
            highlightbackground='#00FF66',
        )
        self.exhibition_tool.pack(side='top', fill='x', pady=(0, 2))

        tk.Label(
            self.exhibition_tool,
            text='🔬 TECHNOLOGY EXHIBITION',
            bg='#002244',
            fg='#00FFFF',
            font=('Segoe UI', 8, 'bold'),
            pady=2,
        ).pack(fill='x')

        self.exhibit_screen = tk.Canvas(
            self.exhibition_tool,
            bg='#000000',
            height=75,
            highlightthickness=1,
            highlightbackground='#00FF66',
        )
        self.exhibit_screen.pack(fill='x', padx=3, pady=2)

        self.ctrl_bar = tk.Frame(self.exhibition_tool, bg='#051026')
        self.ctrl_bar.pack(fill='x', padx=3, pady=(0, 2))

        tk.Button(
            self.ctrl_bar,
            text='⏮ PREV',
            bg='#0055FF',
            fg='white',
            font=('Segoe UI', 7, 'bold'),
            command=self.prev_exhibit,
        ).pack(side='left', padx=1)
        tk.Button(
            self.ctrl_bar,
            text='▶ OPEN FILE',
            bg='#00FF66',
            fg='black',
            font=('Segoe UI', 7, 'bold'),
            command=self.play_current_exhibit,
        ).pack(side='left', padx=1)
        tk.Button(
            self.ctrl_bar,
            text='NEXT ⏭',
            bg='#0055FF',
            fg='white',
            font=('Segoe UI', 7, 'bold'),
            command=self.next_exhibit,
        ).pack(side='left', padx=1)

        self.lbl_exhibit_status = tk.Label(
            self.ctrl_bar,
            text='',
            bg='#051026',
            fg='#FFFF00',
            font=('Consolas', 7, 'bold'),
        )
        self.lbl_exhibit_status.pack(side='right', padx=1)

        # B. Compact College Situation & Status Box
        self.situation_tool = tk.Frame(
            self.right_frame,
            bg='#051026',
            highlightthickness=2,
            highlightbackground='#FF9900',
        )
        self.situation_tool.pack(side='top', fill='x', pady=2)

        tk.Label(
            self.situation_tool,
            text='🏫 COLLEGE SITUATION & STATES',
            bg='#331100',
            fg='#FF9900',
            font=('Segoe UI', 8, 'bold'),
            pady=1,
        ).pack(fill='x')

        self.lbl_situation_content = tk.Label(
            self.situation_tool,
            bg='#0A1526',
            fg='#FFFFFF',
            font=('Nyala', 10, 'bold'),
            justify='left',
            anchor='nw',
            padx=4,
            pady=3,
            wraplength=240,
        )
        self.lbl_situation_content.pack(fill='x', padx=2, pady=1)

        # C. Visible Prepared Profile Component
        self.profile_tool = tk.Frame(
            self.right_frame,
            bg='#051026',
            highlightthickness=2,
            highlightbackground='#00FFFF',
        )
        self.profile_tool.pack(side='top', fill='x', pady=(2, 0))

        tk.Label(
            self.profile_tool,
            text='👤 PREPARED BY',
            bg='#002244',
            fg='#00FFFF',
            font=('Segoe UI', 8, 'bold'),
            pady=1,
        ).pack(fill='x')

        p_inner = tk.Frame(self.profile_tool, bg='#051026', padx=4, pady=3)
        p_inner.pack(fill='x')

        self.profile_canvas = tk.Canvas(
            p_inner,
            width=42,
            height=42,
            bg='#000000',
            highlightthickness=1,
            highlightbackground='#00FFFF',
        )
        self.profile_canvas.pack(side='left', padx=(0, 5))

        p_info = tk.Frame(p_inner, bg='#051026')
        p_info.pack(side='left', fill='both', expand=True)

        self.lbl_prof_name = tk.Label(
            p_info,
            bg='#051026',
            fg='#FFFF00',
            font=('Segoe UI', 8, 'bold'),
            anchor='w',
        )
        self.lbl_prof_name.pack(fill='x')

        self.lbl_prof_role = tk.Label(
            p_info,
            bg='#051026',
            fg='#00FF66',
            font=('Segoe UI', 7),
            anchor='w',
        )
        self.lbl_prof_role.pack(fill='x')

    def render_profile_photo(self):
        self.profile_canvas.delete('all')
        prof = d.get('prepared_profile', {})
        photo_path = prof.get('photo', '')
        if photo_path and Path(photo_path).exists():
            try:
                im = Image.open(photo_path).convert('RGBA')
                im.thumbnail((42, 42))
                self.profile_img_ph = ImageTk.PhotoImage(im)
                self.profile_canvas.create_image(
                    21, 21, image=self.profile_img_ph
                )
                return
            except Exception:
                pass
        self.profile_canvas.create_text(
            21,
            21,
            text='[PHOTO]',
            fill='#00FFFF',
            font=('Consolas', 7, 'bold'),
        )

    def animate_ticker(self):
        self.ticker_x -= 3
        bbox = self.ticker_canvas.bbox(self.ticker_text_item)
        if bbox and bbox[2] < 0:
            self.ticker_x = self.ticker_canvas.winfo_width() + 10

        self.ticker_canvas.coords(self.ticker_text_item, self.ticker_x, 13)

        self.ticker_blink_toggle = not self.ticker_blink_toggle
        red_color = '#FF0000' if self.ticker_blink_toggle else '#660000'
        self.ticker_canvas.itemconfig(self.ticker_text_item, fill=red_color)

        self.r.after(50, self.animate_ticker)

    def draw_exhibition_screen(self):
        self.exhibit_screen.delete('all')
        exhibits = d.get('exhibits', [])
        w = self.exhibit_screen.winfo_width() or 240
        h = self.exhibit_screen.winfo_height() or 75

        if not exhibits:
            self.exhibit_screen.create_text(
                w / 2,
                h / 2,
                text='No Exhibition Items.',
                fill='#FFFFFF',
                font=('Segoe UI', 8, 'bold'),
            )
            self.lbl_exhibit_status.config(text='0/0')
            return

        item = exhibits[self.current_exhibit_idx % len(exhibits)]

        self.exhibit_screen.create_rectangle(
            2, 2, w - 2, h - 2, outline='#00FF66', width=1, fill='#0A1526'
        )
        self.exhibit_screen.create_text(
            w / 2,
            14,
            text=f"EXHIBIT #{self.current_exhibit_idx+1}: {item['title']}",
            fill='#00FFFF',
            font=('Segoe UI', 8, 'bold'),
        )
        self.exhibit_screen.create_text(
            w / 2,
            28,
            text=f"TYPE: [{item['type']}]",
            fill='#FFFF00',
            font=('Consolas', 7, 'bold'),
        )

        f_p = Path(item.get('file', ''))
        if f_p.exists():
            self.exhibit_screen.create_text(
                w / 2,
                h - 15,
                text='[CLICK OPEN FILE]',
                fill='#00FF66',
                font=('Segoe UI', 8, 'bold'),
            )
        else:
            self.exhibit_screen.create_text(
                w / 2,
                h - 15,
                text='⚠️ READY / UNLINKED',
                fill='#FF9900',
                font=('Segoe UI', 8, 'bold'),
            )

        self.lbl_exhibit_status.config(
            text=f'{self.current_exhibit_idx+1}/{len(exhibits)}'
        )

    def prev_exhibit(self):
        if d.get('exhibits'):
            self.current_exhibit_idx = (self.current_exhibit_idx - 1) % len(
                d['exhibits']
            )
            self.draw_exhibition_screen()

    def next_exhibit(self):
        if d.get('exhibits'):
            self.current_exhibit_idx = (self.current_exhibit_idx + 1) % len(
                d['exhibits']
            )
            self.draw_exhibition_screen()

    def play_current_exhibit(self):
        exhibits = d.get('exhibits', [])
        if exhibits:
            item = exhibits[self.current_exhibit_idx % len(exhibits)]
            self.launch_file(item.get('file', ''))

    def refresh(self):
        self.setup_fonts()

        self.ce.config(text=d['college_en'], font=self.font_header_en)
        self.ca.config(text=d['college_am'], font=self.font_header_am)
        self.cs.config(
            text=d.get('college_sid', ''), font=self.font_body_en
        )
        self.mo.config(
            text=f'"{d["motto"]}"', font=self.font_body_en
        )
        self.banner_lbl.config(
            text=f"📢  {d['headline_en']}  |  {d['headline_am']}",
            font=self.font_body_am,
        )

        self.ticker_canvas.itemconfig(
            self.ticker_text_item,
            text=d.get('bottom_ticker_news', ''),
            font=self.font_ticker,
        )

        sit = d.get('college_situation', {})
        sit_text = (
            f"📍 {sit.get('status_am', '')}\n"
            f"ℹ️ {sit.get('status_en', '')}\n"
            f"👥 Trainees: {sit.get('trainees', '3,500+')}  |  👨‍🏫 Staff: {sit.get('staff', '145')}\n"
            f"🔬 Prototypes: {sit.get('projects', '12 Prototypes')}"
        )
        self.lbl_situation_content.config(
            text=sit_text, font=self.font_body_am
        )

        prof = d.get('prepared_profile', {})
        self.lbl_prof_name.config(
            text=prof.get('name', 'In. TEMESGEN SAMUA'), font=self.font_body_en
        )
        self.lbl_prof_role.config(
            text=prof.get('role', 'System Administrator')
        )
        self.render_profile_photo()

        self.address_bar.config(
            text=f"📞 {d.get('phone', '')} | 📮 {d.get('po_box', '')} | ✉️ {d.get('email', '')} | 📍 {d.get('address', '')}"
        )

        self.draw()
        self.draw_exhibition_screen()

    def draw(self):
        self.c.delete('all')
        if not d['notices']:
            return

        n = d['notices'][self.current_notice_idx % len(d['notices'])]

        w = max(self.c.winfo_width(), 400)
        card_w = w - 20
        x_offset = 10
        y = -self.offset + 10

        body_text = n.get('body', '')
        f_path = n.get('file_path', '')
        m_type = n.get('media_type', 'TEXT')

        docx_text = ''
        if f_path and Path(f_path).suffix.lower() in ['.docx', '.doc']:
            docx_text = read_docx_lines(f_path)

        full_text = body_text
        if docx_text:
            full_text += '\n\n📄 DOCUMENT CONTENT:\n' + docx_text

        raw_lines = full_text.split('\n')
        total_wrapped_lines = sum(
            max(1, len(line) // 50 + 1) for line in raw_lines
        )
        card_h = max(320, 80 + (total_wrapped_lines * 22))

        self.c.create_rectangle(
            x_offset,
            y,
            x_offset + card_w,
            y + card_h,
            outline='#00FFFF',
            width=2,
            fill='#FFFFFF',
        )
        self.c.create_rectangle(
            x_offset,
            y,
            x_offset + card_w,
            y + 50,
            outline='#051026',
            fill='#051026',
        )

        notice_num = (
            f"NOTICE ({self.current_notice_idx + 1}/{len(d['notices'])})"
        )
        self.c.create_text(
            x_offset + 10,
            y + 8,
            text=f"{n.get('title', '')} - {notice_num}",
            anchor='nw',
            font=self.font_body_en,
            fill='#00FFFF',
        )
        play_sec = n.get('display_time', '10')
        self.c.create_text(
            x_offset + 10,
            y + 28,
            text=f"DATE: {n.get('date', '')} | DURATION: {play_sec}s",
            anchor='nw',
            font=('Segoe UI', 9, 'bold'),
            fill='#FFFF00',
        )

        tag_text = f'[{m_type.upper()}]'
        self.c.create_text(
            x_offset + card_w - 10,
            y + 28,
            text=tag_text,
            anchor='ne',
            font=('Segoe UI', 8, 'italic'),
            fill='#00FF00',
        )

        self.c.create_text(
            x_offset + 15,
            y + 65,
            text=full_text,
            anchor='nw',
            width=card_w - 30,
            font=self.font_body_am,
            fill='#000000',
        )

        canvas_h = self.c.winfo_height()
        self.total = max(0, card_h - canvas_h + 20)

    def scroll(self):
        if not self.paused and d['notices']:
            n = d['notices'][self.current_notice_idx % len(d['notices'])]
            play_time = int(n.get('display_time', 10))

            if self.offset < self.total:
                self.offset += 1
            else:
                elapsed = time.time() - self.notice_timer_start
                if elapsed >= play_time:
                    self.offset = 0
                    self.current_notice_idx = (
                        self.current_notice_idx + 1
                    ) % len(d['notices'])
                    self.notice_timer_start = time.time()
            self.draw()
        self.r.after(50, self.scroll)


if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()