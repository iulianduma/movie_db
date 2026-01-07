import reflex as rx
from .state import UserState

def login_page():
    return rx.center(
        rx.vstack(
            rx.heading("MOVIE_DB", style={"color": "#ff0000", "font_size": "48px", "font_weight": "900"}),
            rx.text("Acces restricționat. Vă rugăm să vă autentificați."),
            rx.input(placeholder="Utilizator", on_change=UserState.set_username, width="100%"),
            rx.input(placeholder="Parolă", type="password", on_change=UserState.set_password, width="100%"),
            rx.button("LOG IN", on_click=UserState.login, width="100%", color_scheme="ruby"),
            spacing="4",
            padding="40px",
            background="rgba(20, 20, 20, 0.9)",
            border="1px solid #333",
            border_radius="15px",
            backdrop_filter="blur(10px)",
        ),
        height="100vh",
        background="black",
    )