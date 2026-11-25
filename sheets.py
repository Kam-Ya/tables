import os
import gspread
from dotenv import load_dotenv
import helpers

load_dotenv()

gc = gspread.service_account(filename=os.environ["GOOGLE_CREDS"])
sheet = gc.open_by_key(os.environ["SHEET"]).sheet1

def getRows():
    return sheet.get_all_records()
