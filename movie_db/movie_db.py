import reflex as rx
from .state import MovieState, FilterState

def movie_card(m: rx.Var[dict]):
    return rx.card(
        rx.vstack(
            rx.box(
                rx.cond(
                    m["yt_id"] != "",
                    rx.html(rx.format('<iframe width="100%" height="220" src="https://www.youtube.com/embed/{0}?autoplay=1" frameborder="0" allowfullscreen style="border-radius:12px 12px 0 0"></iframe>', m["yt_id"])),
                    rx.box(
                        rx.image(src="https://image.tmdb.org/t/p/w500" + m["poster_path"].to_string(), height="220px", width="100%", object_fit="cover", border_radius="12px 12px 0 0"),
                        rx.center(rx.button(rx.icon(tag="play"), on_click=lambda: MovieState.load_trailer(m["id"]), variant="ghost"), position="absolute", top="0", left="0", width="100%", height="100%", background="rgba(0,0,0,0.4)"),
                        position="relative"
                    )
                ), width="100%"
            ),
            rx.vstack(
                rx.hstack(
                    rx.heading(m["title"], size="3", line_clamp=1, flex="1"),
                    rx.vstack(
                        rx.checkbox(checked=MovieState.watched_ids.contains(m["id"].to_string()), on_change=lambda _: MovieState.toggle_movie(m, "watched"), color_scheme="ruby"),
                        rx.checkbox(checked=MovieState.watchlist_ids.contains(m["id"].to_string()), on_change=lambda _: MovieState.toggle_movie(m, "watchlist"), color_scheme="blue"),
                        spacing="1"
                    )
                ),
                rx.text(m["overview"], size="1", line_clamp=3, color="#888"),
                padding="15px", width="100%"
            )
        ),
        padding="0", background="#0a0a0a", border="1px solid #222"
    )

def sidebar():
    return rx.vstack(
        rx.heading("MOVIE_DB", color="red", size="8", weight="black"),
        rx.vstack(
            rx.button("DISCOVER", on_click=lambda: [FilterState.set_show_mode("Discover"), MovieState.fetch_movies()], width="100%"),
            rx.button("WATCHLIST", on_click=lambda: [FilterState.set_show_mode("Watchlist"), MovieState.fetch_movies()], width="100%"),
            rx.button("WATCHED", on_click=lambda: [FilterState.set_show_mode("Watched"), MovieState.fetch_movies()], width="100%"),
            spacing="2", width="100%", color_scheme="ruby"
        ),
        rx.text("ANI PRODUCȚIE", size="1", color="#555", weight="bold"),
        rx.hstack(rx.input(placeholder="Din", on_blur=FilterState.set_y_start), rx.input(placeholder="La", on_blur=FilterState.set_y_end)),
        width="300px", height="100vh", padding="2em", position="fixed", left="0", background="#050505", border_right="1px solid #111"
    )

def index():
    return rx.flex(
        sidebar(),
        rx.box(
            rx.cond(
                MovieState.is_loading,
                rx.center(rx.spinner(size="3"), width="100%", height="80vh"),
                rx.grid(
                    rx.foreach(MovieState.movies, movie_card),
                    columns=rx.breakpoints(initial="1", sm="2", lg="3", xl="4"),
                    spacing="6", width="100%"
                )
            ),
            flex="1", margin_left="300px", padding="2em"
        ),
        background="black", min_height="100vh"
    )

app = rx.App(theme=rx.theme(appearance="dark", accent_color="ruby"))
app.add_page(index, on_load=MovieState.fetch_movies)