# 📦 Standard Libraries
import os
import pickle

# 🌐 Third-Party Libraries
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload

# 🔐 Load environment variables from .env
load_dotenv()

# 🌐 OAuth credentials and Drive target folder configuration
CREDENTIALS_PATH = os.getenv("GOOGLE_OAUTH_FILE")               # Path to OAuth client secrets
TOKEN_PATH = os.getenv("GOOGLE_TOKEN_FILE")                     # Path to store/load user session token
FOLDER_ID = os.getenv("WEBSITE_DRIVE_FOLDER_ID")                # Destination Drive folder for uploads
CLIENT_SECRETS_FILE = CREDENTIALS_PATH                          # Redundant but kept for clarity
SCOPES = ["https://www.googleapis.com/auth/drive.file"]         # Scope for file upload access


# 🔐 Authenticate and return a Google Drive API client using OAuth 2.0
def authenticate_google_drive():
    creds = None

    # ✅ Load previously saved token (if available and valid)
    if TOKEN_PATH and os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "rb") as token:
            creds = pickle.load(token)

    # 🔄 Refresh or prompt user login if token is missing or invalid
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        
        else:
            if not CREDENTIALS_PATH:
                raise ValueError("⚠️ GOOGLE_OAUTH_FILE not set in .env")
            
            # Launch browser-based login flow
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

        # 💾 Save new token for future use
        if TOKEN_PATH:
            with open(TOKEN_PATH, "wb") as token:
                pickle.dump(creds, token)

    # 📡 Return an authorized Drive client
    return build("drive", "v3", credentials=creds)


# 📤 Upload a DOCX file (in memory) to the configured Google Drive folder
def upload_docx_to_gdrive(docx_stream, filename):
    service = authenticate_google_drive()   # Ensure authenticated session

    # 📄 Metadata for the file to be created in Drive
    file_metadata = {
        "name": filename,
        "parents": [FOLDER_ID],
        "mimeType": "application/vnd.google-apps.document",     # Create as a Google Doc
    }

    docx_stream.seek(0)
    docx_content = docx_stream.read()

    # 🗃️ Prepare the file content for upload
    media = MediaInMemoryUpload(
        docx_content,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        resumable=True,
    )

    # 🚀 Upload the file and return its ID
    uploaded = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id, name")
        .execute()
    )

    print(f"Uploaded to Google Drive as: {uploaded['name']} (ID: {uploaded['id']})")
    return uploaded["id"]