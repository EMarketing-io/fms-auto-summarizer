# 📦 Standard Library
import os

# 🌐 Load environment variables from .env file into the environment
from dotenv import load_dotenv

# 🔐 Load all environment variables at runtime
load_dotenv()

# 🔑 OpenAI API key — used for Whisper and GPT calls
OPENAI_KEY = os.getenv("OPENAI_KEY")

# 🔑 Google Drive API key — optional for certain unauthenticated requests (like file search)
GDRIVE_API_KEY = os.getenv("GDRIVE_API_KEY")

# 📁 Folder ID in Google Drive where processed audio summaries should be uploaded
AUDIO_DRIVE_FOLDER_ID = os.getenv("AUDIO_DRIVE_FOLDER_ID")