import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / 'movie_recommender.db'
if not DB.exists():
    print('DB not found at', DB)
    raise SystemExit(1)

con = sqlite3.connect(str(DB))
cur = con.cursor()
for t in ('users','movies','ratings','viewing_history'):
    try:
        cur.execute(f'SELECT COUNT(*) FROM {t}')
        print(t, cur.fetchone()[0])
    except Exception as e:
        print(t, 'ERROR', e)
con.close()
