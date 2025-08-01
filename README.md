# 📘 FMS Auto Summarizer

## 🔍 Overview

**FMS Auto Summarizer** automates the process of:

- Extracting and summarizing content from a company’s **website**
- Transcribing and summarizing **meeting audio**
- Generating polished **DOCX reports**
- Uploading reports to **Google Drive**
- Updating a centralized **Google Sheet** with links and status

This is ideal for agencies or teams who conduct regular client meetings and want automated documentation.

---

## 🏗️ Project Structure

```
fms-auto-summarizer/
├── audio/                     # Audio summarization logic
├── website/                   # Website summarization logic
├── utils/                     # Shared utilities
├── config/                    # Credential files & token
├── main.py                    # 🔁 Main script entrypoint
├── requirements.txt
├── .env
└── README.md
```

---

## ⚙️ Features

- 🔗 Google Sheets integration (for task queue and progress tracking)
- 🌐 Website analysis and summarization via GPT-4
- 🎙️ Audio transcription and summarization using OpenAI Whisper
- 📄 Automated DOCX report generation
- ☁️ Google Drive upload with hyperlinks back in the sheet
- 🛠 Fallbacks and error handling for missing folders or files

---

## 🛠️ Requirements

- Python 3.12.10
- Google Cloud Project with OAuth + Service Account credentials
- OpenAI API Key

---

## 🔑 Environment Setup (`.env`)

Create a `.env` file in your project root:

```env
# OpenAI
OPENAI_KEY=sk-...

# Google Auth
GOOGLE_SA_FILE=config/google_service_account.json
GOOGLE_OAUTH_FILE=config/google_oauth_credentials.json
GOOGLE_TOKEN_FILE=config/token.pickle

# Google Drive
AUDIO_PARENT_FOLDER_ID=your_parent_folder_id
AUDIO_DRIVE_FOLDER_ID=folder_id_for_audio_outputs
WEBSITE_DRIVE_FOLDER_ID=folder_id_for_website_outputs
GDRIVE_API_KEY=your_google_drive_api_key

# Google Sheets
GOOGLE_SHEET_ID=your_google_sheet_id
```

---

## 📦 Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ How to Run

```bash
python main.py
```

The script will:

1. Read pending rows from your Google Sheet
2. Process each company's website and audio
3. Upload DOCX summaries to Drive
4. Update the sheet with links and mark as `Done`

---

## 🧾 Google Sheet Format

| Date | Company Name | ... | Website | Audio Folder | ... | Audio Summary Link | Website Summary Link | Status |
| ---- | ------------ | --- | ------- | ------------ | --- | ------------------ | -------------------- | ------ |

- Script auto-skips rows marked as `Done`
- Auto-fills audio folder link if missing (based on company name match)

---

## 🧠 Tech Stack

- OpenAI GPT-4 / Whisper
- Python + dotenv + gspread
- Google Drive & Sheets API
- `python-docx` for report generation
- `pydub` for audio chunking

---

## 📌 Notes

- If you're renaming folders (`Audio → audio`, `Website → website`), remember to use an **intermediate rename** when committing to Git on Windows.
- Audio files over 25MB are auto-split into chunks for Whisper transcription.

---
