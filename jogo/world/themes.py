"""Paletas de cor de cada bioma."""

THEMES = {
    "campo": dict(
        sky=((110, 185, 255), (255, 222, 175)),
        dirt=(150, 95, 55), dirt_dark=(115, 70, 40), dirt_light=(180, 125, 75),
        top=(85, 185, 70), top_light=(150, 225, 95), top_dark=(50, 130, 50),
        brick=(205, 125, 65), brick_line=(120, 65, 30),
        chest=(235, 175, 45), chest_dark=(150, 95, 20),
        plank=(175, 125, 75), plank_top=(215, 165, 95),
        spike=(215, 215, 225), liquid=(60, 140, 230), liquid_top=(150, 210, 255),
        platform=(175, 120, 70),
    ),
    "caverna": dict(
        sky=((25, 18, 45), (60, 40, 85)),
        dirt=(75, 65, 95), dirt_dark=(50, 42, 70), dirt_light=(100, 90, 125),
        top=(90, 200, 190), top_light=(170, 255, 240), top_dark=(50, 130, 140),
        brick=(120, 105, 140), brick_line=(60, 50, 80),
        chest=(170, 140, 230), chest_dark=(90, 70, 150),
        plank=(110, 95, 130), plank_top=(150, 135, 175),
        spike=(190, 230, 255), liquid=(50, 100, 200), liquid_top=(130, 180, 255),
        platform=(120, 105, 150),
    ),
    "vulcao": dict(
        sky=((60, 15, 20), (200, 80, 40)),
        dirt=(70, 50, 50), dirt_dark=(45, 32, 32), dirt_light=(95, 70, 65),
        top=(55, 45, 45), top_light=(255, 130, 50), top_dark=(30, 25, 25),
        brick=(110, 60, 45), brick_line=(50, 25, 20),
        chest=(230, 120, 50), chest_dark=(130, 50, 20),
        plank=(90, 70, 65), plank_top=(130, 100, 90),
        spike=(200, 180, 170), liquid=(240, 80, 20), liquid_top=(255, 200, 70),
        platform=(110, 80, 70),
    ),
}
