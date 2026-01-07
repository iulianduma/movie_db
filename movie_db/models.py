import reflex as rx
from datetime import datetime

class MovieEntry(rx.Model, table=True):
    tmdb_id: int
    title: str
    overview: str
    poster_path: str
    vote_average: float
    list_type: str 
    added_at: datetime = rx.Field(default_factory=datetime.now)