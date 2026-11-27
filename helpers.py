import gspread

EMAIL_COL = "Email"
TICKETS_COL = "Number of Tickets"
SEATS_COL = "Seats"

def getTickets(val):
    try:
        return int(val)
    except (ValueError, TypeError):
        return 0


def getSeats(value):
    return [s.strip() for s in str(value).split(",") if s.strip()]

def find_user(email, rows):
    email = email.strip().lower()
    for rowNum, row in enumerate(rows, start=2):
        if str(row[EMAIL_COL]).strip().lower() == email:
            return {
                    "row": rowNum,
                    "email": row[EMAIL_COL],
                    "tickets": getTickets(row[TICKETS_COL]),
                    "seats": getSeats(row[SEATS_COL]),
                    }
    return None

def parse_seats(value):
    return [s.strip() for s in str(value).split(",") if s.strip()]

def taken_by_others(email, rows):
    """Return the set of seat IDs booked by everyone except this email."""
    email = email.strip().lower()
    taken = set()
    for record in rows:
        if str(record[EMAIL_COL]).strip().lower() != email:
            taken.update(parse_seats(record[SEATS_COL]))
    return taken
