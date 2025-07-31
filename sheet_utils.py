import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

load_dotenv()

SHEET_ID = os.getenv("GOOGLE_SHEET") # Google Sheet ID
CREDENTIALS_PATH = os.getenv("GOOGLE_SERVICE_ACCOUNT") # Path to Google Service Account Credentials JSON file


# Function to get all rows from the Google Sheet
def get_pending_rows():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    # Authenticate with Google Sheets API
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_PATH, scope)
    client = gspread.authorize(creds)
    
    # Open the Google Sheet and get all records
    sheet = client.open_by_key(SHEET_ID).sheet1
    records = sheet.get_all_values()

    # Filter rows that have both website and audio links, and are not marked as "Done"
    pending = []
    for idx, row in enumerate(records[1:], start=2):
        website = row[4].strip() if len(row) >= 5 else ""
        audio = row[5].strip() if len(row) >= 6 else ""
        status = row[8].strip().lower() if len(row) >= 9 else ""

        # Check if both website and audio links are present and status is not "done"
        if website and audio and status != "done":
            pending.append((idx, website, audio))

    return pending


# Function to update the Google Sheet with meeting and website links
def update_sheet_with_links( row_index, meeting_url=None, meeting_name=None, website_url=None, website_name=None):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_PATH, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).sheet1
    wrote_something = False
    
    # Update the Google Sheet with hyperlinks
    if meeting_url and meeting_name:
        formula = f'=HYPERLINK("{meeting_url}", "{meeting_name}")'
        sheet.update_cell(row_index, 7, formula)
        wrote_something = True
    
    # Update website link if provided
    if website_url and website_name:
        formula = f'=HYPERLINK("{website_url}", "{website_name}")'
        sheet.update_cell(row_index, 8, formula)
        wrote_something = True
    
    # Update status to "Done" if any link was written
    if wrote_something:
        sheet.update_cell(row_index, 9, "Done")