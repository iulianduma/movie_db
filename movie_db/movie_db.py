import reflex as rx
from .state import MovieState

def movie_card(m: rx.Var[dict]):
    return rx.box(
        rx.image(src=m["poster_path"], width="100%", height="600px", object_fit="cover", border_radius="15px"),
        rx.vstack(
            rx.spacer(),
            rx.vstack(
                rx.hstack(
                    rx.heading(m["title"], size="6", weight="bold", color="white", style={"text_shadow": "0px 0px 15px rgba(255,255,255,0.5)"}),
                    rx.spacer(),
                    rx.badge(f"⭐ {m['vote_average']}", color_scheme="yellow", variant="solid")
                ),
                rx.text(m["overview"], size="2", color="white", line_clamp=5, style={"text_shadow": "1px 1px 10px rgba(0,0,0,0.8)"}),
                rx.hstack(
                    rx.button(rx.cond(MovieState.watched_ids.contains(m["id"].to_string()), rx.icon(tag="check-circle", color="#00ff00"), rx.icon(tag="circle")), "Vizionat", size="1", variant="ghost", color="white", on_click=lambda: MovieState.toggle_status(m, "watched")),
                    rx.button(rx.cond(MovieState.watchlist_ids.contains(m["id"].to_string()), rx.icon(tag="bookmark-check", color="#00d4ff"), rx.icon(tag="bookmark")), "Later", size="1", variant="ghost", color="white", on_click=lambda: MovieState.toggle_status(m, "watchlist")),
                    spacing="4", width="100%", padding_top="10px"
                ),
                rx.button("VEZI TRAILER", rx.icon(tag="play"), width="100%", size="3", color_scheme="ruby", on_click=lambda: MovieState.load_trailer(m["id"]), margin_top="10px"),
                padding="30px", background="linear-gradient(to top, rgba(0,0,0,1) 0%, rgba(0,0,0,0.8) 50%, rgba(0,0,0,0) 100%)", border_radius="0 0 15px 15px", width="100%"
            ),
            width="100%", height="100%", position="absolute", top="0", left="0"
        ),
        rx.cond(
            (m["yt_id"] != "") & (m["yt_id"] != "none"),
            rx.box(
                rx.vstack(
                    rx.button(rx.icon(tag="x"), on_click=lambda: MovieState.close_trailer(m["id"]), variant="ghost", color="white", align_self="end"),
                    rx.html(f"<iframe width='100%' height='550' src='https://www.youtube.com/embed/{m['yt_id']}?autoplay=1' frameborder='0' allowfullscreen></iframe>", width="100%", height="100%"),
                    width="100%", height="100%"
                ),
                position="absolute", top="0", left="0", width="100%", height="100%", background="black", z_index="100", border_radius="15px"
            )
        ),
        position="relative", width="100%", height="600px", border_radius="15px", overflow="hidden", border="1px solid #222"
    )

def sidebar():
    return rx.vstack(
        # TITLU IMPUNATOR
        rx.box(
            rx.text("MOVIE", size="9", weight="bold", color="red", line_height="1"),
            rx.text("_db pro", size="4", weight="medium", color="white", margin_top="-10px", letter_spacing="4px"),
            margin_bottom="1.5em", padding_left="10px"
        ),
        rx.vstack(
            rx.button("EXPLOREAZĂ", on_click=lambda: MovieState.set_show_mode("Discover"), width="100%", variant=rx.cond(MovieState.show_mode == "Discover", "solid", "ghost")),
            rx.button("DE VIZIONAT", on_click=lambda: MovieState.set_show_mode("watchlist"), width="100%", variant=rx.cond(MovieState.show_mode == "watchlist", "solid", "ghost")),
            rx.button("VIZIONATE", on_click=lambda: MovieState.set_show_mode("watched"), width="100%", variant=rx.cond(MovieState.show_mode == "watched", "solid", "ghost")),
            color_scheme="ruby", width="100%", spacing="2"
        ),
        rx.accordion.root(
            rx.accordion.item(
                rx.accordion.trigger("🕒 TIMP & SORTARE"),
                rx.accordion.content(rx.vstack(rx.select(["vote_average.desc", "popularity.desc"], on_change=MovieState.set_sort_by, width="100%"), rx.hstack(rx.input(placeholder="1950", on_blur=MovieState.set_y_start), rx.input(placeholder="2026", on_blur=MovieState.set_y_end))))
            ),
            rx.accordion.item(
                rx.accordion.trigger("🎬 GENURI"),
                rx.accordion.content(rx.flex(rx.foreach(MovieState.genre_names_list, lambda g: rx.button(g, size="1", variant=rx.cond(MovieState.selected_genres.contains(MovieState.GENRE_MAP[g]), "solid", "outline"), on_click=lambda: MovieState.toggle_genre(g), margin="2px")), wrap="wrap"))
            ),
            rx.accordion.item(
                rx.accordion.trigger("🏢 STUDIOURI"),
                rx.accordion.content(rx.scroll_area(rx.vstack(rx.foreach(MovieState.studio_names_list, lambda s: rx.checkbox(s, on_change=lambda _: MovieState.toggle_studio(s), size="1")), spacing="1"), style={"height": "150px"}))
            ),
            rx.accordion.item(
                rx.accordion.trigger("🎭 FORMAT & LIMBĂ"),
                rx.accordion.content(rx.vstack(rx.select({"movie": "Filme", "tv": "Seriale"}, on_change=MovieState.set_type, width="100%"), rx.select({"": "Toate", "ro": "Română", "en": "Engleză"}, on_change=MovieState.set_lang, width="100%")))
            ),
            variant="ghost", width="100%"
        ),
        rx.button("APLICĂ FILTRE", on_click=MovieState.fetch_movies, width="100%", color_scheme="ruby", size="3", margin_top="1em"),
        rx.button("RESET", on_click=MovieState.reset_filters, width="100%", variant="ghost", size="1"),
        width="300px", height="100vh", padding="25px", background="rgba(10,10,10,0.95)", backdrop_filter="blur(10px)", position="fixed", overflow_y="auto"
    )

def index():
    return rx.flex(sidebar(), rx.box(rx.cond(MovieState.is_loading, rx.center(rx.spinner(color="red", size="3"), width="100%", height="80vh"), rx.grid(rx.foreach(MovieState.movies, movie_card), columns=rx.breakpoints(initial="1", sm="2", md="2", lg="3", xl="4"), spacing="6", width="100%")), flex="1", margin_left="300px", padding="4em"), background="black", min_height="100vh")

app = rx.App(theme=rx.theme(appearance="dark", accent_color="ruby"))
app.add_page(index, on_load=MovieState.fetch_movies)