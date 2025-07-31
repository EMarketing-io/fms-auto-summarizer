import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") # OpenAI API Key
GOOGLE_DRIVE_API_KEY = os.getenv("GOOGLE_DRIVE_API_KEY") # Google Drive API Key
GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID") # Google Drive Folder ID