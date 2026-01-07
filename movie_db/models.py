import reflex as rx
from datetime import datetime
from typing import Optional

class MovieEntry(rx.Model, table=True):
    tmdb_id: int
    title: str
    overview: str
    poster_path: str
    vote_average: float
    list_type: str  # "watchlist" sau "watched"
    added_at: datetime = datetime.now()