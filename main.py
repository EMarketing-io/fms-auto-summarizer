# Standard Libraries
import os

# Third-Party Libraries
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Sheet Utilities
from sheet_utils import update_sheet_with_links

# Website Processing Modules
from Website.extract import extract_text_from_url
from Website.summarize import summarize_with_openai
from Website.document import create_docx_in_memory as create_website_doc
from Website.drive import upload_docx_to_gdrive

# Audio Processing Modules
from Audio.transcription import transcribe_audio
from Audio.summarizer import generate_summary
from Audio.doc_generator import generate_docx as create_audio_doc
from Audio.drive_utils import (
    upload_file_to_drive_in_memory,
    download_audio_from_drive,
    find_audio_file_in_folder,
    find_folder_id_by_partial_name,
)
from Audio.config import GOOGLE_DRIVE_FOLDER_ID, GOOGLE_DRIVE_API_KEY
from Audio.utils import split_audio_file

# Load environment variables
load_dotenv()


# Function to extract Google Drive folder ID from a link
def extract_drive_folder_id(link):
    try:
        if "folders/" in link:
            return link.split("folders/")[1].split("?")[0]
        elif "id=" in link:
            return link.split("id=")[1].split("&")[0]
        else:
            return None
    except Exception:
        return None


# Function to get all rows from the Google Sheet
def get_all_rows():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        os.getenv("GOOGLE_SERVICE_ACCOUNT"), scope
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key(os.getenv("GOOGLE_SHEET")).sheet1
    return sheet.get_all_values(), sheet


# Main function to process all rows in the Google Sheet
def main():
    print("📦 SmartSummarizer")

    # Get all rows from the Google Sheet
    rows, sheet = get_all_rows()
    processed_count = 0

    # Iterate through each row in the sheet
    print(f"📊 Total Rows: {len(rows) - 1}")
    for idx, row in enumerate(rows[1:], start=2):
        meeting_date = row[0].strip() if len(row) > 0 else ""
        company_name = row[1].strip() if len(row) > 1 else ""
        website_url = row[4].strip() if len(row) > 4 else ""
        audio_folder_link = row[5].strip() if len(row) > 5 else ""
        status = row[8].strip().lower() if len(row) > 8 else ""

        print(f"\n🔍 Row {idx} — Status: {status or '[empty]'}")
        print(f"   🗓 Date         : {meeting_date or '[MISSING]'}")
        print(f"   🏢 Company Name : {company_name or '[MISSING]'}")
        print(f"   🌐 Website Link : {website_url or '[MISSING]'}")
        print(f"   🎧 Audio Folder : {audio_folder_link or '[MISSING]'}")

        # Skip if already marked as "Done"
        if status == "done":
            print(f"✅ Skipped: Already marked as Done.")
            continue

        # Validate required fields
        if not audio_folder_link:
            parent_drive_folder = os.getenv("AUDIO_PARENT_FOLDER_ID")
            folder_id = find_folder_id_by_partial_name(company_name, parent_drive_folder, api_key=GOOGLE_DRIVE_API_KEY)
            
            # Auto-fill audio folder link if missing
            if folder_id:
                audio_folder_link = (f"https://drive.google.com/drive/folders/{folder_id}?usp=sharing")
                sheet.update_cell(idx, 6, audio_folder_link)
            else:
                print(f"❌ Could not auto-fill Audio Folder Link for: {company_name}")
                print(f"⛔ Skipping Row {idx} — Required audio folder is missing.")
                continue
        # Check if all required fields are present
        if (not meeting_date
            or not company_name
            or not website_url
            or not audio_folder_link):
            print(f"⛔ Skipping Row {idx} — One or more required fields are missing.")
            continue

        print(f"✅ Row {idx} passed validation. Beginning summarization...")
        
        # Prepare filenames and results
        website_filename = f"{company_name} Website Summary.docx"
        audio_filename = f"{company_name} Meeting Notes.docx"
        website_link_result = None
        audio_link_result = None

        # 🌐 Website Summary
        try:
            print(f"🌐 Extracting and summarizing website: {website_url}")
            raw_text = extract_text_from_url(website_url)
            summary = summarize_with_openai(raw_text)
            doc_stream = create_website_doc(summary, f"{company_name} Website Summary")
            drive_file_id = upload_docx_to_gdrive(doc_stream, website_filename)
            website_link_result = (f"https://drive.google.com/file/d/{drive_file_id}/view")
            print(f"✅ Website uploaded: {website_link_result}")
        except Exception as e:
            print(f"❌ Website processing failed: {e}")

        # 🎧 Audio Summary
        try:
            print(f"🎧 Searching audio folder: {audio_folder_link}")
            folder_id = extract_drive_folder_id(audio_folder_link)
            if not folder_id:
                raise Exception("Invalid or missing folder ID.")

            file_id = find_audio_file_in_folder(folder_id, extension=".m4a", api_key=GOOGLE_DRIVE_API_KEY)
            if not file_id:
                raise Exception("No .m4a file found in folder.")

            print("🎙️ Transcribing and summarizing audio...")
            audio_path = download_audio_from_drive(file_id, api_key=GOOGLE_DRIVE_API_KEY)
            transcript = ""
            audio_size_bytes = os.path.getsize(audio_path)

            # Check if audio file is small enough for single transcription
            if audio_size_bytes <= 25 * 1024 * 1024:
                print("🎙️ Transcribing with OpenAI Whisper API (single file)...")
                transcript = transcribe_audio(audio_path)
            else:
                print(f"📦 Audio is {round(audio_size_bytes / 1024 / 1024, 2)}MB — splitting for transcription.")
                chunks = split_audio_file(audio_path)
                all_transcripts = []

                # Transcribe each chunk
                for i, chunk_path in enumerate(chunks, start=1):
                    print(
                        f"📝 Transcribing chunk {i}/{len(chunks)}: {os.path.basename(chunk_path)}"
                    )
                    chunk_transcript = transcribe_audio(chunk_path)
                    all_transcripts.append(chunk_transcript)
                    os.remove(chunk_path)

                transcript = "\n".join(all_transcripts)
            # Generate summary and create DOCX
            summary_data = generate_summary(transcript)
            docx_file = create_audio_doc(summary_data, company_name, meeting_date)
            file_id_uploaded = upload_file_to_drive_in_memory(
                docx_file,
                folder_id=GOOGLE_DRIVE_FOLDER_ID,
                final_name=audio_filename,
            )
            audio_link_result = (f"https://drive.google.com/file/d/{file_id_uploaded}/view")
            os.remove(audio_path)
            print(f"✅ Audio uploaded: {audio_link_result}")
        except Exception as e:
            print(f"❌ Audio processing failed: {e}")
            
        # Update Google Sheet with results
        if website_link_result or audio_link_result:
            update_sheet_with_links(
                row_index=idx,
                meeting_url=audio_link_result,
                meeting_name=audio_filename,
                website_url=website_link_result,
                website_name=website_filename,
            )
            print(f"✅ Row {idx} updated in sheet and marked as 'Done'.")
            processed_count += 1
        else:
            print("⚠️ No uploads succeeded. Row not marked as Done.")

    print(f"\n📊 Summary: {processed_count} row(s) processed and marked as Done.")


if __name__ == "__main__":
    main()