import tkinter as tk
from tkinter import messagebox
from modules.storage import Storage
from modules.habit_manager import HabitManager
from modules.analytics import Analytics
from modules.gui import HabitTrackApp

def main():
    try:
        storage = Storage()
        manager = HabitManager(storage)
        analytics = Analytics(storage)
        app = HabitTrackApp(manager, analytics, storage)
        app.mainloop()
    except Exception as exc:
        messagebox.showerror("HabitTrack", f"Application failed to start:\n{exc}")

if __name__ == "__main__":
    main()
