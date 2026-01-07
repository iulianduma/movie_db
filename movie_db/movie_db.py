def movie_card(m: rx.Var[dict]):
    return rx.card(
        rx.vstack(
            rx.box(
                rx.image(
                    src="https://image.tmdb.org/t/p/w500" + m["poster_path"].to_string(),
                    width="100%", height="220px", object_fit="cover"
                ),
                # Buton de Play plutitor pentru trailere
                rx.center(
                    rx.icon(tag="play", size=30, color="white"),
                    position="absolute", top="0", left="0", width="100%", height="100%",
                    background="rgba(0,0,0,0.3)", opacity="0", transition="0.3s",
                    _hover={"opacity": "1", "cursor": "pointer"},
                    on_click=lambda: MovieState.load_trailer(m["id"])
                ),
                position="relative"
            ),
            # Restul detaliilor ...
        ),
        # Design adaptiv: cardul ocupă 100% din coloana grid-ului
        width="100%", 
        style={"background": "rgba(20, 20, 20, 0.8)", "backdrop-filter": "blur(10px)"}
    )

def main_layout():
    return rx.box(
        rx.grid(
            rx.foreach(MovieState.movies, movie_card),
            # Telefon: 1 col, Tabletă: 2 col, PC: 3+ col
            columns=rx.breakpoints(initial="1", sm="2", md="3", lg="4"),
            spacing="6",
            width="100%"
        ),
        padding=rx.breakpoints(initial="2em", md="5em")
    )