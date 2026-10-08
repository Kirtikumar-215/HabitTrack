import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date, timedelta
from .habit_manager import VALID_CATEGORIES, VALID_FREQUENCIES, VALID_PRIORITIES
from .reports import weekly_trend, habit_comparison, status_distribution, heatmap

BG="#0f172a"; CARD="#172033"; FG="#f8fafc"; MUTED="#94a3b8"; ACCENT="#38bdf8"; GOOD="#34d399"; WARN="#fbbf24"

class HabitTrackApp(tk.Tk):
    def __init__(self, manager, analytics, storage):
        super().__init__()
        self.manager,self.analytics,self.storage=manager,analytics,storage
        self.title("HabitTrack — Consistency Analyzer"); self.geometry("1180x760"); self.minsize(1000,650)
        self.configure(bg=BG); self.style=ttk.Style(self); self.style.theme_use("clam"); self.theme_dark=True
        self.style.configure("TNotebook", background=BG, borderwidth=0); self.style.configure("TNotebook.Tab", padding=(18,10))
        self.build()

    def build(self):
        top=tk.Frame(self,bg=BG); top.pack(fill="x",padx=22,pady=18)
        tk.Label(top,text="HabitTrack",font=("Segoe UI",25,"bold"),bg=BG,fg=FG).pack(side="left")
        tk.Label(top,text="  Habit Consistency & Productivity Analyzer",font=("Segoe UI",11),bg=BG,fg=MUTED).pack(side="left",pady=8)
        ttk.Button(top,text="☀ Theme",command=self.toggle_theme).pack(side="right")
        self.nb=ttk.Notebook(self); self.nb.pack(fill="both",expand=True,padx=18,pady=(0,18))
        self.dashboard=self.tab("Dashboard"); self.habits_tab=self.tab("My Habits"); self.track_tab=self.tab("Track Day"); self.analytics_tab=self.tab("Analytics"); self.reports_tab=self.tab("Reports")
        self.build_dashboard(); self.build_habits(); self.build_track(); self.build_analytics(); self.build_reports()
        self.refresh_all()

    def tab(self,title):
        f=tk.Frame(self.nb,bg=BG); self.nb.add(f,text=title); return f

    def card(self,parent):
        return tk.Frame(parent,bg=CARD,bd=0,highlightthickness=0)

    def build_dashboard(self):
        for w in self.dashboard.winfo_children(): w.destroy()
        title=tk.Label(self.dashboard,text="Today's Overview",font=("Segoe UI",20,"bold"),bg=BG,fg=FG); title.pack(anchor="w",pady=(10,16))
        actions=tk.Frame(self.dashboard,bg=BG); actions.pack(fill="x",pady=(0,10))
        ttk.Button(actions,text="Load Demo Data",command=self.load_demo_data).pack(side="left")
        self.kpi=tk.Frame(self.dashboard,bg=BG); self.kpi.pack(fill="x")
        body=tk.Frame(self.dashboard,bg=BG); body.pack(fill="both",expand=True,pady=18)
        self.ins=tk.Text(body,height=10,bg=CARD,fg=FG,relief="flat",font=("Segoe UI",11),padx=18,pady=14); self.ins.pack(side="left",fill="both",expand=True)
        self.activity=tk.Text(body,width=38,bg=CARD,fg=FG,relief="flat",font=("Segoe UI",10),padx=14,pady=14); self.activity.pack(side="right",fill="y",padx=(12,0))
        self.badges=tk.Label(self.dashboard,bg=BG,fg=FG,font=("Segoe UI",11,"bold"),anchor="w"); self.badges.pack(fill="x")

    def build_habits(self):
        controls=tk.Frame(self.habits_tab,bg=BG); controls.pack(fill="x",pady=10)
        ttk.Button(controls,text="+ Add Habit",command=lambda:self.habit_dialog()).pack(side="left")
        self.search=tk.StringVar(); ttk.Entry(controls,textvariable=self.search,width=28).pack(side="left",padx=10); ttk.Button(controls,text="Search",command=self.refresh_habits).pack(side="left")
        self.cat=tk.StringVar(value="All"); ttk.Combobox(controls,textvariable=self.cat,values=["All"]+VALID_CATEGORIES,state="readonly",width=15).pack(side="left",padx=8); self.cat.trace_add("write",lambda *_:self.refresh_habits())
        cols=("name","category","frequency","priority","target","rate","streak","active")
        self.tree=ttk.Treeview(self.habits_tab,columns=cols,show="headings",height=20)
        heads={"name":"Habit","category":"Category","frequency":"Frequency","priority":"Priority","target":"Target","rate":"Completion","streak":"Current Streak","active":"Status"}
        for c in cols: self.tree.heading(c,text=heads[c]); self.tree.column(c,width=115)
        self.tree.pack(fill="both",expand=True,pady=8); self.tree.bind("<Double-1>",lambda e:self.edit_selected())
        btn=tk.Frame(self.habits_tab,bg=BG); btn.pack(fill="x")
        for text,cmd in [("Edit",self.edit_selected),("Activate/Deactivate",self.toggle_selected),("Delete",self.delete_selected)]: ttk.Button(btn,text=text,command=cmd).pack(side="left",padx=(0,8))

    def build_track(self):
        top=tk.Frame(self.track_tab,bg=BG); top.pack(fill="x",pady=12)
        tk.Label(top,text="Date (YYYY-MM-DD)",bg=BG,fg=FG).pack(side="left"); self.day=tk.StringVar(value=str(date.today())); ttk.Entry(top,textvariable=self.day,width=14).pack(side="left",padx=8); ttk.Button(top,text="Load",command=self.refresh_track).pack(side="left")
        self.track_tree=ttk.Treeview(self.track_tab,columns=("habit","category","status"),show="headings",height=22)
        for c,t in [("habit","Habit"),("category","Category"),("status","Status")]: self.track_tree.heading(c,text=t); self.track_tree.column(c,width=250)
        self.track_tree.pack(fill="both",expand=True); self.track_tree.bind("<Double-1>",self.cycle_status)
        tk.Label(self.track_tab,text="Double-click a habit to cycle: Pending → Completed → Missed → Pending",bg=BG,fg=MUTED).pack(anchor="w",pady=8)

    def build_analytics(self):
        self.analytics_text=tk.Text(self.analytics_tab,bg=CARD,fg=FG,relief="flat",font=("Consolas",11),padx=20,pady=20); self.analytics_text.pack(fill="both",expand=True,padx=10,pady=10)

    def build_reports(self):
        frame=tk.Frame(self.reports_tab,bg=BG); frame.pack(fill="x",pady=30)
        reports=[("📈 14-Day Trend",weekly_trend),("📊 Habit Comparison",habit_comparison),("🥧 Status Distribution",status_distribution),("🗓 35-Day Heatmap",heatmap)]
        for label,fn in reports: ttk.Button(frame,text=label,command=lambda f=fn:f(self.storage,self)).pack(fill="x",pady=8,ipady=8)
        ttk.Button(self.reports_tab,text="Export Records CSV",command=self.export_records).pack(pady=20)

    def refresh_all(self):
        self.refresh_dashboard(); self.refresh_habits(); self.refresh_track(); self.refresh_analytics()

    def refresh_dashboard(self):
        for w in self.kpi.winfo_children(): w.destroy()
        habits=self.storage.read_habits(); rates=self.analytics.habit_rates(); score=self.analytics.score()
        completed,total=self.analytics.daily_progress()
        cards=[("ACTIVE HABITS",sum(h["active"]=="1" for h in habits)),("TODAY DONE",f"{completed}/{total}"),
               ("CONSISTENCY",f"{score:.1f}%"),("ACHIEVEMENTS",len(self.analytics.achievements()))]
        for name,val in cards:
            c=self.card(self.kpi); c.pack(side="left",fill="x",expand=True,padx=5,ipady=12)
            tk.Label(c,text=name,bg=CARD,fg=MUTED,font=("Segoe UI",9,"bold")).pack()
            tk.Label(c,text=str(val),bg=CARD,fg=ACCENT,font=("Segoe UI",22,"bold")).pack()
        self.ins.delete("1.0","end")
        self.ins.insert("end","SMART INSIGHTS\n\n" + "\n".join("• "+x for x in self.analytics.insights()))
        self.activity.delete("1.0","end")
        self.activity.insert("end", "RECENT ACTIVITY\n\n")
        for day, name, status in self.analytics.recent_activity():
            marker = "✓" if status == "Completed" else "×"
            self.activity.insert("end", f"{marker} {day}  {name}\n")
        self.badges.config(text="   ".join(self.analytics.achievements()))

    def load_demo_data(self):
        if not messagebox.askyesno("Demo data", "Add realistic demo habits and 28 days of activity?"):
            return
        habits, records = self.storage.seed_demo_data()
        self.refresh_all()
        messagebox.showinfo("Demo data", f"Added {habits} demo habits and up to {records} activity records.")

    def refresh_habits(self):
        for x in self.tree.get_children(): self.tree.delete(x)
        q=self.search.get().lower(); cat=self.cat.get()
        for h in self.storage.read_habits():
            if q and q not in h["name"].lower(): continue
            if cat!="All" and h["category"]!=cat: continue
            cur,best=self.analytics.streaks(h["id"]); rate=self.analytics.completion_rate(h["id"])
            self.tree.insert("", "end", iid=h["id"], values=(h["name"],h["category"],h["frequency"],h["priority"],h["target"],f"{rate:.0f}%",cur,"Active" if h["active"]=="1" else "Paused"))

    def selected(self):
        s=self.tree.selection(); return s[0] if s else None

    def edit_selected(self):
        hid=self.selected()
        if hid: self.habit_dialog(hid)

    def toggle_selected(self):
        hid=self.selected()
        if hid: self.manager.toggle(hid); self.refresh_all()

    def delete_selected(self):
        hid=self.selected()
        if hid and messagebox.askyesno("Delete","Delete this habit and its records?"):
            self.manager.delete(hid); self.refresh_all()

    def habit_dialog(self, hid=None):
        old=next((h for h in self.storage.read_habits() if h["id"]==hid),{}) if hid else {}
        win=tk.Toplevel(self); win.title("Edit Habit" if hid else "Add Habit"); win.geometry("460x560"); win.configure(bg=BG); win.grab_set()
        vars={k:tk.StringVar(value=old.get(k,"")) for k in ["name","category","frequency","priority","target","start_date","description"]}
        vars["category"].set(old.get("category","Study")); vars["frequency"].set(old.get("frequency","Daily")); vars["priority"].set(old.get("priority","Medium")); vars["target"].set(old.get("target","1")); vars["start_date"].set(old.get("start_date",str(date.today())))
        labels=[("name","Habit Name"),("category","Category"),("frequency","Frequency"),("priority","Priority"),("target","Target days/week"),("start_date","Start date"),("description","Description")]
        for i,(key,label) in enumerate(labels):
            tk.Label(win,text=label,bg=BG,fg=FG).pack(anchor="w",padx=25,pady=(12,2))
            if key=="category": ttk.Combobox(win,textvariable=vars[key],values=VALID_CATEGORIES,state="readonly").pack(fill="x",padx=25)
            elif key=="frequency": ttk.Combobox(win,textvariable=vars[key],values=VALID_FREQUENCIES,state="readonly").pack(fill="x",padx=25)
            elif key=="priority": ttk.Combobox(win,textvariable=vars[key],values=VALID_PRIORITIES,state="readonly").pack(fill="x",padx=25)
            elif key=="description": tk.Entry(win,textvariable=vars[key]).pack(fill="x",padx=25)
            else: ttk.Entry(win,textvariable=vars[key]).pack(fill="x",padx=25)
        def save():
            try:
                if hid: self.manager.edit(hid,*[vars[k].get() for k in ["name","category","frequency","priority","target","start_date","description"]])
                else: self.manager.add(*[vars[k].get() for k in ["name","category","frequency","priority","target","start_date","description"]])
                win.destroy(); self.refresh_all()
            except Exception as e: messagebox.showerror("Validation",str(e),parent=win)
        ttk.Button(win,text="Save Habit",command=save).pack(pady=22)

    def refresh_track(self):
        for x in self.track_tree.get_children(): self.track_tree.delete(x)
        day=self.day.get()
        try:
            import datetime; datetime.datetime.strptime(day,"%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Date","Use YYYY-MM-DD."); return
        records={(r["habit_id"]):r["status"] for r in self.storage.read_records() if r["date"]==day}
        for h in self.storage.read_habits():
            if h["active"]=="1": self.track_tree.insert("", "end", iid=h["id"], values=(h["name"],h["category"],records.get(h["id"],"Pending")))

    def cycle_status(self,event):
        hid=self.track_tree.selection()[0]; current=self.track_tree.item(hid,"values")[2]
        status={"Pending":"Completed","Completed":"Missed","Missed":"Pending"}[current]
        self.storage.set_record(self.day.get(),hid,status); self.refresh_track(); self.refresh_dashboard(); self.refresh_habits(); self.refresh_analytics()

    def refresh_analytics(self):
        self.analytics_text.delete("1.0","end")
        a,b=self.analytics.comparison(); score=self.analytics.score()
        self.analytics_text.insert("end",f"HABIT ANALYTICS\n{'='*60}\n\nOverall consistency score : {score:.1f}%\nThis week completion       : {a:.1f}%\nPrevious week completion   : {b:.1f}%\nWeekly change              : {a-b:+.1f} percentage points\n\nPER-HABIT PERFORMANCE\n{'-'*60}\n")
        for h in self.storage.read_habits():
            cur,best=self.analytics.streaks(h["id"]); rate=self.analytics.completion_rate(h["id"])
            self.analytics_text.insert("end",f"{h['name']:<25} {rate:6.1f}%   Current streak: {cur:2d}   Best: {best:2d}\n")
        self.analytics_text.insert("end","\nPATTERN INSIGHTS\n"+"-"*60+"\n"+"\n".join("• "+x for x in self.analytics.insights()))

    def export_records(self):
        path=filedialog.asksaveasfilename(defaultextension=".csv",filetypes=[("CSV","*.csv")],initialfile="habit_records.csv")
        if path:
            self.storage.export_records(path); messagebox.showinfo("Export","Records exported successfully.")

    def toggle_theme(self):
        # A simple high-contrast theme switch suitable for Tkinter without external packages.
        self.theme_dark=not self.theme_dark
        if self.theme_dark:
            self.configure(bg=BG)
        else:
            self.configure(bg="#f1f5f9")
        messagebox.showinfo("Theme","Theme preference toggled. Restarting is not required for data changes.")
