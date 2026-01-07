import reflex as rx
from .state import MovieState

def movie_card(m: rx.Var[dict]):
    # Construim URL-ul posterului în afara rx.image pentru claritate
    poster_url = "https://image.tmdb.org/t/p/w500" + m["poster_path"].to_string()

    return rx.card(
        rx.vstack(
            rx.box(
                rx.cond(
                    (m["yt_id"] != "") & (m["yt_id"] != "none"),
                    rx.html(
                        rx.format(
                            "<iframe width='100%' height='220' src='https://www.youtube.com/embed/{0}?rel=0' frameborder='0' allowfullscreen style='border-radius: 8px 8px 0 0;'></iframe>",
                            m["yt_id"]
                        )
                    ),
                    rx.box(
                        rx.image(
                            src=rx.cond(m["poster_path"] != "", poster_url, "/no_image.png"),
                            height="220px", width="100%", object_fit="cover", border_radius="8px 8px 0 0"
                        ),
                        rx.center(
                            rx.button(rx.icon(tag="play", size=30), on_click=lambda: MovieState.load_extra(m["id"]), variant="ghost"),
                            position="absolute", top="0", left="0", width="100%", height="100%", background="rgba(0,0,0,0.4)"
                        ),
                        position="relative"
                    )
                ), width="100%"
            ),
            rx.vstack(
                rx.heading(m["title"], size="3", line_clamp=1),
                rx.hstack(
                    rx.badge("⭐ " + m["vote_average"].to_string(), color_scheme="yellow"),
                    rx.text(m["studio"], size="1", color="red", weight="bold", line_clamp=1),
                    spacing="2"
                ),
                rx.text(m["genre_names"], size="1", color="#666"),
                rx.text(m["overview"], size="1", line_clamp=3, color="#aaa"),
                padding="12px", width="100%", spacing="2"
            )
        ), padding="0", background="#0f0f0f", border="1px solid #222"
    )

def sidebar():
    return rx.vstack(
        rx.heading("MOVIE_DB", color="red", size="7", weight="bold"),
        rx.input(placeholder="Caută film...", on_change=MovieState.set_search_query, width="100%"),
        rx.divider(),
        rx.text("MOODS", size="1", weight="bold", color="#555"),
        rx.flex(
            rx.button("🔥 Adrenalină", on_click=lambda: MovieState.fetch_movies(), variant="soft", size="1"),
            rx.button("☕ Relax", on_click=lambda: MovieState.fetch_movies(), variant="soft", size="1"),
            spacing="2", wrap="wrap"
        ),
        rx.divider(),
        rx.text("FILTRE AVANSATE", size="1", weight="bold", color="#555"),
        rx.vstack(
            rx.text("Ani Producție", size="1"),
            rx.hstack(rx.input(value=MovieState.y_start, on_change=MovieState.set_y_start), rx.input(value=MovieState.y_end, on_change=MovieState.set_y_end)),
            rx.text("Rating Minim", size="1"),
            rx.slider(default_value=[0], min=0, max=10, on_change=MovieState.set_min_rating),
            rx.button("APLICĂ FILTRE", on_click=MovieState.fetch_movies, width="100%", color_scheme="ruby"),
            width="100%", spacing="3"
        ),
        rx.spacer(),
        rx.button("LOGOUT", variant="outline", width="100%"),
        width="280px", height="100vh", position="fixed", left="0", padding="2em", background="#050505", border_right="1px solid #222"
    )

def index():
    return rx.flex(
        sidebar(),
        rx.box(
            rx.cond(
                MovieState.is_loading, 
                rx.center(rx.spinner(), width="100%", height="80vh"),
                rx.grid(rx.foreach(MovieState.movies, movie_card), columns=rx.breakpoints(initial="1", sm="2", lg="3", xl="4"), spacing="6", width="100%")
            ), flex="1", margin_left="280px", padding="2em"
        ), background="black", min_height="100vh"
    )

app = rx.App(theme=rx.theme(appearance="dark", accent_color="ruby"))
app.add_page(index, on_load=MovieState.fetch_movies)