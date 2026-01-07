import reflex as rx
from .state import MovieState

def mood_bar():
    return rx.hstack(
        rx.foreach(
            ["Discover", "Adrenalină", "Relaxare", "Mister", "Futuristic"],
            lambda mood: rx.button(
                mood,
                on_click=lambda: MovieState.get_discover_movies(mood),
                variant=rx.cond(MovieState.current_mood == mood, "solid", "outline"),
                color_scheme="ruby",
                border_radius="20px",
            )
        ),
        padding_y="1em", overflow_x="auto", width="100%", spacing="4"
    )

def movie_card(m: rx.Var[dict]):
    return rx.card(
        rx.vstack(
            rx.image(
                src="https://image.tmdb.org/t/p/w500" + m["poster_path"].to_string(),
                height="250px", width="100%", object_fit="cover", border_radius="8px 8px 0 0"
            ),
            rx.vstack(
                rx.hstack(
                    rx.heading(m["title"], size="3", line_clamp=1, flex="1"),
                    rx.vstack(
                        rx.checkbox(checked=MovieState.watched_ids.contains(m["id"].to_string()), on_change=lambda _: MovieState.toggle_list(m, "watched"), color_scheme="ruby"),
                        rx.checkbox(checked=MovieState.watchlist_ids.contains(m["id"].to_string()), on_change=lambda _: MovieState.toggle_list(m, "watchlist"), color_scheme="blue"),
                        spacing="1"
                    )
                ),
                rx.badge("⭐ " + m["vote_average"].to_string(), color_scheme="yellow"),
                rx.text(m["overview"], size="1", line_clamp=3, color="#aaa"),
                padding="12px", width="100%", spacing="2"
            )
        ),
        padding="0", background="rgba(15,15,15,0.7)", backdrop_filter="blur(10px)", border="1px solid #222"
    )

def sidebar():
    return rx.vstack(
        rx.heading("MOVIE_DB", color="red", size="8", weight="bold"),
        rx.divider(alpha=0.1),
        rx.button("DISCOVER", on_click=lambda: MovieState.set_mode("Discover"), width="100%", variant="ghost"),
        rx.button("WATCHLIST", on_click=lambda: MovieState.set_mode("Watchlist"), width="100%", variant="ghost"),
        rx.button("WATCHED", on_click=lambda: MovieState.set_mode("Watched"), width="100%", variant="ghost"),
        width="280px", height="100vh", position="fixed", left="0", padding="2em", background="#050505", border_right="1px solid #111", spacing="4"
    )

def index():
    return rx.flex(
        sidebar(),
        rx.box(
            mood_bar(),
            rx.cond(
                MovieState.is_loading,
                rx.center(rx.spinner(size="3"), width="100%", height="50vh"),
                rx.grid(
                    rx.foreach(MovieState.movies, movie_card),
                    columns=rx.breakpoints(initial="1", sm="2", md="3", lg="4"),
                    spacing="6", width="100%"
                )
            ),
            flex="1", margin_left="280px", padding="2em"
        ),
        background="black", min_height="100vh", color="white"
    )

app = rx.App(theme=rx.theme(appearance="dark", accent_color="ruby"))
app.add_page(index, on_load=MovieState.fetch_movies)