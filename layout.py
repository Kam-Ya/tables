DEFAULT_SEATS = 10   # seats per table unless overridden below

# Seats per table, only for tables that differ from the default
SEATS_OVERRIDE = {
    # 5: 8,
}

# Table number: (x, y) centre position, measured in pixels on your floor plan image
POSITIONS = {
    1: (50, 628),  2: (127, 628), 3: (213, 626), 4: (297, 628), 5: (391, 629),
    6: (116, 556), 7: (194, 559), 8: (293, 556), 9: (393, 553),
    13: (59, 488), 12: (147, 490), 11: (229, 493), 10: (317, 489),
    18: (52, 416), 17: (132, 421), 14: (209, 419),
    20: (51, 353), 19: (129, 352), 15: (204, 350),
    22: (53, 276), 21: (132, 271), 16: (201, 277),
    23: (52, 203), 24: (135, 194), 25: (215, 188), 26: (301, 189), 27: (384, 187),
    31: (91, 123), 30: (164, 121), 29: (243, 122), 28: (328, 123),
    35: (51, 50),  34: (125, 52), 33: (200, 54), 32: (276, 55),
}

# Non-seating things to draw (stage, DJ, etc.): x, y, width, height in the same units
FEATURES = [
    {"label": "Stage",  "x": 255, "y": 267, "w": 195, "h": 185, "color": "#8c8a4d"},
    {"label": "DJ",     "x": 472, "y": 278, "w": 58,  "h": 140, "color": "#e11"},
]

FLOOR_WIDTH = 536
FLOOR_HEIGHT = 690


def get_tables():
    return [
        {"number": n, "x": x, "y": y, "seats": SEATS_OVERRIDE.get(n, DEFAULT_SEATS)}
        for n, (x, y) in sorted(POSITIONS.items())
    ]

def valid_seat_ids():
    return {
        f"T{t['number']}-S{s}"
        for t in get_tables()
        for s in range(1, t["seats"] + 1)
    }
