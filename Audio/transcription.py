import openai
from Audio.config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY


# Function to transcribe audio using OpenAI Whisper API
def transcribe_audio(audio_path):
    print("🎙️ Transcribing with OpenAI Whisper API...")
    
    # OpenAI Whisper API call to transcribe audio
    with open(audio_path, "rb") as audio_file:
        response = openai.Audio.transcribe(model="whisper-1", file=audio_file, response_format="text", task="translate")
        return response.strip()