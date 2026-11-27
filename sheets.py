import os
import gspread
from dotenv import load_dotenv
import time
import layout
import helpers

load_dotenv()

gc = gspread.service_account(filename=os.environ["GOOGLE_CREDS"])
sheet = gc.open_by_key(os.environ["SHEET"]).sheet1

_cache = {"time": 0, "rows": []}
CACHE_SECONDS = 5


def getRows(fresh=False):
    if fresh or time.time() - _cache["time"] > CACHE_SECONDS:
        _cache["rows"] = sheet.get_all_records()
        _cache["time"] = time.time()
    return _cache["rows"]

def saveSeats(row_number, seats):
    headers = sheet.row_values(1)
    col = headers.index(helpers.SEATS_COL) + 1
    sheet.update_cell(row_number, col, ", ".join(seats))
    _cache["time"] = 0  # force the next read to refetch
