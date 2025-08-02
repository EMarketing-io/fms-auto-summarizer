# Standard Libraries
import os
# 📦 Standard Libraries
import os
import io
import pickle
import tempfile

# 🌐 Third-Party Libraries for Google Auth and Drive
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

# 🔐 Load environment variables from .env
load_dotenv()

# 🛠 OAuth2 credential and token paths (set via .env)
CREDENTIALS_PATH = os.getenv("GOOGLE_OAUTH_FILE")
TOKEN_PATH = os.getenv("GOOGLE_TOKEN_FILE")


# 🔐 Authenticate with Google Drive using OAuth2 credentials
def authenticate_with_oauth():
    SCOPES = ["https://www.googleapis.com/auth/drive.file"]
    creds = None

    # ✅ Load cached credentials (token.pickle) if they exist
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "rb") as token:
            creds = pickle.load(token)

    # 🔄 If credentials are missing or expired, refresh or re-authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        
        # Launch a browser-based login flow
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

        # 💾 Save the new token to disk
        with open(TOKEN_PATH, "wb") as token:
            pickle.dump(creds, token)

    # ✅ Return an authenticated Google Drive service object
    return build("drive", "v3", credentials=creds)


# 📡 Get Google Drive service, either via OAuth or API key (fallback)
def get_drive_service(api_key=None):
    if api_key:
        print("🔐 Using API Key authentication")
        return build("drive", "v3", developerKey=api_key)
    
    else:
        print("🔐 Using OAuth authentication")
        return authenticate_with_oauth()


# ⬇️ Download an audio file from Google Drive and store it temporarily
def download_audio_from_drive(file_id, api_key=None):
    service = get_drive_service(api_key)
    request = service.files().get_media(fileId=file_id)
    
    # Create a temporary local .m4a file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".m4a")
    downloader = MediaIoBaseDownload(temp_file, request)
    done = False

    # Stream the download in chunks
    while not done:
        status, done = downloader.next_chunk()
        print(f"Downloading audio: {int(status.progress() * 100)}%")

    temp_file.close()
    return temp_file.name


# 📤 Upload a DOCX file (from memory) to Google Drive
def upload_file_to_drive_in_memory(file_data, folder_id, api_key=None, final_name="Zoom Call Notes.docx"):
    service = get_drive_service(api_key)
    
    # Prepare file metadata (name + destination folder)
    file_metadata = {"name": final_name, "parents": [folder_id]}
    file_stream = io.BytesIO(file_data)

    # Define the media type for Word documents
    media = MediaIoBaseUpload(
        file_stream,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        resumable=True,
    )

    # Upload the file and get its ID
    file = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id")
        .execute()
    )

    print(f"📤 File uploaded: {file.get('id')}")
    return file.get("id")


# 🔍 Search for the first audio file in a specific Drive folder
def find_audio_file_in_folder(folder_id, extension=".m4a", api_key=None):
    service = get_drive_service(api_key)
    
    # Query all files in the target folder
    query = f"'{folder_id}' in parents"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])

    # Match file by extension
    for file in files:
        if file["name"].lower().endswith(extension):
            print(f"🎯 Found audio file: {file['name']}")
            return file["id"]

    print("⚠️ No .m4a file found in folder.")
    return None


# 🔍 Try to locate a folder based on company name keywords under a parent folder
def find_folder_id_by_partial_name(company_name, parent_folder_id, api_key=None):
    service = get_drive_service(api_key)
    
    # Search for subfolders under the parent folder
    query = f"mimeType='application/vnd.google-apps.folder' and '{parent_folder_id}' in parents"
    response = service.files().list(q=query, fields="files(id, name)").execute()
    folders = response.get("files", [])
    company_keywords = company_name.lower().split()

    # Match any folder whose name contains a keyword from the company name
    for folder in folders:
        folder_name = folder["name"].lower()
        if any(keyword in folder_name for keyword in company_keywords):
            print(f"📁 Matched folder: {folder['name']}")
            return folder["id"]

    print(f"❌ No folder matched any part of: {company_name}")
    return None