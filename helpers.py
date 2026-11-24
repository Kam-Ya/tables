import gspread

def getTickets(val):
    try:
        return int(val)
    except (ValueError, TypeError):
        return 0

def isPaid(val):
    return str(val).strip().lower() in ("yes", "y", "true", "paid")

def getSeats(value):
    return [s.strip() for s in str(value).split(",") if s.strip()]

def find_user(email, rows):
    email = email.strip().lower()
    for rowNum, row in enumerate(rows, start=2):
        if str(row["Email"]).strip().lower() == email:
            return {
                    "row": rowNum,
                    "email": row["Email"],
                    "tickets": getTickets(row["Number of Tickets"]),
                    "paid": isPaid(row["Paid"]),
                    "seats": getSeats(row["Seats"]),
                    }
    return None
