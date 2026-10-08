from pathlib import Path
import tempfile
from modules.storage import Storage
from modules.habit_manager import HabitManager
from modules.analytics import Analytics

def make():
    td=tempfile.TemporaryDirectory()
    import modules.storage as s
    old=(s.DATA,s.HABITS_FILE,s.RECORDS_FILE)
    base=Path(td.name); s.DATA=base; s.HABITS_FILE=base/"habits.csv"; s.RECORDS_FILE=base/"records.csv"
    st=Storage(); return td, st, old, s

def test_add_and_validate():
    td,st,old,s=make()
    try:
        m=HabitManager(st); h=m.add("Study","Study","Daily","High",5,"2026-10-01","Python")
        assert h["name"]=="Study"; assert len(st.read_habits())==1
    finally:
        s.DATA,s.HABITS_FILE,s.RECORDS_FILE=old; td.cleanup()

def test_record_and_rate():
    td,st,old,s=make()
    try:
        m=HabitManager(st); h=m.add("Read","Personal","Daily","Medium",3,"2026-10-01","")
        st.set_record("2026-10-08",h["id"],"Completed")
        st.set_record("2026-10-07",h["id"],"Missed")
        assert Analytics(st).completion_rate(h["id"])==50.0
    finally:
        s.DATA,s.HABITS_FILE,s.RECORDS_FILE=old; td.cleanup()

def test_duplicate_rejected():
    td,st,old,s=make()
    try:
        m=HabitManager(st); m.add("Run","Fitness","Daily","Low",2,"2026-10-01","")
        try:
            m.add("run","Fitness","Daily","Low",2,"2026-10-01","")
            assert False
        except ValueError:
            assert True
    finally:
        s.DATA,s.HABITS_FILE,s.RECORDS_FILE=old; td.cleanup()

def test_demo_data_is_repeatable_and_analytics_are_available():
    td,st,old,s=make()
    try:
        assert st.seed_demo_data() == (6, 168)
        first = (len(st.read_habits()), len(st.read_records()))
        st.seed_demo_data()
        assert (len(st.read_habits()), len(st.read_records())) == first
        completed, total = Analytics(st).daily_progress()
        assert (completed, total) == (6, 6)
        assert len(Analytics(st).recent_activity()) == 8
    finally:
        s.DATA,s.HABITS_FILE,s.RECORDS_FILE=old; td.cleanup()
