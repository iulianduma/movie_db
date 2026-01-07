import reflex as rx
from .state import MovieState

def movie_card(m: rx.Var[dict]):
    return rx.card(
        rx.vstack(
            rx.box(
                rx.cond(
                    (m["yt_id"] != "") & (m["yt_id"] != "none"),
                    rx.html("<iframe width='100%' height='220' src='https://www.youtube.com/embed/" + m["yt_id"].to_string() + "?autoplay=1' frameborder='0' allowfullscreen style='border-radius: 8px 8px 0 0;'></iframe>"),
                    rx.box(
                        rx.image(src="https://image.tmdb.org/t/p/w500" + m["poster_path"].to_string(), height="220px", width="100%", object_fit="cover", border_radius="8px 8px 0 0"),
                        rx.center(rx.button(rx.icon(tag="play", size=30), on_click=lambda: MovieState.load_extra(m["id"]), variant="ghost"), position="absolute", top="0", left="0", width="100%", height="100%", background="rgba(0,0,0,0.4)"),
                        position="relative"
                    )
                ), width="100%"
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
                rx.hstack(
                    rx.badge("⭐ " + m["vote_average"].to_string(), color_scheme="yellow"),
                    rx.text(m["studio"], size="1", color="red", weight="bold"),
                    rx.text(m["genre_names"], size="1", color="#666"),
                    spacing="2", align="center"
                ),
                rx.text(m["overview"], size="1", line_clamp=3, color="#aaa"),
                padding="12px", width="100%", spacing="2"
            )
        ), padding="0", background="#0f0f0f", border="1px solid #222"
    )

def sidebar():
    return rx.vstack(
        rx.heading("MOVIE_DB", color="red", size="8", weight="bold"),
        rx.hstack(rx.input(placeholder="Caută...", on_change=MovieState.set_search_query, width="100%"), rx.button(rx.icon(tag="search"), on_click=MovieState.fetch_movies, color_scheme="ruby")),
        rx.divider(),
        rx.button("DISCOVER", on_click=lambda: [MovieState.set_show_mode("Discover"), MovieState.fetch_movies()], width="100%", variant="soft"),
        rx.button("WATCHLIST", on_click=lambda: [MovieState.set_show_mode("Watchlist"), MovieState.fetch_movies()], width="100%", variant="ghost"),
        rx.button("WATCHED", on_click=lambda: [MovieState.set_show_mode("Watched"), MovieState.fetch_movies()], width="100%", variant="ghost"),
        rx.divider(),
        rx.text("FILTRE", size="1", weight="bold", color="#555"),
        rx.vstack(
            rx.text("Ani Producție", size="1"),
            rx.hstack(rx.input(placeholder="Din", on_blur=MovieState.set_y_start), rx.input(placeholder="La", on_blur=MovieState.set_y_end)),
            rx.text("Rating Minim", size="1"),
            rx.input(placeholder="0-10", on_blur=MovieState.set_min_rating),
            width="100%", spacing="2"
        ),
        rx.spacer(),
        rx.button("LOGOUT", variant="outline", width="100%"),
        width="280px", height="100vh", position="fixed", left="0", padding="2em", background="#050505", border_right="1px solid #222", spacing="4"
    )

def index():
    return rx.flex(
        sidebar(),
        rx.box(
            rx.cond(MovieState.is_loading, rx.center(rx.spinner()), 
                    rx.grid(rx.foreach(MovieState.movies, movie_card), columns=rx.breakpoints(initial="1", sm="2", lg="3", xl="4"), spacing="6", width="100%")
            ), flex="1", margin_left="280px", padding="2em"
        ), background="black", min_height="100vh", color="white"
    )

app = rx.App(theme=rx.theme(appearance="dark", accent_color="ruby"))
app.add_page(index, on_load=MovieState.fetch_movies)