# Standard Libraries
import os
import pickle

# Third-Party Libraries
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload

# Load environment variables
load_dotenv()

CREDENTIALS_PATH = os.getenv("GOOGLE_OAUTH_FILE")
TOKEN_PATH = os.getenv("GOOGLE_TOKEN_FILE")
FOLDER_ID = os.getenv("WEBSITE_DRIVE_FOLDER_ID")  # Google Drive Folder ID
CLIENT_SECRETS_FILE = os.getenv(
    "GOOGLE_OAUTH_FILE"
)  # Path to Google Service Account Credentials JSON file
SCOPES = [
    "https://www.googleapis.com/auth/drive.file"
]  # Scope for file operations in Google Drive


# Function to authenticate with Google Drive using OAuth2
def authenticate_google_drive():
    creds = None

    # Load existing token if available
    if TOKEN_PATH and os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "rb") as token:
            creds = pickle.load(token)

    # If no valid credentials, prompt for login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_PATH:
                raise ValueError("⚠️ GOOGLE_OAUTH_FILE not set in .env")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save token for reuse
        if TOKEN_PATH:
            with open(TOKEN_PATH, "wb") as token:
                pickle.dump(creds, token)

    # Build and return Drive service
    return build("drive", "v3", credentials=creds)


# Function to upload a DOCX file to Google Drive
def upload_docx_to_gdrive(docx_stream, filename):
    service = authenticate_google_drive()

    # Prepare the file metadata
    file_metadata = {
        "name": filename,
        "parents": [FOLDER_ID],
        "mimeType": "application/vnd.google-apps.document",
    }

    docx_stream.seek(0)
    docx_content = docx_stream.read()

    # Create a MediaInMemoryUpload object
    media = MediaInMemoryUpload(
        docx_content,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        resumable=True,
    )

    # Upload the file to Google Drive
    uploaded = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id, name")
        .execute()
    )

    print(f"Uploaded to Google Drive as: {uploaded['name']} (ID: {uploaded['id']})")
    return uploaded["id"]
