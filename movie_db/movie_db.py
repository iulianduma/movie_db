import reflex as rx
from .state import MovieState

def movie_card(m: rx.Var[dict]):
    return rx.card(
        rx.vstack(
            rx.box(
                rx.cond(
                    (m["yt_id"] != "") & (m["yt_id"] != "none"),
                    rx.html("<iframe width='100%' height='220' src='https://www.youtube.com/embed/" + m["yt_id"].to_string() + "?autoplay=1' frameborder='0' allowfullscreen></iframe>"),
                    rx.box(
                        rx.image(src=m["poster_path"], height="220px", width="100%", object_fit="cover", border_radius="12px"),
                        rx.center(
                            rx.button(rx.icon(tag="play", size=30), on_click=lambda: MovieState.load_trailer(m["id"]), variant="ghost", color_scheme="gray"),
                            position="absolute", top="0", left="0", width="100%", height="100%", background="rgba(0,0,0,0.4)", border_radius="12px"
                        ),
                        position="relative"
                    )
                ), width="100%"
            ),
            rx.vstack(
                rx.hstack(
                    rx.heading(m["title"], size="3", line_clamp=1, flex="1"),
                    rx.checkbox(checked=MovieState.watched_ids.contains(m["id"].to_string()), on_change=lambda _: MovieState.toggle_list(m, "watched"), color_scheme="ruby")
                ),
                rx.badge("⭐ " + m["vote_average"].to_string(), color_scheme="yellow"),
                rx.text(m["overview"], size="1", line_clamp=2, color="#aaa"),
                padding="12px", spacing="2", width="100%"
            )
        ), padding="0", background="#0d0d0d", border="1px solid #1a1a1a", border_radius="12px"
    )

def sidebar():
    return rx.vstack(
        rx.heading("MOVIE_DB", style={"color": "#ff0000", "font_size": "42px", "font_weight": "900"}),
        rx.button("RESET FILTRE", on_click=MovieState.reset_filters, color_scheme="ruby", variant="outline", width="100%"),
        rx.divider(),
        rx.text("ANI PRODUCȚIE", size="1", weight="bold", color="#555"),
        rx.hstack(
            rx.input(placeholder="Din", on_blur=MovieState.set_y_start, width="100%"),
            rx.input(placeholder="La", on_blur=MovieState.set_y_end, width="100%"),
        ),
        rx.text("GENURI", size="1", weight="bold", color="#555"),
        rx.flex(
            rx.foreach(MovieState.genre_names_list, lambda g: rx.button(g, size="1", variant=rx.cond(MovieState.selected_genres.contains(MovieState.GENRE_MAP[g]), "solid", "outline"), on_click=lambda: MovieState.toggle_genre(g), margin="2px")),
            wrap="wrap"
        ),
        rx.button("APLICĂ", on_click=MovieState.fetch_movies, width="100%", color_scheme="ruby"),
        width="320px", height="100vh", padding="30px", background="rgba(10,10,10,0.6)", backdrop_filter="blur(20px)", position="fixed", overflow_y="auto"
    )

def index():
    return rx.flex(
        sidebar(),
        rx.box(
            rx.cond(MovieState.is_loading, rx.center(rx.spinner(color="red", size="3"), width="100%", height="80vh"),
                rx.grid(rx.foreach(MovieState.movies, movie_card), columns=rx.breakpoints(initial="1", sm="2", lg="3"), spacing="8", width="100%")
            ), flex="1", margin_left="320px", padding="5em"
        ), background="black", min_height="100vh"
    )

app = rx.App(theme=rx.theme(appearance="dark", accent_color="ruby"))
app.add_page(index, on_load=MovieState.fetch_movies)