import sqlite3
from pathlib import Path
from datetime import datetime, timezone

def init_db(name):
    Path(name).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(name) as c:
        c.execute("CREATE TABLE IF NOT EXISTS history(id INTEGER PRIMARY KEY, question TEXT, answer TEXT, created TEXT)")

def save(name, q, a):
    with sqlite3.connect(name) as c:
        c.execute("INSERT INTO history(question,answer,created) VALUES(?,?,?)",
                  (q,a,datetime.now(timezone.utc).isoformat()))

def history(name):
    with sqlite3.connect(name) as c:
        c.row_factory=sqlite3.Row
        return [dict(r) for r in c.execute("SELECT * FROM history ORDER BY id DESC LIMIT 40")]
