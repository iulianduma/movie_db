import reflex as rx
from typing import Optional
from datetime import datetime

class MovieEntry(rx.Model, table=True):
    """Tabelul care înlocuiește fișierele JSON."""
    tmdb_id: int
    title: str
    poster_path: str
    list_type: str  # "watchlist" sau "watched"
    added_at: datetime = datetime.now()
    user_id: str = "admin"