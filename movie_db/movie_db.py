import reflex as rx
from .state import MovieState

def movie_card(m: rx.Var[dict]):
    return rx.box(
        # Imaginea pe tot cardul - mărită la 600px
        rx.image(
            src=m["poster_path"], 
            width="100%", 
            height="600px", 
            object_fit="cover", 
            border_radius="15px"
        ),
        
        # Overlay Cinematic
        rx.vstack(
            rx.spacer(),
            rx.vstack(
                rx.hstack(
                    rx.heading(
                        m["title"], 
                        size="6", 
                        weight="bold", 
                        color="white", 
                        style={
                            "text_shadow": "0px 0px 15px rgba(255,255,255,0.4), 0px 0px 5px rgba(0,0,0,0.8)",
                            "letter_spacing": "0.5px"
                        }
                    ),
                    rx.spacer(),
                    rx.badge(f"⭐ {m['vote_average']}", color_scheme="yellow", variant="solid")
                ),
                
                # Text alb cu glow și antialiasing îmbunătățit
                rx.text(
                    m["overview"], 
                    size="2", 
                    color="white", 
                    line_clamp=5, # Mai mult spațiu pentru descriere
                    style={
                        "text_shadow": "1px 1px 10px rgba(0,0,0,0.9)",
                        "font_weight": "500",
                        "opacity": "0.95",
                        "line_height": "1.4"
                    }
                ),
                
                # Checkbox-uri sub formă de butoane moderne
                rx.hstack(
                    rx.button(
                        rx.cond(MovieState.watched_ids.contains(m["id"].to_string()), rx.icon(tag="check-circle", color="#00ff00"), rx.icon(tag="circle")),
                        "Vizionat", 
                        size="1", 
                        variant="ghost", 
                        color="white",
                        on_click=lambda: MovieState.toggle_status(m, "watched"),
                        style={"_hover": {"background": "rgba(255,255,255,0.1)"}}
                    ),
                    rx.button(
                        rx.cond(MovieState.watchlist_ids.contains(m["id"].to_string()), rx.icon(tag="bookmark-check", color="#00d4ff"), rx.icon(tag="bookmark")),
                        "Later", 
                        size="1", 
                        variant="ghost", 
                        color="white",
                        on_click=lambda: MovieState.toggle_status(m, "watchlist"),
                        style={"_hover": {"background": "rgba(255,255,255,0.1)"}}
                    ),
                    spacing="4", width="100%", padding_top="15px"
                ),
                
                # Buton Trailer
                rx.button(
                    "TRAILER", 
                    rx.icon(tag="play"), 
                    width="100%", 
                    size="3", 
                    color_scheme="ruby",
                    on_click=lambda: MovieState.load_trailer(m["id"]), 
                    margin_top="15px",
                    style={"box_shadow": "0 0 20px rgba(225, 29, 72, 0.4)"}
                ),
                
                padding="30px",
                # Gradient mai dens la bază pentru a susține textul lung
                background="linear-gradient(to top, rgba(0,0,0,1) 0%, rgba(0,0,0,0.85) 60%, rgba(0,0,0,0) 100%)",
                border_radius="0 0 15px 15px", 
                width="100%"
            ),
            width="100%", 
            height="100%", 
            position="absolute", 
            top="0", 
            left="0"
        ),
        
        # Overlay Video
        rx.cond(
            (m["yt_id"] != "") & (m["yt_id"] != "none"),
            rx.box(
                rx.html(f"<iframe width='100%' height='100%' src='https://www.youtube.com/embed/{m['yt_id']}?autoplay=1' frameborder='0' allowfullscreen style='border-radius: 15px;'></iframe>"),
                position="absolute", top="0", left="0", width="100%", height="100%", background="black", border_radius="15px", z_index="10"
            )
        ),
        
        position="relative", 
        width="100%", 
        height="600px", 
        border_radius="15px", 
        overflow="hidden", 
        border="1px solid #222",
        style={
            "transition": "transform 0.3s ease, box-shadow 0.3s ease",
            "_hover": {
                "transform": "scale(1.02)",
                "box_shadow": "0 10px 30px rgba(0,0,0,0.5)",
                "border": "1px solid #444"
            }
        }
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
                    # Am redus numărul de coloane pe ecrane mari pentru a nu înghesui cardurile lungi
                    columns=rx.breakpoints(initial="1", sm="2", md="2", lg="3", xl="4"), 
                    spacing="6", 
                    width="100%"
                )
            ), 
            flex="1", 
            margin_left="300px", 
            padding="4em"
        ), 
        background="#000", 
        min_height="100vh"
    )

# Restul codului (sidebar, app configuration) rămâne neschimbat.