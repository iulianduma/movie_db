import reflex as rx
from .state import MovieState

def movie_card(m: rx.Var[dict]):
    return rx.box(
        rx.image(src=m["poster_path"], width="100%", height="600px", object_fit="cover", border_radius="15px"),
        rx.vstack(
            rx.spacer(),
            rx.vstack(
                rx.hstack(
                    rx.heading(m["title"], size="6", weight="bold", color="white", style={"text_shadow": "0px 0px 15px rgba(255,255,255,0.7)"}),
                    rx.spacer(),
                    rx.badge(f"⭐ {m['vote_average']}", color_scheme="yellow", variant="solid")
                ),
                rx.text(m["overview"], size="2", color="white", line_clamp=5, style={"text_shadow": "1px 1px 10px rgba(0,0,0,0.9)"}),
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
                    rx.html(f"<iframe width='100%' height='540' src='https://www.youtube.com/embed/{m['yt_id']}?autoplay=1' frameborder='0' allowfullscreen></iframe>", width="100%", height="100%"),
                    width="100%", height="100%"
                ),
                position="absolute", top="0", left="0", width="100%", height="100%", background="black", z_index="100", border_radius="15px"
            )
        ),
        position="relative", width="100%", height="600px", border_radius="15px", overflow="hidden", border="1px solid #333"
    )

def sidebar():
    return rx.vstack(
        rx.box(
            rx.text("MOVIE", style={"font_size": "60px", "font_weight": "bold", "color": "#e11d48", "line_height": "1"}),
            rx.text("_db pro", style={"font_size": "18px", "color": "white", "letter_spacing": "10px", "margin_top": "-10px"}),
            margin_bottom="2em"
        ),
        rx.vstack(
            rx.button("DISCOVER", on_click=lambda: MovieState.set_show_mode("Discover"), width="100%", variant=rx.cond(MovieState.show_mode == "Discover", "solid", "ghost")),
            rx.button("WATCHLIST", on_click=lambda: MovieState.set_show_mode("watchlist"), width="100%", variant=rx.cond(MovieState.show_mode == "watchlist", "solid", "ghost")),
            rx.button("WATCHED", on_click=lambda: MovieState.set_show_mode("watched"), width="100%", variant=rx.cond(MovieState.show_mode == "watched", "solid", "ghost")),
            color_scheme="ruby", width="100%", spacing="2"
        ),
        rx.accordion.root(
            rx.accordion.item(
                rx.accordion.trigger("⭐ RATING INTERVAL"),
                rx.accordion.content(
                    rx.vstack(
                        rx.text("Min Nota", size="1"),
                        rx.slider(default_value=0, min=0, max=10, on_change=MovieState.set_rate_min, width="100%"),
                        rx.text("Max Nota", size="1"),
                        rx.slider(default_value=10, min=0, max=10, on_change=MovieState.set_rate_max, width="100%"),
                    )
                )
            ),
            rx.accordion.item(
                rx.accordion.trigger("🎬 GENURI & STUDIOURI"),
                rx.accordion.content(
                    rx.vstack(
                        rx.flex(rx.foreach(MovieState.genre_names, lambda g: rx.button(g, size="1", variant="ghost", on_click=lambda: MovieState.toggle_genre(g))), wrap="wrap"),
                        rx.divider(),
                        rx.scroll_area(rx.vstack(rx.foreach(MovieState.studio_names, lambda s: rx.checkbox(s, on_change=lambda _: MovieState.toggle_studio(s))), spacing="1"), style={"height": "100px"})
                    )
                )
            ),
            rx.accordion.item(
                rx.accordion.trigger("🕒 ANI PRODUCȚIE"),
                rx.accordion.content(rx.hstack(rx.input(placeholder="1950", on_blur=MovieState.set_y_start), rx.input(placeholder="2026", on_blur=MovieState.set_y_end)))
            ),
            variant="ghost", width="100%"
        ),
        rx.button("APLICĂ", on_click=MovieState.fetch_movies, width="100%", color_scheme="ruby", size="3", margin_top="auto"),
        width="320px", height="100vh", padding="30px", 
        background="rgba(0,0,0,0.5)", backdrop_filter="blur(20px)", border_right="1px solid rgba(255,255,255,0.1)", position="fixed"
    )

def index():
    return rx.box(
        style={
            "background": "radial-gradient(circle, #2a0000 0%, #000000 100%)",
            "animation": "bgMove 15s ease infinite alternate",
            "background-size": "200% 200%",
        },
        children=[
            rx.flex(
                sidebar(),
                rx.box(
                    rx.cond(MovieState.is_loading, rx.center(rx.spinner(color="red", size="3"), width="100%", height="80vh"),
                        rx.grid(rx.foreach(MovieState.movies, movie_card), columns=rx.breakpoints(initial="1", sm="2", md="2", lg="3", xl="4"), spacing="6", width="100%")
                    ), flex="1", margin_left="320px", padding="4em"
                ), min_height="100vh"
            ),
            rx.html("<style>@keyframes bgMove { 0% {background-position: 0% 50%;} 100% {background-position: 100% 50%;} }</style>")
        ]
    )

app = rx.App(theme=rx.theme(appearance="dark", accent_color="ruby"))
app.add_page(index, on_load=MovieState.fetch_movies)