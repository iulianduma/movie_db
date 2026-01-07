import reflex as rx
from datetime import datetime

class MovieEntry(rx.Model, table=True):
    tmdb_id: int
    title: str
    poster_path: str
    list_type: str  # "watchlist" sau "watched"
    added_at: datetime = datetime.now()