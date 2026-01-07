import reflex as rx
from .state import UserState

def login_page():
    return rx.center(
        rx.vstack(
            rx.heading("MOVIE_DB", color="red", size="9", weight="bold"),
            rx.text("Introduceți datele de acces", color="#888"),
            rx.input(placeholder="Utilizator", on_change=UserState.set_username, width="100%"),
            rx.input(placeholder="Parolă", type="password", on_change=UserState.set_password, width="100%"),
            rx.button("CONECTARE", on_click=UserState.login, width="100%", color_scheme="ruby"),
            spacing="4",
            padding="40px",
            background="#111",
            border="1px solid #333",
            border_radius="15px",
        ),
        height="100vh",
        background="black"
    )