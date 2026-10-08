from datetime import date, datetime
import uuid

VALID_CATEGORIES = ["Health","Study","Fitness","Productivity","Personal","Other"]
VALID_FREQUENCIES = ["Daily","Weekdays","Weekends","Custom"]
VALID_PRIORITIES = ["High","Medium","Low"]

class HabitManager:
    def __init__(self, storage):
        self.storage = storage

    def validate(self, name, category, frequency, priority, target, start_date):
        name = name.strip()
        if not name:
            raise ValueError("Habit name is required.")
        if category not in VALID_CATEGORIES:
            raise ValueError("Select a valid category.")
        if frequency not in VALID_FREQUENCIES:
            raise ValueError("Select a valid frequency.")
        if priority not in VALID_PRIORITIES:
            raise ValueError("Select a valid priority.")
        try:
            target = int(target)
            if not 1 <= target <= 7:
                raise ValueError
        except Exception:
            raise ValueError("Target must be an integer from 1 to 7.")
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Start date must use YYYY-MM-DD.")
        if any(h["name"].strip().lower() == name.lower() for h in self.storage.read_habits()):
            raise ValueError("A habit with this name already exists.")

    def add(self, name, category, frequency, priority, target, start_date, description):
        self.validate(name, category, frequency, priority, target, start_date)
        row = {"id": uuid.uuid4().hex[:10], "name": name.strip(),
               "category": category, "frequency": frequency, "priority": priority,
               "target": str(int(target)), "start_date": start_date,
               "description": description.strip(), "active": "1"}
        self.storage.add_habit(row)
        return row

    def edit(self, habit_id, name, category, frequency, priority, target, start_date, description):
        rows = self.storage.read_habits()
        old = next((h for h in rows if h["id"] == habit_id), None)
        if not old:
            raise ValueError("Habit not found.")
        duplicate = any(h["id"] != habit_id and h["name"].strip().lower() == name.strip().lower() for h in rows)
        if not name.strip() or duplicate:
            raise ValueError("Enter a unique, non-empty habit name.")
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
            target = int(target)
            if not 1 <= target <= 7: raise ValueError
        except Exception:
            raise ValueError("Check target and start date.")
        self.storage.update_habit(habit_id, {"name":name.strip(),"category":category,
            "frequency":frequency,"priority":priority,"target":str(target),
            "start_date":start_date,"description":description.strip()})

    def toggle(self, habit_id):
        h = next((x for x in self.storage.read_habits() if x["id"] == habit_id), None)
        if h: self.storage.update_habit(habit_id, {"active": "0" if h["active"] == "1" else "1"})

    def delete(self, habit_id):
        self.storage.delete_habit(habit_id)
