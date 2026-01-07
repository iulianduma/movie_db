import reflex as rx
from .state import MovieState

def sidebar():
    return rx.vstack(
        rx.heading("FILTRE PRO", size="6", color="red"),
        
        rx.text("SORTARE RATING", size="1", weight="bold", color="#555"),
        rx.select(
            ["vote_average.desc", "vote_average.asc", "primary_release_date.desc", "popularity.desc"],
            default_value="vote_average.desc",
            on_change=MovieState.set_sort_by,
            width="100%"
        ),

        rx.divider(),
        
        rx.text("INTERVAL ANI (1950-2026)", size="1", weight="bold", color="#555"),
        rx.hstack(
            rx.input(placeholder="1950", on_blur=MovieState.set_y_start, width="100%"),
            rx.input(placeholder="2026", on_blur=MovieState.set_y_end, width="100%"),
        ),

        rx.text("STUDIOURI PRODUCȚIE", size="1", weight="bold", color="#555"),
        rx.scroll_area(
            rx.vstack(
                rx.foreach(MovieState.studio_names, lambda s: rx.checkbox(s, on_change=lambda _: MovieState.toggle_studio(s), size="1")),
                spacing="1"
            ),
            style={"height": "150px"}
        ),

        rx.text("GENURI & TEMATICI", size="1", weight="bold", color="#555"),
        rx.flex(
            rx.foreach(MovieState.genre_names, lambda g: rx.button(
                g, size="1", variant=rx.cond(MovieState.selected_genres.contains(MovieState.GENRE_MAP[g]), "solid", "outline"),
                on_click=lambda: MovieState.toggle_genre(g), margin="2px"
            )),
            wrap="wrap"
        ),

        rx.button("APLICĂ FILTRE", on_click=MovieState.fetch_movies, width="100%", color_scheme="ruby", size="3"),
        
        width="300px", height="100vh", padding="25px", background="#0a0a0a", position="fixed", left="0", border_right="1px solid #222", overflow_y="auto"
    )

def movie_card(m: rx.Var[dict]):
    # ... logică card existentă ...
    return rx.card(
        rx.vstack(
            rx.box(
                rx.cond(
                    (m["yt_id"] != "") & (m["yt_id"] != "none"),
                    rx.video(url=f"https://www.youtube.com/watch?v={m['yt_id']}", width="100%", height="200px"),
                    rx.box(
                        rx.image(src=m["poster_path"], height="200px", width="100%", object_fit="cover"),
                        rx.center(
                            rx.button(rx.icon(tag="play"), on_click=lambda: MovieState.load_trailer(m["id"]), variant="ghost"),
                            position="absolute", top="0", width="100%", height="100%", background="rgba(0,0,0,0.4)"
                        ),
                        position="relative"
                    )
                )
            ),
            rx.vstack(
                rx.heading(m["title"], size="3", line_clamp=1),
                rx.badge(f"⭐ {m['vote_average']}", color_scheme="yellow"),
                rx.text(m["overview"], size="1", line_clamp=2, color="#666"),
                padding="10px"
            )
        ), padding="0", background="#111", border="1px solid #222"
    )

def index():
    return rx.flex(
        sidebar(),
        rx.box(
            rx.cond(
                MovieState.is_loading,
                rx.center(rx.spinner(), width="100%", height="80vh"),
                rx.grid(rx.foreach(MovieState.movies, movie_card), columns=rx.breakpoints(initial="1", sm="2", lg="4"), spacing="4", width="100%")
            ),
            flex="1", margin_left="300px", padding="2em"
        ),
        background="black", min_height="100vh"
    )

app = rx.App()
app.add_page(index, on_load=MovieState.fetch_movies)