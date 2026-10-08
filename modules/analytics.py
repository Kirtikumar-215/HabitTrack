from datetime import date, timedelta
import pandas as pd
import numpy as np

class Analytics:
    def __init__(self, storage):
        self.storage = storage

    def frames(self):
        habits = pd.DataFrame(self.storage.read_habits())
        records = pd.DataFrame(self.storage.read_records())
        if habits.empty:
            habits = pd.DataFrame(columns=["id","name","category","frequency","priority","target","start_date","description","active"])
        if records.empty:
            records = pd.DataFrame(columns=["date","habit_id","status"])
        if not records.empty:
            records["date"] = pd.to_datetime(records["date"], errors="coerce")
        return habits, records

    def completion_rate(self, habit_id=None, start=None, end=None):
        _, r = self.frames()
        if r.empty: return 0.0
        if habit_id: r = r[r.habit_id == habit_id]
        if start: r = r[r.date >= pd.Timestamp(start)]
        if end: r = r[r.date <= pd.Timestamp(end)]
        if r.empty: return 0.0
        return float((r.status == "Completed").mean() * 100)

    def status_counts(self, start=None, end=None):
        _, r = self.frames()
        if start: r = r[r.date >= pd.Timestamp(start)]
        if end: r = r[r.date <= pd.Timestamp(end)]
        return r["status"].value_counts().to_dict() if not r.empty else {}

    def streaks(self, habit_id):
        _, r = self.frames()
        if r.empty: return 0, 0
        days = sorted(set(r[(r.habit_id == habit_id) & (r.status == "Completed")]["date"].dt.date))
        if not days: return 0, 0
        best = cur = 1
        for a,b in zip(days, days[1:]):
            if b == a + timedelta(days=1): cur += 1
            else: cur = 1
            best = max(best, cur)
        today = date.today()
        current = 0
        d = today
        while d in days:
            current += 1; d -= timedelta(days=1)
        return current, best

    def habit_rates(self):
        h, _ = self.frames()
        return {row["id"]: self.completion_rate(row["id"]) for _, row in h.iterrows()}

    def score(self):
        rates = list(self.habit_rates().values())
        return round(float(np.mean(rates)) if rates else 0.0, 1)

    def insights(self):
        h, r = self.frames()
        if h.empty: return ["Add your first habit to start receiving insights."]
        insights = []
        rates = self.habit_rates()
        for _, row in h.iterrows():
            rate = rates.get(row["id"], 0)
            if rate >= 80: insights.append(f"📈 {row['name']} is highly consistent at {rate:.0f}%.")
            elif rate < 40: insights.append(f"⚠ {row['name']} needs attention: only {rate:.0f}% completion.")
        if r.empty:
            return insights or ["Start tracking today to unlock pattern insights."]
        r = r.copy()
        r["date"] = pd.to_datetime(r["date"])
        cutoff = pd.Timestamp.today().normalize() - pd.Timedelta(days=14)
        recent = r[r.date >= cutoff]
        if not recent.empty:
            missed = recent[recent.status == "Missed"]["habit_id"].value_counts()
            for hid, n in missed.items():
                if n >= 3:
                    name = next((x["name"] for x in self.storage.read_habits() if x["id"] == hid), hid)
                    insights.append(f"🔎 {name} was missed {int(n)} times in the last 14 days.")
        return insights[:8] or ["Your tracking is stable. Keep building consistency!"]

    def comparison(self):
        end = date.today()
        this_start = end - timedelta(days=6)
        prev_end = this_start - timedelta(days=1)
        prev_start = prev_end - timedelta(days=6)
        return self.completion_rate(start=this_start, end=end), self.completion_rate(start=prev_start, end=prev_end)

    def achievements(self):
        score = self.score()
        total = len(self.storage.read_habits())
        badges = []
        if total >= 1: badges.append("🌱 First Habit")
        if total >= 5: badges.append("🧩 Habit Builder")
        if score >= 70: badges.append("⭐ Consistency Star")
        if score >= 90: badges.append("🏆 Master of Consistency")
        return badges or ["🌱 Start your journey"]

    def daily_progress(self, day=None):
        day = day or date.today()
        habits = [h for h in self.storage.read_habits() if h["active"] == "1"]
        records = {r["habit_id"]: r["status"] for r in self.storage.read_records()
                   if r["date"] == str(day)}
        completed = sum(records.get(h["id"]) == "Completed" for h in habits)
        return completed, len(habits)

    def recent_activity(self, limit=8):
        habits = {h["id"]: h["name"] for h in self.storage.read_habits()}
        records = [r for r in self.storage.read_records() if r["status"] != "Pending"]
        records.sort(key=lambda r: (r["date"], r["habit_id"]), reverse=True)
        return [(r["date"], habits.get(r["habit_id"], "Unknown habit"), r["status"])
                for r in records[:limit]]
