# ... în interiorul clasei MovieState ...
    async def toggle_list(self, movie: dict, l_type: str):
        with rx.session() as session:
            m_id = int(movie["id"])
            exist = session.exec(
                select(MovieEntry).where(
                    (MovieEntry.tmdb_id == m_id) & (MovieEntry.list_type == l_type)
                )
            ).first()
            
            if exist:
                session.delete(exist)
            else:
                # Creăm obiectul și forțăm data acum pentru a evita eroarea IntegrityError
                new_entry = MovieEntry(
                    tmdb_id=m_id, 
                    title=movie["title"], 
                    overview=movie["overview"], 
                    poster_path=movie["poster_path"].replace("https://image.tmdb.org/t/p/w500", ""), 
                    vote_average=movie["vote_average"], 
                    list_type=l_type,
                    added_at=datetime.now() # Forțăm data aici
                )
                session.add(new_entry)
            session.commit()
        return await self.fetch_movies()