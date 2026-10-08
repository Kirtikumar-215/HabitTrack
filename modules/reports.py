from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import date, timedelta

def weekly_trend(storage, parent=None):
    r = pd.DataFrame(storage.read_records())
    if r.empty: return _empty("No tracking data yet.", parent)
    r["date"] = pd.to_datetime(r["date"])
    days = pd.date_range(end=pd.Timestamp.today().normalize(), periods=14)
    vals = [float((r[r.date.dt.normalize() == d].status == "Completed").mean()*100) if not r[r.date.dt.normalize() == d].empty else 0 for d in days]
    fig, ax = plt.subplots(figsize=(9,4.5))
    ax.plot(days, vals, marker="o"); ax.set_title("14-Day Completion Trend"); ax.set_ylabel("Completion %"); ax.set_ylim(0,100); ax.grid(alpha=.25)
    fig.autofmt_xdate(); return _show(fig, parent)

def habit_comparison(storage, parent=None):
    h = pd.DataFrame(storage.read_habits()); r = pd.DataFrame(storage.read_records())
    if h.empty: return _empty("Add habits to compare them.", parent)
    vals=[]
    for _, x in h.iterrows():
        rr=r[r.habit_id==x.id] if not r.empty else pd.DataFrame()
        vals.append(float((rr.status=="Completed").mean()*100) if not rr.empty else 0)
    fig, ax=plt.subplots(figsize=(9,4.5)); ax.bar(h.name, vals); ax.set_ylabel("Completion %"); ax.set_ylim(0,100); ax.set_title("Habit Performance Comparison"); ax.tick_params(axis="x", rotation=30)
    return _show(fig,parent)

def status_distribution(storage, parent=None):
    r=pd.DataFrame(storage.read_records())
    counts=r.status.value_counts() if not r.empty else pd.Series(dtype=int)
    fig, ax=plt.subplots(figsize=(6,5))
    if counts.empty: ax.text(.5,.5,"No tracking data yet.",ha="center",va="center"); ax.axis("off")
    else: ax.pie(counts.values, labels=counts.index, autopct="%1.0f%%"); ax.set_title("Completed vs Missed vs Pending")
    return _show(fig,parent)

def heatmap(storage, parent=None):
    r=pd.DataFrame(storage.read_records())
    days=pd.date_range(end=pd.Timestamp.today().normalize(), periods=35)
    vals=[]
    for d in days:
        rr=r[pd.to_datetime(r.date).dt.normalize()==d] if not r.empty else pd.DataFrame()
        vals.append(float((rr.status=="Completed").mean()*100) if not rr.empty else 0)
    matrix=np.array(vals).reshape(5,7)
    fig,ax=plt.subplots(figsize=(9,4)); im=ax.imshow(matrix, aspect="auto"); ax.set_title("35-Day Consistency Heatmap"); ax.set_xlabel("Day of week"); ax.set_ylabel("Week"); fig.colorbar(im,ax=ax,label="Completion %")
    return _show(fig,parent)

def _show(fig,parent):
    if parent is not None:
        fig.canvas.manager.set_window_title("HabitTrack Report")
    plt.show()
    return fig

def _empty(msg,parent):
    fig,ax=plt.subplots(figsize=(7,4)); ax.text(.5,.5,msg,ha="center",va="center"); ax.axis("off"); plt.show(); return fig
