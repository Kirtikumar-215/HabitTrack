# HabitTrack — Habit Consistency & Productivity Analyzer

A desktop habit tracker built with Python, Tkinter, Pandas/NumPy and Matplotlib.

## Features
- Dashboard with KPI cards
- Dashboard recent-activity feed and today's completion progress
- One-click, repeatable demo data seeding with six realistic habits and 28 days of history
- Add/edit/delete/activate/deactivate habits
- Daily habit tracking with Completed/Missed/Pending status
- Categories, frequency, priority, targets and descriptions
- Search and filtering
- Current and longest streaks
- Consistency score
- Weekly/monthly/yearly analytics
- Period comparison
- Automatic improvement/decline/missed-habit insights
- Four Matplotlib reports: weekly trend, habit comparison, status distribution, calendar heatmap
- Achievements/badges
- CSV export
- Persistent CSV storage
- Input validation and exception handling
- Dark/light theme
- Modular architecture and tests

## Run
```bash
pip install -r requirements.txt
python main.py
```

## Test
```bash
python -m pytest -q
```

Data is stored locally in `data/habits.csv` and `data/records.csv`.

## Demo data

Launch the app and select **Load Demo Data** on the Dashboard to add realistic
habits and four weeks of Completed, Missed, and Pending activity. The action is
safe to repeat: seeded rows use stable IDs and are not duplicated.
