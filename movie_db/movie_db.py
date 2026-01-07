import reflex as rx
from .state import MovieState

# --- CARDUL FILMULUI (Neschimbat) ---
def movie_card(m: rx.Var[dict]):
    return rx.box(
        rx.image(src=m["poster_path"], width="100%", height="600px", object_fit="cover", border_radius="15px"),
        rx.vstack(
            rx.spacer(),
            rx.vstack(
                rx.hstack(
                    rx.heading(m["title"], size="6", weight="bold", color="white", 
                               style={"text_shadow": "0px 0px 15px rgba(255,255,255,0.7)"}),
                    rx.spacer(),
                    rx.badge(f"⭐ {m['vote_average']}", color_scheme="yellow", variant="solid")
                ),
                rx.text(m["overview"], size="2", color="white", line_clamp=5, 
                        style={"text_shadow": "1px 1px 10px rgba(0,0,0,0.9)", "font_weight": "500"}),
                rx.hstack(
                    rx.button(rx.cond(MovieState.watched_ids.contains(m["id"].to_string()), rx.icon(tag="circle-check", color="#00ff00"), rx.icon(tag="circle")), "Vizionat", size="1", variant="ghost", color="white", on_click=lambda: MovieState.toggle_status(m, "watched")),
                    rx.button(rx.cond(MovieState.watchlist_ids.contains(m["id"].to_string()), rx.icon(tag="bookmark-check", color="#00d4ff"), rx.icon(tag="bookmark")), "Later", size="1", variant="ghost", color="white", on_click=lambda: MovieState.toggle_status(m, "watchlist")),
                    spacing="4", width="100%", padding_top="10px"
                ),
                rx.button("VEZI TRAILER", rx.icon(tag="play"), width="100%", size="3", color_scheme="ruby", on_click=lambda: MovieState.load_trailer(m["id"]), margin_top="15px"),
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

# --- SIDEBAR COMPLET ---
def sidebar():
    return rx.vstack(
        # Header + Reset
        rx.hstack(
            rx.vstack(
                rx.text("MOVIE", style={"font_size": "28px", "font_weight": "bold", "color": "#e11d48", "line_height": "0.8"}),
                rx.text("_db pro", style={"font_size": "14px", "color": "white", "letter_spacing": "6px"}),
                spacing="0"
            ),
            rx.spacer(),
            rx.button(
                rx.icon("rotate-ccw", size=16), "Reset", 
                size="1", variant="soft", color_scheme="gray", 
                on_click=MovieState.reset_filters
            ),
            width="100%", margin_bottom="20px", align_items="center"
        ),

        # Meniu Navigare
        rx.grid(
            rx.button("Explore", variant=rx.cond(MovieState.show_mode == "Discover", "solid", "surface"), on_click=lambda: MovieState.set_show_mode("Discover"), size="2"),
            rx.button("Watchlist", variant=rx.cond(MovieState.show_mode == "watchlist", "solid", "surface"), on_click=lambda: MovieState.set_show_mode("watchlist"), size="2"),
            rx.button("Watched", variant=rx.cond(MovieState.show_mode == "watched", "solid", "surface"), on_click=lambda: MovieState.set_show_mode("watched"), size="2"),
            columns="3", spacing="2", width="100%", margin_bottom="10px"
        ),
        rx.divider(margin_bottom="10px", opacity="0.3"),

        # ZONA FILTRE (Vizibilă doar pe Explore)
        rx.cond(
            MovieState.show_mode == "Discover",
            rx.vstack(
                # 1. Tip Producție
                rx.text("TIP PRODUCȚIE", size="1", weight="bold", color="#888", margin_top="10px"),
                rx.segmented_control.root(
                    rx.segmented_control.item("Filme", value="movie"),
                    rx.segmented_control.item("Seriale", value="tv"),
                    value=MovieState.content_type,
                    on_change=MovieState.set_content_type,
                    width="100%",
                ),

                # 2. Slidere (Ani & Rating)
                rx.box(
                    rx.text(f"Ani: {MovieState.year_range[0]} - {MovieState.year_range[1]}", size="1", weight="bold", color="#ccc"),
                    rx.range_slider(
                        default_value=[1990, 2026], min=1950, max=2026, step=1,
                        on_value_commit=MovieState.set_year_range,
                        width="100%", margin_top="5px"
                    ),
                    margin_top="20px", width="100%"
                ),
                rx.box(
                    rx.text(f"Rating: {MovieState.rate_range[0]} - {MovieState.rate_range[1]}", size="1", weight="bold", color="#ccc"),
                    rx.range_slider(
                        default_value=[5, 10], min=0, max=10, step=0.5,
                        on_value_commit=MovieState.set_rate_range,
                        width="100%", margin_top="5px"
                    ),
                    margin_top="15px", width="100%"
                ),

                # 3. Actori (Input + Tags)
                rx.box(
                    rx.text("ACTORI", size="1", weight="bold", color="#888", margin_top="20px", margin_bottom="5px"),
                    rx.hstack(
                        rx.input(
                            value=MovieState.actor_input, 
                            placeholder="Ex: Brad Pitt", 
                            on_change=MovieState.set_actor_input,
                            size="1", radius="full", flex="1"
                        ),
                        rx.button(rx.icon("plus"), size="1", radius="full", on_click=MovieState.add_actor),
                        width="100%"
                    ),
                    rx.flex(
                        rx.foreach(
                            MovieState.selected_actors,
                            lambda tag: rx.badge(tag, rx.icon("x", size=12, on_click=lambda: MovieState.remove_actor(tag)), variant="solid", color_scheme="ruby", padding="5px", margin="2px")
                        ),
                        wrap="wrap", margin_top="10px"
                    ),
                    width="100%"
                ),

                # 4. Acordeon Categorii (Genuri + Studiouri)
                rx.accordion.root(
                    rx.accordion.item(
                        rx.accordion.header("GENURI"),
                        rx.accordion.content(
                            rx.flex(
                                rx.foreach(
                                    MovieState.GENRES_LIST,
                                    lambda g: rx.badge(
                                        g, 
                                        variant=rx.cond(MovieState.selected_genres.contains(MovieState.GENRE_MAP[g]), "solid", "outline"),
                                        color_scheme=rx.cond(MovieState.selected_genres.contains(MovieState.GENRE_MAP[g]), "ruby", "gray"),
                                        on_click=lambda: MovieState.toggle_genre(g),
                                        cursor="pointer", margin="2px"
                                    )
                                ),
                                wrap="wrap"
                            )
                        )
                    ),
                    rx.accordion.item(
                        rx.accordion.header("STUDIOURI"),
                        rx.accordion.content(
                            rx.vstack(
                                rx.text("România 🇷🇴", size="1", weight="bold"),
                                rx.flex(rx.foreach(MovieState.studios_ro, lambda s: rx.checkbox(s, on_change=lambda _: MovieState.toggle_studio(s), size="1", margin_right="10px")), wrap="wrap"),
                                
                                rx.text("SUA - Principale 🇺🇸", size="1", weight="bold", margin_top="10px"),
                                rx.flex(rx.foreach(MovieState.studios_us, lambda s: rx.checkbox(s, on_change=lambda _: MovieState.toggle_studio(s), size="1", margin_right="10px")), wrap="wrap"),

                                rx.text("Europa 🇪🇺", size="1", weight="bold", margin_top="10px"),
                                rx.flex(rx.foreach(MovieState.studios_eu, lambda s: rx.checkbox(s, on_change=lambda _: MovieState.toggle_studio(s), size="1", margin_right="10px")), wrap="wrap"),

                                rx.text("Independente 🎬", size="1", weight="bold", margin_top="10px"),
                                rx.flex(rx.foreach(MovieState.studios_indie, lambda s: rx.checkbox(s, on_change=lambda _: MovieState.toggle_studio(s), size="1", margin_right="10px")), wrap="wrap"),
                                spacing="2"
                            )
                        )
                    ),
                    width="100%", variant="ghost", margin_top="10px"
                ),
                
                # Buton Aplicare
                rx.button(
                    "APLICĂ FILTRELE", 
                    width="100%", size="3", margin_top="30px", 
                    color_scheme="ruby", variant="solid",
                    on_click=MovieState.fetch_movies
                ),
                width="100%", align_items="start"
            )
        ),
        
        width="350px", height="100vh", padding="20px", 
        background="rgba(20,20,20,0.95)", border_right="1px solid #333",
        position="fixed", left="0", top="0", overflow_y="auto", z_index="50"
    )

# --- PAGINA PRINCIPALĂ ---
def index():
    return rx.box(
        rx.flex(
            sidebar(),
            rx.box(
                rx.cond(
                    MovieState.is_loading, 
                    rx.center(rx.spinner(color="red", size="3"), width="100%", height="80vh"),
                    rx.grid(
                        rx.foreach(MovieState.movies, movie_card), 
                        columns=rx.breakpoints(initial="1", sm="2", md="2", lg="3", xl="4"), 
                        spacing="6", 
                        width="100%"
                    )
                ), 
                flex="1", 
                margin_left="350px", 
                padding="4em"
            ), 
            min_height="100vh"
        ),
        rx.html("<style>@keyframes bgMove { 0% {background-position: 0% 50%;} 100% {background-position: 100% 50%;} }</style>"),
        style={
            "background": "radial-gradient(circle, #2a0000 0%, #000000 100%)",
            "background_size": "200% 200%",
            "animation": "bgMove 15s ease infinite alternate",
        }
    )

app = rx.App(theme=rx.theme(appearance="dark", accent_color="ruby"))
app.add_page(index, on_load=MovieState.fetch_movies)