from pathlib import Path
from datetime import date, timedelta
import csv
import uuid

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"
HABITS_FILE = DATA / "habits.csv"
RECORDS_FILE = DATA / "records.csv"

HABIT_FIELDS = ["id","name","category","frequency","priority","target","start_date","description","active"]
RECORD_FIELDS = ["date","habit_id","status"]

class Storage:
    def __init__(self):
        DATA.mkdir(exist_ok=True)
        self._ensure(HABITS_FILE, HABIT_FIELDS)
        self._ensure(RECORDS_FILE, RECORD_FIELDS)

    def _ensure(self, path, fields):
        if not path.exists():
            with path.open("w", newline="", encoding="utf-8") as f:
                csv.DictWriter(f, fieldnames=fields).writeheader()

    def read_habits(self):
        with HABITS_FILE.open(encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def write_habits(self, rows):
        with HABITS_FILE.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=HABIT_FIELDS)
            w.writeheader(); w.writerows(rows)

    def read_records(self):
        with RECORDS_FILE.open(encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def write_records(self, rows):
        with RECORDS_FILE.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=RECORD_FIELDS)
            w.writeheader(); w.writerows(rows)

    def add_habit(self, row):
        rows = self.read_habits()
        rows.append(row)
        self.write_habits(rows)

    def update_habit(self, habit_id, updates):
        rows = self.read_habits()
        for r in rows:
            if r["id"] == habit_id:
                r.update(updates)
        self.write_habits(rows)

    def delete_habit(self, habit_id):
        self.write_habits([r for r in self.read_habits() if r["id"] != habit_id])
        self.write_records([r for r in self.read_records() if r["habit_id"] != habit_id])

    def set_record(self, day, habit_id, status):
        rows = self.read_records()
        found = False
        for r in rows:
            if r["date"] == day and r["habit_id"] == habit_id:
                r["status"] = status
                found = True
        if not found:
            rows.append({"date": day, "habit_id": habit_id, "status": status})
        self.write_records(rows)

    def export_records(self, path):
        import shutil
        shutil.copy2(RECORDS_FILE, path)

    def export_habits(self, path):
        import shutil
        shutil.copy2(HABITS_FILE, path)

    def seed_demo_data(self):
        """Add a realistic, repeatable demo set without duplicating existing rows."""
        demo_habits = [
            {"id": "demo-water", "name": "Drink 8 glasses of water", "category": "Health",
             "frequency": "Daily", "priority": "High", "target": "7",
             "start_date": str(date.today() - timedelta(days=21)),
             "description": "Stay hydrated throughout the workday.", "active": "1"},
            {"id": "demo-reading", "name": "Read for 20 minutes", "category": "Personal",
             "frequency": "Daily", "priority": "Medium", "target": "5",
             "start_date": str(date.today() - timedelta(days=28)),
             "description": "Read a book instead of scrolling.", "active": "1"},
            {"id": "demo-workout", "name": "Morning workout", "category": "Fitness",
             "frequency": "Weekdays", "priority": "High", "target": "5",
             "start_date": str(date.today() - timedelta(days=35)),
             "description": "A short strength or mobility session.", "active": "1"},
            {"id": "demo-focus", "name": "Deep work block", "category": "Productivity",
             "frequency": "Weekdays", "priority": "High", "target": "5",
             "start_date": str(date.today() - timedelta(days=14)),
             "description": "Complete one distraction-free focus block.", "active": "1"},
            {"id": "demo-language", "name": "Practice Spanish", "category": "Study",
             "frequency": "Daily", "priority": "Low", "target": "4",
             "start_date": str(date.today() - timedelta(days=21)),
             "description": "Complete one short lesson or review session.", "active": "1"},
            {"id": "demo-journal", "name": "Evening journal", "category": "Personal",
             "frequency": "Weekends", "priority": "Medium", "target": "2",
             "start_date": str(date.today() - timedelta(days=14)),
             "description": "Write down one win and one reflection.", "active": "1"},
        ]
        habits = self.read_habits()
        existing_ids = {row["id"] for row in habits}
        habits.extend(row for row in demo_habits if row["id"] not in existing_ids)
        self.write_habits(habits)

        patterns = {
            "demo-water": [1, 1, 1, 0, 1, 1, 1],
            "demo-reading": [1, 1, 0, 1, 1, 0, 1],
            "demo-workout": [1, 1, 0, 1, 1, 1, 0],
            "demo-focus": [1, 1, 1, 0, 1, 0, 1],
            "demo-language": [1, 0, 1, 0, 1, 1, 0],
            "demo-journal": [1, 0, 0, 1, 0, 0, 1],
        }
        records = self.read_records()
        existing = {(row["date"], row["habit_id"]) for row in records}
        for days_ago in range(27, -1, -1):
            day = date.today() - timedelta(days=days_ago)
            for habit_id, pattern in patterns.items():
                if (str(day), habit_id) in existing:
                    continue
                value = pattern[days_ago % len(pattern)]
                status = "Completed" if value else ("Missed" if days_ago % 5 else "Pending")
                records.append({"date": str(day), "habit_id": habit_id, "status": status})
        self.write_records(records)
        return len(demo_habits), 28 * len(patterns)
