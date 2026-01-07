import reflex as rx
from .state import UserState, MovieState
from .login_view import login_page

def main_app():
    """Aici pui layout-ul tău existent (Sidebar + Grid)."""
    return rx.hstack(
        # sidebar(),
        # movie_grid(),
        rx.text("Bine ai venit în aplicație!"),
        rx.button("Logout", on_click=UserState.logout)
    )

@rx.page(route="/")
def index():
    # PUNCTUL 4: Condiția de afișare
    return rx.cond(
        UserState.is_logged_in,
        main_app(),
        login_page()
    )

app = rx.App()