import json
import sqlite3
import os

def run_migration():
    WATCHED_FILE = "watched_list.json"
    WATCHLIST_FILE = "watchlist.json"
    conn = sqlite3.connect("reflex.db")
    cursor = conn.cursor()

    for file, l_type in [(WATCHED_FILE, "watched"), (WATCHLIST_FILE, "watchlist")]:
        if os.path.exists(file):
            with open(file, "r") as f:
                ids = json.load(f)
                for mid in ids:
                    cursor.execute(
                        "INSERT OR IGNORE INTO movieentry (tmdb_id, title, overview, poster_path, vote_average, list_type, added_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (int(mid), "Migrated", "", "", 0.0, l_type, "2026-01-07 12:00:00")
                    )
    conn.commit()
    conn.close()
    print("Migrare terminată!")

if __name__ == "__main__":
    run_migration()