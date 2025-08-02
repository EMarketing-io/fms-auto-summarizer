import re
import json
from pydub import AudioSegment
import os


# Function to extract JSON block from OpenAI response
def extract_json_block(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError as e:
            print("❌ JSON decoding failed:", e)
            print("OpenAI response:", text)
            raise
    else:
        print("❌ No JSON found in OpenAI response.")
        print("Raw output:", text)
        raise ValueError("Response did not contain valid JSON.")


# Function to split audio file into smaller chunks for transcription
def split_audio_file(audio_path, max_size_bytes=25 * 1024 * 1024):
    print("🔍 Determining optimal chunk size for Whisper API...")

    # Load the audio file
    audio = AudioSegment.from_file(audio_path)
    duration_ms = len(audio)
    
    # Calculate chunk length based on file size
    test_durations = [15 * 60 * 1000, 10 * 60 * 1000, 5 * 60 * 1000]

    # If the audio is shorter than the maximum size, return it as a single chunk
    base_name = os.path.splitext(audio_path)[0]

    # Check if the audio file is small enough for a single chunk
    for test_duration in test_durations:
        test_chunk = audio[:test_duration]
        test_path = f"{base_name}_test_chunk.m4a"
        test_chunk.export(test_path, format="mp4")
        size = os.path.getsize(test_path)
        os.remove(test_path)
        
        # If the size is within limits, use this duration
        if size <= max_size_bytes:
            chunk_length_ms = test_duration
            break
    # If no suitable duration found, use a default of 1 minute
    else:
        chunk_length_ms = 60 * 1000
        
        # Reduce chunk size until it fits within the max size limit
        while True:
            test_chunk = audio[:chunk_length_ms]
            test_path = f"{base_name}_test_chunk.m4a"
            test_chunk.export(test_path, format="mp4")
            if os.path.getsize(test_path) > max_size_bytes:
                chunk_length_ms -= 10 * 1000
                os.remove(test_path)
            else:
                os.remove(test_path)
                break

    # Create chunks based on the determined chunk length
    chunks = []
    for i in range(0, duration_ms, chunk_length_ms):
        chunk = audio[i : i + chunk_length_ms]
        chunk_path = f"{base_name}_part{i // chunk_length_ms}.m4a"
        chunk.export(chunk_path, format="mp4")
        chunks.append(chunk_path)

    print(f"🧩 Final chunk size: {chunk_length_ms // 1000} seconds")
    print(f"📂 Total chunks: {len(chunks)}")
    return chunks