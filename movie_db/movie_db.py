import reflex as rx
from .state import UserState, MovieState, FilterState
from .login_view import login_page

def movie_card(m: rx.Var[dict]):
    return rx.card(
        rx.vstack(
            rx.box(
                rx.cond(
                    m["yt_id"] != "",
                    # Am înlocuit rx.format cu concatenare simplă
                    rx.html(
                        "<iframe width='100%' height='220' src='https://www.youtube.com/embed/" 
                        + m["yt_id"].to_string() 
                        + "?autoplay=1' frameborder='0' allowfullscreen style='border-radius: 12px 12px 0 0;'></iframe>"
                    ),
                    rx.box(
                        rx.image(
                            src="https://image.tmdb.org/t/p/w500" + m["poster_path"].to_string(),
                            width="100%", height="220px", object_fit="cover", border_radius="12px 12px 0 0"
                        ),
                        rx.center(
                            rx.button(
                                rx.icon(tag="play", size=30),
                                on_click=lambda: MovieState.load_trailer(m["id"]),
                                variant="ghost", color_scheme="gray"
                            ),
                            position="absolute", top="0", left="0", width="100%", height="220px", background="rgba(0,0,0,0.4)", border_radius="12px 12px 0 0"
                        ),
                        position="relative"
                    )
                ), width="100%"
            ),
            rx.vstack(
                rx.hstack(
                    rx.heading(m["title"], size="4", weight="bold", line_clamp=1, flex="1", color="white"),
                    rx.vstack(
                        rx.hstack(
                            rx.text("Văzut", size="1", color="#aaa"),
                            rx.checkbox(
                                checked=MovieState.watched_ids.contains(m["id"].to_string()),
                                on_change=lambda _: MovieState.toggle_movie(m, "watched"),
                                color_scheme="ruby"
                            )
                        ),
                        rx.hstack(
                            rx.text("Later", size="1", color="#aaa"),
                            rx.checkbox(
                                checked=MovieState.watchlist_ids.contains(m["id"].to_string()),
                                on_change=lambda _: MovieState.toggle_movie(m, "watchlist"),
                                color_scheme="blue"
                            )
                        ),
                        spacing="1", align_items="end"
                    ), width="100%"
                ),
                rx.badge("⭐ " + m["vote_average"].to_string(), color_scheme="yellow", variant="soft"),
                rx.text(m["overview"], style={"font_size": "10px", "color": "#888"}, line_clamp=3),
                padding="15px", spacing="3", width="100%"
            )
        ),
        padding="0", background_color="#0d0d0d", border="1px solid #1a1a1a", border_radius="12px"
    )

def sidebar():
    return rx.vstack(
        rx.heading("MOVIE_DB", style={"color": "#ff0000", "font_size": "32px", "font_weight": "900"}),
        rx.divider(alpha=0.1),
        rx.vstack(
            rx.button("DISCOVER", on_click=lambda: [FilterState.set_show_mode("Discover"), MovieState.fetch_movies()], variant="soft", width="100%"),
            rx.button("WATCHLIST", on_click=lambda: [FilterState.set_show_mode("Watchlist"), MovieState.fetch_movies()], variant="ghost", width="100%"),
            rx.button("WATCHED", on_click=lambda: [FilterState.set_show_mode("Watched"), MovieState.fetch_movies()], variant="ghost", width="100%"),
            color_scheme="ruby", spacing="2", width="100%"
        ),
        rx.text("ANI PRODUCȚIE", weight="bold", size="1", color="#555", margin_top="1.5em"),
        rx.hstack(
            rx.input(placeholder="Din", on_blur=FilterState.set_y_start, width="100%"),
            rx.input(placeholder="La", on_blur=FilterState.set_y_end, width="100%"),
        ),
        rx.spacer(),
        rx.button("LOGOUT", on_click=UserState.logout, variant="outline", width="100%"),
        width="320px", height="100vh", padding="30px", background="#0a0a0a", position="fixed", left="0", border_right="1px solid #222"
    )

def main_layout():
    return rx.flex(
        sidebar(),
        rx.box(
            rx.cond(
                MovieState.is_loading,
                rx.center(rx.spinner(color="#ff0000", size="3"), width="100%", padding="5em"),
                rx.grid(
                    rx.foreach(MovieState.movies, movie_card),
                    columns=rx.breakpoints(initial="1", sm="2", lg="3"),
                    spacing="6", width="100%"
                )
            ),
            flex="1", margin_left="320px", padding="5em"
        ),
        background="black", min_height="100vh"
    )

@rx.page(route="/", on_load=MovieState.fetch_movies)
def index():
    return rx.cond(UserState.is_logged_in, main_layout(), login_page())

app = rx.App(theme=rx.theme(appearance="dark", accent_color="ruby"))