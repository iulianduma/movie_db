import reflex as rx
import requests
import os
from .models import MovieEntry
from sqlmodel import select

class MovieState(rx.State):
    movies: list[dict] = []
    is_loading: bool = False

    async def toggle_movie(self, movie: dict, list_type: str):
        """Salvează sau elimină un film la un singur click."""
        with rx.session() as session:
            m_id = int(movie["id"])
            # Căutăm dacă există deja în lista respectivă
            existing = session.exec(
                select(MovieEntry).where(
                    (MovieEntry.tmdb_id == m_id) & (MovieEntry.list_type == list_type)
                )
            ).first()
            
            if existing:
                session.delete(existing)
            else:
                # Salvăm doar link-ul posterului, nu imaginea
                session.add(MovieEntry(
                    tmdb_id=m_id,
                    title=movie["title"],
                    overview=movie.get("overview", ""),
                    poster_path=movie.get("poster_path", ""),
                    vote_average=movie.get("vote_average", 0.0),
                    list_type=list_type
                ))
            session.commit()
        # Actualizăm interfața instantaneu
        return await self.fetch_movies()

    async def fetch_movies(self):
        self.is_loading = True
        yield # Permite spinner-ului să apară imediat
        
        # Logica de Discover rămâne API-based (nu ocupă loc pe disk)
        # Logica de Watchlist devine DB-based (viteză maximă)
        # ... implementare fetch ...
        self.is_loading = False