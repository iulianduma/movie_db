import json
import sqlite3
import os

def migrate():
    # Căile către fișierele tale vechi
    WATCHED_FILE = "watched_list.json"
    WATCHLIST_FILE = "watchlist.json"
    DB_FILE = "reflex.db"

    if not os.path.exists(DB_FILE):
        print("❌ Eroare: reflex.db nu a fost găsit. Rulează 'reflex db init' întâi.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Migrare Watched
    if os.path.exists(WATCHED_FILE):
        with open(WATCHED_FILE, "r") as f:
            ids = json.load(f)
            for mid in ids:
                try:
                    cursor.execute(
                        "INSERT INTO movieentry (tmdb_id, title, poster_path, list_type, user_id, added_at) VALUES (?, ?, ?, ?, ?, ?)",
                        (int(mid), "Migrated", "", "watched", "admin", "2026-01-07")
                    )
                except Exception as e:
                    print(f"⚠️ Sărit ID {mid} (posibil duplicat)")

    # Migrare Watchlist
    if os.path.exists(WATCHLIST_FILE):
        with open(WATCHLIST_FILE, "r") as f:
            ids = json.load(f)
            for mid in ids:
                try:
                    cursor.execute(
                        "INSERT INTO movieentry (tmdb_id, title, poster_path, list_type, user_id, added_at) VALUES (?, ?, ?, ?, ?, ?)",
                        (int(mid), "Migrated", "", "watchlist", "admin", "2026-01-07")
                    )
                except Exception as e:
                    print(f"⚠️ Sărit ID {mid}")

    conn.commit()
    conn.close()
    print("✅ Migrare finalizată cu succes!")

if __name__ == "__main__":
    migrate()