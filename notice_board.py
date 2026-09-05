import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import json, shutil

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
LOGOS.mkdir(exist_ok=True)

DEFAULT = {
    'college_en': 'YIRGALEM POLYTECHNIC COLLEGE',
    'college_am': 'ይርጋለም ፖሊ ቴክኒክ ኮሌጅ',
    'college_sid': 'IRGALAME POOLITEKNIKKE KOLLEEJ',
    'motto': 'SKILLS AND INNOVATION FOR BETTER GENERATION!',
    'headline_en': 'DIGITAL NOTICE BOARD',
    'headline_am': 'ዲጂታል ማስታወቂያ ሰሌዳ',
    'email': 'info@yptc.edu.et', 'po_box': 'P.O. Box: 000', 'phone': '+251 000 000 000',
    'address': 'Yirgalem, Sidama Region, Ethiopia',
    'left_logo': '', 'right_logo': '',
    'daily_event': {
        'title': 'College Innovation Day',
        'time': '09:00 AM - 05:00 PM',
        'location': 'Main Auditorium',
        'prepared_by_name': 'Eng. Alemu T.',
        'prepared_by_photo': ''
    },
    'notices': [
        {
            'title': 'Student Registration',
            'date': '26/12/2018 E.C',
            'display_time': '10',
            'body': 'Students are informed to complete registration according to the college schedule.',
            'media_type': 'Text',
            'file_path': ''
        },
        {
            'title': 'Innovation Exhibition',
            'date': 'Upcoming',
            'display_time': '15',
            'body': 'Technology, engineering and innovation projects will be presented at the college.',
            'media_type': 'Doc',
            'file_path': ''
        }
    ]
}

def load():
    try:
        d = json.loads(DATA.read_text(encoding='utf-8'))
        DEFAULT.update(d)
    except Exception:
        pass
    return DEFAULT

def save():
    DATA.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')

def read_docx_lines(file_path):
    """Reads .docx files line-by-line using python-docx."""
    if not file_path or not Path(file_path).exists():
        return ""
    if Path(file_path).suffix.lower() not in ['.docx', '.doc']:
        return ""
    if docx is None:
        return "[Error: python-docx not installed. Run 'pip install python-docx']"
    
    try:
        doc = docx.Document(file_path)
        lines = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        return "\n".join(lines)
    except Exception as e:
        return f"[Docx Read Error: {str(e)}]"

d = load()

class App:
    def __init__(self, r):
        self.r = r
        self.r.title('Yirgalem Polytechnic College - Advanced Notice Board')
        self.r.geometry('1366x768')
        self.r.configure(bg='#3C2218')

        self.photos = []
        self.offset = 0
        self.total = 1
        self.paused = False
        self.logo_angle = 0
        
        self.make_editor()
        self.make_preview()
        self.refresh()
        self.animate_logos()
        self.scroll()

    def make_editor(self):
        self.admin_outer = ttk.Frame(self.r)
        self.admin_outer.pack(side='left', fill='y')

        self.admin_canvas = tk.Canvas(self.admin_outer, width=320, borderwidth=0, highlightthickness=0)
        self.admin_scrollbar = ttk.Scrollbar(self.admin_outer, orient='vertical', command=self.admin_canvas.yview)
        self.left_frame = ttk.Frame(self.admin_canvas, padding=8)

        self.left_frame.bind(
            "<Configure>",
            lambda e: self.admin_canvas.configure(scrollregion=self.admin_canvas.bbox("all"))
        )

        self.admin_canvas.create_window((0, 0), window=self.left_frame, anchor="nw")
        self.admin_canvas.configure(yscrollcommand=self.admin_scrollbar.set)

        self.admin_canvas.pack(side="left", fill="both", expand=True)
        self.admin_scrollbar.pack(side="right", fill="y")
        
        ttk.Label(self.left_frame, text='ADMIN CONTROL PANEL', font=('Segoe UI', 12, 'bold')).pack(pady=5)
        
        self.btn_pause = tk.Button(self.left_frame, text='⏸ PAUSE DISPLAY (EDIT MODE)', bg='#D4AF37', fg='black', font=('Segoe UI', 9, 'bold'), command=self.toggle_pause)
        self.btn_pause.pack(fill='x', pady=4)

        self.v = {}
        for k, label in [
            ('college_en', 'College Name (EN)'), ('college_am', 'College Name (AM)'),
            ('college_sid', 'College Name (SID)'), ('motto', 'Motto'),
            ('headline_en', 'Headline (EN)'), ('headline_am', 'Headline (AM)')
        ]:
            ttk.Label(self.left_frame, text=label).pack(anchor='w')
            self.v[k] = tk.StringVar(value=d.get(k, ''))
            ttk.Entry(self.left_frame, textvariable=self.v[k], width=28).pack(fill='x', pady=(0, 2))

        ttk.Button(self.left_frame, text='Upload LEFT LOGO', command=lambda: self.logo('left_logo')).pack(fill='x', pady=2)
        ttk.Button(self.left_frame, text='Upload RIGHT LOGO', command=lambda: self.logo('right_logo')).pack(fill='x', pady=2)

        ttk.Separator(self.left_frame).pack(fill='x', pady=5)
        ttk.Label(self.left_frame, text='DAILY EVENT (RED PANEL)', font=('Segoe UI', 10, 'bold')).pack(anchor='w')
        
        self.dev = {}
        for k, label in [('title', 'Event Title'), ('time', 'Time'), ('location', 'Location'), ('prepared_by_name', 'Prepared By (Name)')]:
            ttk.Label(self.left_frame, text=label).pack(anchor='w')
            self.dev[k] = tk.StringVar(value=d['daily_event'].get(k, ''))
            ttk.Entry(self.left_frame, textvariable=self.dev[k], width=28).pack(fill='x', pady=(0, 2))
        
        ttk.Button(self.left_frame, text='Upload Presenter Photo', command=self.upload_presenter_photo).pack(fill='x', pady=2)

        ttk.Separator(self.left_frame).pack(fill='x', pady=5)
        ttk.Label(self.left_frame, text='NOTICES / MEDIA', font=('Segoe UI', 10, 'bold')).pack(anchor='w')
        
        self.tree = ttk.Treeview(self.left_frame, columns=('date', 'title', 'type'), show='headings', height=5)
        self.tree.heading('date', text='Date')
        self.tree.heading('title', text='Title')
        self.tree.heading('type', text='Type')
        self.tree.column('date', width=50)
        self.tree.column('title', width=110)
        self.tree.column('type', width=50)
        self.tree.pack(fill='x')

        for b, cmd in [('ADD NOTICE', self.add), ('EDIT', self.edit), ('DELETE', self.delete)]:
            ttk.Button(self.left_frame, text=b, command=cmd).pack(fill='x', pady=1)

        ttk.Separator(self.left_frame).pack(fill='x', pady=5)
        ttk.Button(self.left_frame, text='SAVE ALL CHANGES', command=self.save_all).pack(fill='x', pady=2)
        ttk.Button(self.left_frame, text='FULLSCREEN (ESC Exit)', command=self.full).pack(fill='x', pady=2)

    def make_preview(self):
        self.p = tk.Frame(self.r, bg='#3C2218')
        self.p.pack(side='right', fill='both', expand=True, padx=5, pady=5)

        self.h = tk.Frame(self.p, bg='#D4AF37', height=130)
        self.h.pack(fill='x')
        self.h.pack_propagate(False)

        self.l = tk.Label(self.h, bg='#D4AF37')
        self.l.pack(side='left', padx=15)

        self.rr = tk.Label(self.h, bg='#D4AF37')
        self.rr.pack(side='right', padx=15)

        c = tk.Frame(self.h, bg='#D4AF37')
        c.pack(expand=True, fill='both')

        self.ce = tk.Label(c, bg='#D4AF37', fg='#3C2218', font=('Segoe UI', 18, 'bold'))
        self.ce.pack(pady=(2, 0))
        self.ca = tk.Label(c, bg='#D4AF37', fg='#3C2218', font=('Noto Sans Ethiopic', 14, 'bold'))
        self.ca.pack()
        self.cs = tk.Label(c, bg='#D4AF37', fg='#3C2218', font=('Segoe UI', 10, 'bold'))
        self.cs.pack()
        self.mo = tk.Label(c, bg='#3C2218', fg='#D4AF37', font=('Segoe UI', 9, 'italic'), pady=2)
        self.mo.pack(fill='x', padx=10, pady=2)

        self.body_frame = tk.Frame(self.p, bg='#3C2218')
        self.body_frame.pack(fill='both', expand=True, pady=5)

        self.notice_frame = tk.Frame(self.body_frame, bg='#3C2218')
        self.notice_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))

        self.c = tk.Canvas(self.notice_frame, bg='#4A2E2B', highlightthickness=1, highlightbackground='#D4AF37')
        self.c_scrollbar = ttk.Scrollbar(self.notice_frame, orient='vertical', command=self.c.yview)
        
        self.c.configure(yscrollcommand=self.c_scrollbar.set)
        self.c.pack(side='left', fill='both', expand=True)
        self.c_scrollbar.pack(side='right', fill='y')

        self.c.bind("<MouseWheel>", lambda e: self.c.yview_scroll(int(-1*(e.delta/120)), "units"))

        self.side_panel = tk.Frame(self.body_frame, bg='#8B0000', width=280, highlightthickness=2, highlightbackground='#D4AF37')
        self.side_panel.pack(side='right', fill='y')
        self.side_panel.pack_propagate(False)

        tk.Label(self.side_panel, text='📌 DAILY EVENT', bg='#8B0000', fg='white', font=('Segoe UI', 14, 'bold')).pack(pady=10)
        self.de_title = tk.Label(self.side_panel, bg='#8B0000', fg='#FFD700', font=('Segoe UI', 11, 'bold'), wraplength=260)
        self.de_title.pack(pady=5)
        self.de_time = tk.Label(self.side_panel, bg='#8B0000', fg='white', font=('Segoe UI', 9))
        self.de_time.pack()
        self.de_loc = tk.Label(self.side_panel, bg='#8B0000', fg='white', font=('Segoe UI', 9, 'italic'))
        self.de_loc.pack(pady=2)

        self.de_img_lbl = tk.Label(self.side_panel, bg='#8B0000')
        self.de_img_lbl.pack(pady=10)

        self.de_prep = tk.Label(self.side_panel, bg='#8B0000', fg='white', font=('Segoe UI', 9))
        self.de_prep.pack(side='bottom', pady=10)

        self.f = tk.Label(self.p, bg='#D4AF37', fg='#3C2218', font=('Segoe UI', 9, 'bold'), pady=4)
        self.f.pack(fill='x')

    def toggle_pause(self):
        self.paused = not self.paused
        self.btn_pause.config(text='▶ RESUME DISPLAY' if self.paused else '⏸ PAUSE DISPLAY (EDIT MODE)',
                              bg='#FF4500' if self.paused else '#D4AF37')

    def animate_logos(self):
        self.logo_angle = (self.logo_angle + 10) % 360
        self.render_logos(self.logo_angle)
        self.r.after(150, self.animate_logos)

    def render_logos(self, angle):
        for lab, key in [(self.l, 'left_logo'), (self.rr, 'right_logo')]:
            try:
                if d[key] and Path(d[key]).exists():
                    im = Image.open(d[key]).convert('RGBA')
                    im = im.rotate(angle)
                    im.thumbnail((70, 70))
                    ph = ImageTk.PhotoImage(im)
                    lab.config(image=ph, text='')
                    lab.image = ph
                else:
                    lab.config(image='', text='[LOGO]', fg='#3C2218', font=('Segoe UI', 10, 'bold'))
            except Exception:
                lab.config(image='', text='[LOGO]', fg='#3C2218', font=('Segoe UI', 10, 'bold'))

    def upload_presenter_photo(self):
        p = filedialog.askopenfilename(filetypes=[('Images', '*.png *.jpg *.jpeg *.webp')])
        if p:
            dest = LOGOS / ('presenter' + Path(p).suffix.lower())
            shutil.copy2(p, dest)
            d['daily_event']['prepared_by_photo'] = str(dest)
            save()
            self.refresh()

    def logo(self, key):
        p = filedialog.askopenfilename(filetypes=[('Images', '*.png *.jpg *.jpeg *.webp')])
        if p:
            dest = LOGOS / (key + Path(p).suffix.lower())
            shutil.copy2(p, dest)
            d[key] = str(dest)
            save()
            self.refresh()

    def refresh(self):
        for k, x in self.v.items():
            d[k] = x.get()
        for k, x in self.dev.items():
            d['daily_event'][k] = x.get()

        self.tree.delete(*self.tree.get_children())
        for i, n in enumerate(d['notices']):
            self.tree.insert('', 'end', iid=str(i), values=(n.get('date', ''), n.get('title', ''), n.get('media_type', 'Text')))

        self.ce.config(text=d['college_en'])
        self.ca.config(text=d['college_am'])
        self.cs.config(text=d['college_sid'])
        self.mo.config(text=f'"{d["motto"]}"')
        self.f.config(text=f"{d['address']}  |  {d['email']}  |  {d['po_box']}  |  {d['phone']}")

        de = d['daily_event']
        self.de_title.config(text=de.get('title', ''))
        self.de_time.config(text=f"🕒 {de.get('time', '')}")
        self.de_loc.config(text=f"📍 {de.get('location', '')}")
        self.de_prep.config(text=f"Prepared By:\n{de.get('prepared_by_name', '')}")

        if de.get('prepared_by_photo') and Path(de['prepared_by_photo']).exists():
            try:
                im = Image.open(de['prepared_by_photo']).convert('RGBA')
                im.thumbnail((120, 120))
                ph = ImageTk.PhotoImage(im)
                self.de_img_lbl.config(image=ph)
                self.de_img_lbl.image = ph
            except Exception:
                self.de_img_lbl.config(image='')

        self.draw()

    def draw(self):
        self.c.delete('all')
        y = -self.offset + 10
        w = max(self.c.winfo_width(), 600)
        card_w = w - 30

        for n in d['notices']:
            # 1. Combine base text and word document content
            body_text = n.get('body', '')
            f_path = n.get('file_path', '')
            m_type = n.get('media_type', 'Text')

            docx_text = ""
            if f_path and Path(f_path).suffix.lower() in ['.docx', '.doc']:
                docx_text = read_docx_lines(f_path)

            full_text = body_text
            if docx_text:
                full_text += "\n\n📄 DOCUMENT CONTENT:\n" + docx_text

            # 2. Dynamic card height calculation per notice box
            raw_lines = full_text.split('\n')
            total_wrapped_lines = sum(max(1, len(line) // 65 + 1) for line in raw_lines)
            
            header_height = 65
            body_height = total_wrapped_lines * 22
            padding = 20
            
            card_h = max(110, header_height + body_height + padding)

            # 3. Draw notice card if visible within canvas viewport
            if y + card_h > 0 and y < self.c.winfo_height() + card_h:
                # Dynamic outer box
                self.c.create_rectangle(
                    15, y, 15 + card_w, y + card_h, 
                    outline='#D4AF37', width=2, fill='#FFF8DC'
                )
                
                # Header elements
                self.c.create_text(30, y + 15, text=n.get('title', ''), anchor='nw', font=('Segoe UI', 14, 'bold'), fill='#3C2218')
                self.c.create_text(w - 30, y + 15, text=f"⏱ {n.get('display_time', '10')}s | {n.get('date', '')}", anchor='ne', font=('Segoe UI', 9, 'bold'), fill='#8B0000')
                
                # Media Tag
                tag_text = f"[{m_type.upper()}] {Path(f_path).name if f_path else ''}"
                self.c.create_text(30, y + 42, text=tag_text, anchor='nw', font=('Segoe UI', 9, 'italic'), fill='#006699')
                
                # Dynamic body content
                self.c.create_text(
                    30, y + 65, 
                    text=full_text, 
                    anchor='nw', 
                    width=card_w - 30, 
                    font=('Segoe UI', 11), 
                    fill='#111111'
                )

            y += card_h + 15

        self.total = max(y + self.offset, 1)
        self.c.configure(scrollregion=(0, 0, w, self.total))

    def scroll(self):
        if not self.paused and self.c.winfo_height() > 100:
            self.offset += 1
            if self.offset >= self.total:
                self.offset = 0
            self.draw()
        self.r.after(50, self.scroll)

    def dialog(self, index=None):
        win = tk.Toplevel(self.r)
        win.title('Edit Notice' if index is not None else 'Add Notice')
        win.geometry('550x480')
        win.grab_set()

        old = d['notices'][index] if index is not None else {'title': '', 'date': '', 'display_time': '10', 'body': '', 'media_type': 'Text', 'file_path': ''}

        ttk.Label(win, text='Headline / Title').pack(anchor='w', padx=15, pady=(10, 2))
        tv = tk.StringVar(value=old.get('title', ''))
        ttk.Entry(win, textvariable=tv).pack(fill='x', padx=15)

        ttk.Label(win, text='Date / Status').pack(anchor='w', padx=15, pady=(5, 2))
        dv = tk.StringVar(value=old.get('date', ''))
        ttk.Entry(win, textvariable=dv).pack(fill='x', padx=15)

        ttk.Label(win, text='Display Duration (Seconds)').pack(anchor='w', padx=15, pady=(5, 2))
        dtv = tk.StringVar(value=old.get('display_time', '10'))
        ttk.Entry(win, textvariable=dtv).pack(fill='x', padx=15)

        ttk.Label(win, text='Media Attachment Type (Image / Video / PDF / Doc)').pack(anchor='w', padx=15, pady=(5, 2))
        mtv = tk.StringVar(value=old.get('media_type', 'Text'))
        m_combo = ttk.Combobox(win, textvariable=mtv, values=['Text', 'Image', 'Video', 'PDF', 'Doc'], state='readonly')
        m_combo.pack(fill='x', padx=15)

        fpv = tk.StringVar(value=old.get('file_path', ''))
        
        def browse_file():
            f = filedialog.askopenfilename(filetypes=[('Supported Files', '*.png *.jpg *.mp4 *.pdf *.doc *.docx')])
            if f:
                fpv.set(f)

        f_frame = ttk.Frame(win)
        f_frame.pack(fill='x', padx=15, pady=5)
        ttk.Entry(f_frame, textvariable=fpv).pack(side='left', fill='x', expand=True)
        ttk.Button(f_frame, text='Browse...', command=browse_file).pack(side='right', padx=(5, 0))

        ttk.Label(win, text='Details / Body Text').pack(anchor='w', padx=15, pady=(5, 2))
        tx = tk.Text(win, height=6)
        tx.pack(fill='both', expand=True, padx=15)
        tx.insert('1.0', old.get('body', ''))

        def ok():
            item = {
                'title': tv.get().strip(),
                'date': dv.get().strip(),
                'display_time': dtv.get().strip(),
                'media_type': mtv.get(),
                'file_path': fpv.get(),
                'body': tx.get('1.0', 'end').strip()
            }
            if not item['title']:
                return messagebox.showwarning('Required', 'Enter a headline.')
            if index is None:
                d['notices'].append(item)
            else:
                d['notices'][index] = item
            save()
            self.refresh()
            win.destroy()

        b_frame = ttk.Frame(win)
        b_frame.pack(fill='x', padx=15, pady=10)
        ttk.Button(b_frame, text='SAVE', command=ok).pack(side='left', expand=True, fill='x', padx=5)
        ttk.Button(b_frame, text='CANCEL', command=win.destroy).pack(side='right', expand=True, fill='x', padx=5)

    def add(self):
        self.dialog()

    def edit(self):
        s = self.tree.selection()
        if s:
            self.dialog(int(s[0]))
        else:
            messagebox.showwarning('Notice', 'Select a notice first.')

    def delete(self):
        s = self.tree.selection()
        if s and messagebox.askyesno('Delete', 'Delete selected notice?'):
            del d['notices'][int(s[0])]
            save()
            self.refresh()

    def save_all(self):
        for k, x in self.v.items():
            d[k] = x.get().strip()
        for k, x in self.dev.items():
            d['daily_event'][k] = x.get().strip()
        save()
        self.refresh()
        messagebox.showinfo('Saved', 'All settings saved successfully.')

    def full(self):
        self.r.attributes('-fullscreen', True)
        self.r.bind('<Escape>', lambda e: self.r.attributes('-fullscreen', False))

if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()