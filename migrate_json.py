import json
import sqlite3
import os

def run_migration():
    WATCHED_FILE = "watched_list.json"
    WATCHLIST_FILE = "watchlist.json"
    DB_FILE = "reflex.db"
    
    if not os.path.exists(DB_FILE):
        print("Eroare: reflex.db nu exista in acest folder!")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    for file, l_type in [(WATCHED_FILE, "watched"), (WATCHLIST_FILE, "watchlist")]:
        if os.path.exists(file):
            with open(file, "r") as f:
                try:
                    ids = json.load(f)
                    count = 0
                    for mid in ids:
                        # INSERT OR IGNORE previne erorile daca filmul exista deja
                        cursor.execute(
                            "INSERT OR IGNORE INTO movieentry (tmdb_id, title, overview, poster_path, vote_average, list_type, added_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (int(mid), "Migrated", "Acest film a fost importat din lista veche JSON.", "", 0.0, l_type, "2026-01-07 12:00:00")
                        )
                        count += 1
                    print(f"Am importat {count} filme din {file}")
                except Exception as e:
                    print(f"Eroare la citirea {file}: {e}")
        else:
            print(f"Fisierul {file} nu a fost gasit, sarim peste.")

    conn.commit()
    conn.close()
    print("Migrare terminata cu succes!")

if __name__ == "__main__":
    run_migration()
