import json
import sqlite3
import os
import requests

def run_migration():
    API_KEY = "a70f38f45a8e036e4763619293111f18" # Cheia ta TMDB
    WATCHED_FILE = "watched_list.json"
    WATCHLIST_FILE = "watchlist.json"
    conn = sqlite3.connect("reflex.db")
    cursor = conn.cursor()

    for file, l_type in [(WATCHED_FILE, "watched"), (WATCHLIST_FILE, "watchlist")]:
        if os.path.exists(file):
            with open(file, "r") as f:
                ids = json.load(f)
                for mid in ids:
                    print(f"Preluare date pentru filmul {mid}...")
                    resp = requests.get(f"https://api.themoviedb.org/3/movie/{mid}?api_key={API_KEY}&language=ro-RO")
                    if resp.status_code == 200:
                        data = resp.json()
                        cursor.execute(
                            "INSERT OR IGNORE INTO movieentry (tmdb_id, title, overview, poster_path, vote_average, list_type) VALUES (?, ?, ?, ?, ?, ?)",
                            (int(mid), data['title'], data.get('overview', ''), data.get('poster_path', ''), data.get('vote_average', 0.0), l_type)
                        )
    conn.commit()
    conn.close()
    print("Migrare completa!")

if __name__ == "__main__":
    run_migration()