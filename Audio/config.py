import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_KEY = os.getenv("OPENAI_KEY") # OpenAI API Key
GDRIVE_API_KEY = os.getenv("GDRIVE_API_KEY") # Google Drive API Key
AUDIO_DRIVE_FOLDER_ID = os.getenv("AUDIO_DRIVE_FOLDER_ID") # Google Drive Folder ID