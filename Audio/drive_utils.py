# Standard Libraries
import os
import io
import pickle
import tempfile

# Third-Party Libraries
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

# Load environment variables
load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials.json") # Path to Google Service Account Credentials JSON file
TOKEN_PATH = os.path.join(BASE_DIR, "token.pickle") # Path to store OAuth token


# Function to authenticate with OAuth2
def authenticate_with_oauth():
    SCOPES = ["https://www.googleapis.com/auth/drive.file"]
    creds = None

    # Load existing token if available
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "rb") as token:
            creds = pickle.load(token)

    # If no valid credentials, prompt for login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(TOKEN_PATH, "wb") as token:
            pickle.dump(creds, token)

    return build("drive", "v3", credentials=creds)


# Function to get Google Drive service
def get_drive_service(api_key=None):
    if api_key:
        print("🔐 Using API Key authentication")
        return build("drive", "v3", developerKey=api_key)
    else:
        print("🔐 Using OAuth authentication")
        return authenticate_with_oauth()


# Function to download audio file from Google Drive
def download_audio_from_drive(file_id, api_key=None):
    service = get_drive_service(api_key)
    request = service.files().get_media(fileId=file_id)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".m4a")
    downloader = MediaIoBaseDownload(temp_file, request)
    done = False
    
    # Download the audio file in chunks
    while not done:
        status, done = downloader.next_chunk()
        print(f"Downloading audio: {int(status.progress() * 100)}%")

    temp_file.close()
    return temp_file.name


# Function to upload a DOCX file to Google Drive
def upload_file_to_drive_in_memory(file_data, folder_id, api_key=None, final_name="Zoom Call Notes.docx"):
    service = get_drive_service(api_key)
    file_metadata = {"name": final_name, "parents": [folder_id]}
    file_stream = io.BytesIO(file_data)
    
    # Set the MIME type for DOCX files
    media = MediaIoBaseUpload(
        file_stream,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        resumable=True,
    )

    # Create the file in Google Drive
    file = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id")
        .execute()
    )

    print(f"📤 File uploaded: {file.get('id')}")
    return file.get("id")


# Function to find an audio file in a specific Google Drive folder
def find_audio_file_in_folder(folder_id, extension=".m4a", api_key=None):
    service = get_drive_service(api_key)
    query = f"'{folder_id}' in parents"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])

    # Check for files with the specified extension
    for file in files:
        if file["name"].lower().endswith(extension):
            print(f"🎯 Found audio file: {file['name']}")
            return file["id"]

    print("⚠️ No .m4a file found in folder.")
    return None


def find_folder_id_by_partial_name(company_name, parent_folder_id, api_key=None):
    service = get_drive_service(api_key)
    query = f"mimeType='application/vnd.google-apps.folder' and '{parent_folder_id}' in parents"
    response = service.files().list(q=query, fields="files(id, name)").execute()
    folders = response.get("files", [])
    company_keywords = company_name.lower().split()

    # Check if any folder name contains the company name keywords
    for folder in folders:
        folder_name = folder["name"].lower()
        if any(keyword in folder_name for keyword in company_keywords):
            print(f"📁 Matched folder: {folder['name']}")
            return folder["id"]

    print(f"❌ No folder matched any part of: {company_name}")
    return None