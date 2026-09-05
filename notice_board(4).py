import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import json, shutil
try:
    from PIL import Image, ImageTk
except ImportError:
    raise SystemExit('Install Pillow first: python -m pip install pillow')

BASE=Path(__file__).resolve().parent
DATA=BASE/'noticeboard_data.json'; LOGOS=BASE/'logos'; LOGOS.mkdir(exist_ok=True)
DEFAULT={
 'college_en':'YIRGALEM POLYTECHNIC COLLEGE','college_am':'ይርጋለም ፖሊ ቴክኒክ ኮሌጅ',
 'headline_en':'DIGITAL NOTICE BOARD','headline_am':'ዲጂታል ማስታወቂያ',
 'motto':'SKILLS AND INNOVATION FOR BETTER GENERATION!',
 'email':'info@yptc.edu.et','po_box':'P.O. Box: 000','phone':'+251 000 000 000',
 'address':'Yirgalem, Sidama Region, Ethiopia','left_logo':'','right_logo':'',
 'notices':[
  {'title':'Student Registration','date':'26/12/2018 E.C','body':'Students are informed to complete registration according to the college schedule.'},
  {'title':'Innovation Exhibition','date':'Upcoming','body':'Technology, engineering and innovation projects will be presented at the college.'},
  {'title':'Important Announcement','date':'Notice','body':'Please check the digital notice board regularly for new college information.'}
 ]}

def load():
    try:
        d=json.loads(DATA.read_text(encoding='utf-8')); DEFAULT.update(d)
    except Exception: pass
    return DEFAULT

def save(): DATA.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
d=load()

class App:
 def __init__(self,r):
  self.r=r; r.title('Yirgalem Polytechnic College - Digital Notice Board'); r.geometry('1280x800'); r.configure(bg='white')
  self.photos=[]; self.offset=0; self.total=1
  self.make_editor(); self.make_preview(); self.refresh(); self.scroll()
 def make_editor(self):
  left=ttk.Frame(self.r,padding=8); left.pack(side='left',fill='y')
  ttk.Label(left,text='NOTICE BOARD SETTINGS',font=('Segoe UI',14,'bold')).pack(pady=5)
  self.v={}
  for k,label in [('college_en','College name English'),('college_am','College name Amharic'),('headline_en','Headline English'),('headline_am','Headline Amharic'),('motto','Top motto'),('email','Email'),('po_box','P.O. Box'),('phone','Phone'),('address','Address')]:
   ttk.Label(left,text=label).pack(anchor='w'); self.v[k]=tk.StringVar(value=d[k]); ttk.Entry(left,textvariable=self.v[k],width=36).pack(fill='x',pady=(0,5))
  ttk.Button(left,text='Upload LEFT LOGO',command=lambda:self.logo('left_logo')).pack(fill='x',pady=3)
  ttk.Button(left,text='Upload RIGHT LOGO',command=lambda:self.logo('right_logo')).pack(fill='x',pady=3)
  ttk.Separator(left).pack(fill='x',pady=8)
  ttk.Label(left,text='NOTICES / EVENTS',font=('Segoe UI',12,'bold')).pack(anchor='w')
  self.tree=ttk.Treeview(left,columns=('date','title'),show='headings',height=8); self.tree.heading('date',text='Date'); self.tree.heading('title',text='Headline'); self.tree.column('date',width=105); self.tree.column('title',width=205); self.tree.pack(fill='x')
  for b,cmd in [('ADD',self.add),('EDIT',self.edit),('DELETE',self.delete)]: ttk.Button(left,text=b,command=cmd).pack(fill='x',pady=2)
  ttk.Separator(left).pack(fill='x',pady=8)
  ttk.Button(left,text='SAVE ALL',command=self.save_all).pack(fill='x',pady=3)
  ttk.Button(left,text='FULL SCREEN',command=self.full).pack(fill='x',pady=3)
 def make_preview(self):
  self.p=tk.Frame(self.r,bg='white'); self.p.pack(side='right',fill='both',expand=True,padx=8,pady=8)
  self.h=tk.Frame(self.p,bg='#17365d',height=145); self.h.pack(fill='x'); self.h.pack_propagate(False)
  self.l=tk.Label(self.h,bg='#17365d'); self.l.pack(side='left',padx=15)
  self.rr=tk.Label(self.h,bg='#17365d'); self.rr.pack(side='right',padx=15)
  c=tk.Frame(self.h,bg='#17365d'); c.pack(expand=True,fill='both')
  self.ce=tk.Label(c,bg='#17365d',fg='white',font=('Segoe UI',22,'bold')); self.ce.pack(pady=(8,0))
  self.ca=tk.Label(c,bg='#17365d',fg='white',font=('Noto Sans Ethiopic',17,'bold')); self.ca.pack()
  self.mo=tk.Label(c,bg='#8aaa1b',fg='white',font=('Segoe UI',11,'bold'),pady=4); self.mo.pack(fill='x',padx=15,pady=5)
  hf=tk.Frame(self.p,bg='#edf2f5'); hf.pack(fill='x',padx=10,pady=8)
  self.he=tk.Label(hf,bg='#edf2f5',fg='#17365d',font=('Segoe UI',22,'bold')); self.he.pack()
  self.ha=tk.Label(hf,bg='#edf2f5',fg='#8aaa1b',font=('Noto Sans Ethiopic',17,'bold')); self.ha.pack(pady=(0,7))
  self.c=tk.Canvas(self.p,bg='white',highlightthickness=0); self.c.pack(fill='both',expand=True,padx=12)
  self.f=tk.Label(self.p,bg='#17365d',fg='white',font=('Segoe UI',10,'bold'),pady=7); self.f.pack(fill='x')
 def logo(self,key):
  p=filedialog.askopenfilename(filetypes=[('Images','*.png *.jpg *.jpeg *.gif *.bmp *.webp')])
  if p:
   dest=LOGOS/(key+Path(p).suffix.lower()); shutil.copy2(p,dest); d[key]=str(dest); save(); self.refresh()
 def refresh(self):
  for k,x in self.v.items(): d[k]=x.get()
  self.tree.delete(*self.tree.get_children())
  for i,n in enumerate(d['notices']): self.tree.insert('', 'end',iid=str(i),values=(n.get('date',''),n.get('title','')))
  self.ce.config(text=d['college_en']); self.ca.config(text=d['college_am']); self.mo.config(text=d['motto']); self.he.config(text=d['headline_en']); self.ha.config(text=d['headline_am']); self.f.config(text=f"{d['address']}  |  {d['email']}  |  {d['po_box']}  |  {d['phone']}")
  self.photos=[]
  for lab,key in [(self.l,'left_logo'),(self.rr,'right_logo')]:
   try:
    im=Image.open(d[key]).convert('RGBA'); im.thumbnail((100,100)); ph=ImageTk.PhotoImage(im); self.photos.append(ph); lab.config(image=ph,text='')
   except Exception: lab.config(image='',text='LOGO',fg='white',font=('Segoe UI',16,'bold'))
  self.draw()
 def draw(self):
  self.c.delete('all'); y=-self.offset; w=max(self.c.winfo_width(),700)
  for n in d['notices']:
   h=145
   if y+h>0 and y<self.c.winfo_height():
    self.c.create_rectangle(20,y,w-20,y+h,outline='#8aaa1b',width=2,fill='#f6f9fb')
    self.c.create_text(40,y+18,text=n.get('title',''),anchor='nw',font=('Segoe UI',17,'bold'),fill='#17365d')
    self.c.create_text(w-40,y+20,text=n.get('date',''),anchor='ne',font=('Segoe UI',10,'bold'),fill='#777')
    self.c.create_text(40,y+58,text=n.get('body',''),anchor='nw',width=w-90,font=('Segoe UI',12),fill='#222')
   y+=165
  self.total=max(y,1)
 def scroll(self):
  if self.c.winfo_height()>100:
   self.offset+=1
   if self.offset>=self.total:self.offset=0
   self.draw()
  self.r.after(45,self.scroll)
 def dialog(self,index=None):
  win=tk.Toplevel(self.r); win.title('Edit Notice' if index is not None else 'Add Notice'); win.geometry('520x400'); win.grab_set()
  old=d['notices'][index] if index is not None else {'title':'','date':'','body':''}
  ttk.Label(win,text='Headline').pack(anchor='w',padx=15,pady=(15,2)); tv=tk.StringVar(value=old.get('title','')); ttk.Entry(win,textvariable=tv).pack(fill='x',padx=15)
  ttk.Label(win,text='Date / Status').pack(anchor='w',padx=15,pady=(10,2)); dv=tk.StringVar(value=old.get('date','')); ttk.Entry(win,textvariable=dv).pack(fill='x',padx=15)
  ttk.Label(win,text='Details').pack(anchor='w',padx=15,pady=(10,2)); tx=tk.Text(win,height=10); tx.pack(fill='both',expand=True,padx=15); tx.insert('1.0',old.get('body',''))
  def ok():
   item={'title':tv.get().strip(),'date':dv.get().strip(),'body':tx.get('1.0','end').strip()}
   if not item['title']: return messagebox.showwarning('Required','Enter a headline.')
   if index is None:d['notices'].append(item)
   else:d['notices'][index]=item
   save(); self.refresh(); win.destroy()
  ttk.Button(win,text='SAVE',command=ok).pack(side='left',expand=True,fill='x',padx=15,pady=10); ttk.Button(win,text='CANCEL',command=win.destroy).pack(side='right',expand=True,fill='x',padx=15,pady=10)
 def add(self): self.dialog()
 def edit(self):
  s=self.tree.selection()
  if s:self.dialog(int(s[0]))
  else:messagebox.showwarning('Notice','Select a notice first.')
 def delete(self):
  s=self.tree.selection()
  if s and messagebox.askyesno('Delete','Delete selected notice?'): del d['notices'][int(s[0])]; save(); self.refresh()
 def save_all(self):
  for k,x in self.v.items():d[k]=x.get().strip()
  save(); self.refresh(); messagebox.showinfo('Saved','All changes saved.')
 def full(self):
  self.r.attributes('-fullscreen',True); self.r.bind('<Escape>',lambda e:self.r.attributes('-fullscreen',False))

root=tk.Tk(); App(root); root.mainloop()
