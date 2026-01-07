import reflex as rx
from .state import MovieState

def movie_card(m: rx.Var[dict]):
    return rx.card(
        rx.vstack(
            rx.box(
                rx.cond(
                    (m["yt_id"] != "") & (m["yt_id"] != "none"),
                    rx.html(
                        f"<iframe width='100%' height='190' src='https://www.youtube.com/embed/{m['yt_id']}?rel=0' " 
                        "frameborder='0' allow='autoplay; encrypted-media' allowfullscreen "
                        "style='border-radius: 8px 8px 0 0;'></iframe>"
                    ),
                    rx.box(
                        rx.image(src=m["poster_path"], height="190px", width="100%", object_fit="cover", border_radius="8px 8px 0 0"),
                        rx.center(
                            rx.button(rx.icon(tag="play", size=30), on_click=lambda: MovieState.load_trailer(m["id"]), variant="ghost", color_scheme="gray"),
                            position="absolute", top="0", left="0", width="100%", height="100%", background="rgba(0,0,0,0.4)"
                        ),
                        position="relative"
                    )
                ), width="100%"
            ),
            rx.vstack(
                rx.hstack(
                    rx.heading(m["title"], size="3", line_clamp=1, flex="1", color="white"),
                    rx.checkbox(checked=MovieState.watched_ids.contains(m["id"].to_string()), on_change=lambda _: MovieState.toggle_list(m, "watched"), color_scheme="ruby", size="1")
                ),
                rx.badge("⭐ " + m["vote_average"].to_string(), color_scheme="yellow", variant="soft"),
                rx.text(m["overview"], size="1", line_clamp=3, color="#888", text_align="justify"),
                padding="12px", spacing="2", width="100%"
            )
        ), padding="0", background="#0d0d0d", border="1px solid #222", border_radius="10px"
    )

def sidebar():
    return rx.vstack(
        rx.heading("MOVIE_DB PRO", size="7", color="red", weight="bold"),
        rx.button("RESET FILTRE", on_click=MovieState.reset_filters, color_scheme="ruby", variant="outline", width="100%", size="2"),
        rx.divider(opacity="0.1"),
        
        rx.accordion.root(
            rx.accordion.item(
                rx.accordion.trigger("🕒 INTERVAL & SORTARE"),
                rx.accordion.content(
                    rx.vstack(
                        rx.text("Rating Mare -> Mic", size="1", color="#555"),
                        rx.select(["vote_average.desc", "vote_average.asc", "popularity.desc", "primary_release_date.desc"], default_value="vote_average.desc", on_change=MovieState.set_sort_by, width="100%"),
                        rx.text("Ani (1950-2026)", size="1", color="#555"),
                        rx.hstack(
                            rx.input(placeholder="1950", on_blur=MovieState.set_y_start, width="100%"),
                            rx.input(placeholder="2026", on_blur=MovieState.set_y_end, width="100%"),
                        ), spacing="2"
                    )
                )
            ),
            rx.accordion.item(
                rx.accordion.trigger("🎭 FORMAT & ORIGINE"),
                rx.accordion.content(
                    rx.vstack(
                        rx.select({"movie": "Film Artistic", "tv": "Serial TV"}, placeholder="Tip Producție", on_change=MovieState.set_content_type, width="100%"),
                        rx.select({"": "Toate Limbile", "ro": "Română", "en": "Engleză", "fr": "Franceză"}, on_change=MovieState.set_language, width="100%"),
                        spacing="2"
                    )
                )
            ),
            rx.accordion.item(
                rx.accordion.trigger("🏢 STUDIOURI"),
                rx.accordion.content(
                    rx.scroll_area(
                        rx.vstack(
                            rx.foreach(MovieState.studio_names_list, lambda s: rx.checkbox(s, on_change=lambda _: MovieState.toggle_studio(s), size="1")),
                            spacing="1"
                        ), style={"height": "150px"}
                    )
                )
            ),
            rx.accordion.item(
                rx.accordion.trigger("🎬 GENURI"),
                rx.accordion.content(
                    rx.flex(
                        rx.foreach(MovieState.genre_names_list, lambda g: rx.button(
                            g, size="1", variant=rx.cond(MovieState.selected_genres.contains(MovieState.GENRE_MAP[g]), "solid", "outline"),
                            on_click=lambda: MovieState.toggle_genre(g), margin="2px"
                        )), wrap="wrap"
                    )
                )
            ),
            rx.accordion.item(
                rx.accordion.trigger("🧪 CLASIFICARE"),
                rx.accordion.content(
                    rx.select({"": "Oricare", "G": "G", "PG": "PG", "PG-13": "PG-13", "R": "R"}, on_change=MovieState.set_certification, width="100%")
                )
            ),
            width="100%", variant="ghost"
        ),
        
        rx.button("APLICĂ FILTRE", on_click=MovieState.fetch_movies, width="100%", color_scheme="ruby", size="3", margin_top="1em"),
        
        width="300px", height="100vh", padding="25px", background="rgba(10,10,10,0.95)", backdrop_filter="blur(10px)", 
        position="fixed", left="0", border_right="1px solid #222", overflow_y="auto"
    )

def index():
    return rx.flex(
        sidebar(),
        rx.box(
            rx.cond(
                MovieState.is_loading, 
                rx.center(rx.spinner(color="red", size="3"), width="100%", height="80vh"),
                rx.grid(
                    rx.foreach(MovieState.movies, movie_card), 
                    columns=rx.breakpoints(initial="1", sm="2", md="3", lg="4"), 
                    spacing="5", width="100%"
                )
            ), flex="1", margin_left="300px", padding="2em"
        ), background="black", min_height="100vh"
    )

app = rx.App(theme=rx.theme(appearance="dark", accent_color="ruby"))
app.add_page(index, on_load=MovieState.fetch_movies)