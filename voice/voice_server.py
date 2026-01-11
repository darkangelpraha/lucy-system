"""
Lucy Voice Interface - Google Cloud Speech-to-Text & Text-to-Speech

Endpoints:
- POST /voice - Upload audio, get voice response
- POST /speak - Text to speech
- WS /voice-stream - Real-time voice conversation
"""

from fastapi import FastAPI, File, UploadFile, WebSocket
from fastapi.responses import StreamingResponse
from google.cloud import speech_v1 as speech
from google.cloud import texttospeech
import httpx
import os
import io
from elevenlabs import generate, set_api_key, Voice, VoiceSettings

app = FastAPI(title="Lucy Voice Interface")

# Configuration
ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://lucy-orchestrator:8080")
USE_ELEVENLABS = os.getenv("USE_ELEVENLABS", "true").lower() == "true"
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")

# Initialize ElevenLabs if enabled
if USE_ELEVENLABS and ELEVENLABS_API_KEY:
    set_api_key(ELEVENLABS_API_KEY)

# Google Cloud clients (fallback)
speech_client = speech.SpeechClient()
tts_client = texttospeech.TextToSpeechClient()

# Voice configuration - Google Cloud TTS (fallback)
VOICE_CONFIG = texttospeech.VoiceSelectionParams(
    language_code="cs-CZ",  # Czech
    name="cs-CZ-Wavenet-A",  # Female voice
    ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
)

AUDIO_CONFIG = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3,
    speaking_rate=1.0,
    pitch=0.0
)

# ElevenLabs Voice - Scarlett Johansson-like (Rachel - warm, natural)
ELEVENLABS_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel - closest to Scarlett
ELEVENLABS_VOICE_SETTINGS = VoiceSettings(
    stability=0.5,
    similarity_boost=0.75,
    style=0.5,
    use_speaker_boost=True
)

@app.get("/health")
async def health():
    return {"status": "healthy", "mode": "voice"}

@app.post("/voice")
async def voice_query(audio: UploadFile = File(...)):
    """
    Voice query endpoint
    
    1. Upload audio file (WAV, MP3, etc.)
    2. Lucy transcribes to text
    3. Processes query via orchestrator
    4. Returns text + audio response
    """
    
    # 1. Transcribe audio to text
    audio_content = await audio.read()
    
    speech_config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="cs-CZ",  # Czech
        alternative_language_codes=["en-US"],  # Fallback to English
        enable_automatic_punctuation=True
    )
    
    audio_data = speech.RecognitionAudio(content=audio_content)
    
    response = speech_client.recognize(
        config=speech_config,
        audio=audio_data
    )
    
    if not response.results:
        return {"error": "No speech detected"}
    
    transcript = response.results[0].alternatives[0].transcript
    
    # 2. Process query via orchestrator
    async with httpx.AsyncClient() as client:
        query_response = await client.post(
            f"{ORCHESTRATOR_URL}/query",
            json={"query": transcript},
            timeout=60.0
        )
        result = query_response.json()
    
    # 3. Convert response to speech
    text_response = result.get("response", "Omlouvám se, nepodařilo se mi zpracovat dotaz.")
    
    # Use ElevenLabs if available, otherwise Google TTS
    if USE_ELEVENLABS and ELEVENLABS_API_KEY:
        audio_content = generate(
            text=text_response,
            voice=Voice(
                voice_id=ELEVENLABS_VOICE_ID,
                settings=ELEVENLABS_VOICE_SETTINGS
            ),
            model="eleven_multilingual_v2"
        )
    else:
        synthesis_input = texttospeech.SynthesisInput(text=text_response)
        tts_response = tts_client.synthesize_speech(
            input=synthesis_input,
            voice=VOICE_CONFIG,
            audio_config=AUDIO_CONFIG
        )
        audio_content = tts_response.audio_content
    
    # 4. Return both text and audio
    return {
        "transcript": transcript,
        "text_response": text_response,
        "audio_response_base64": audio_content.hex() if isinstance(audio_content, bytes) else audio_content,
        "agent": result.get("agent"),
        "sources": result.get("sources", []),
        "voice_engine": "elevenlabs" if (USE_ELEVENLABS and ELEVENLABS_API_KEY) else "google_tts"
    }

@app.post("/speak")
async def text_to_speech(text: str):
    """Convert text to speech - returns MP3 audio"""
    
    # Use ElevenLabs if available
    if USE_ELEVENLABS and ELEVENLABS_API_KEY:
        audio_content = generate(
            text=text,
            voice=Voice(
                voice_id=ELEVENLABS_VOICE_ID,
                settings=ELEVENLABS_VOICE_SETTINGS
            ),
            model="eleven_multilingual_v2"
        )
    else:
        synthesis_input = texttospeech.SynthesisInput(text=text)
        response = tts_client.synthesize_speech(
            input=synthesis_input,
            voice=VOICE_CONFIG,
            audio_config=AUDIO_CONFIG
        )
        audio_content = response.audio_content
    
    # Return audio stream
    return StreamingResponse(
        io.BytesIO(audio_content if isinstance(audio_content, bytes) else audio_content),
        media_type="audio/mpeg",
        headers={"Content-Disposition": "attachment; filename=response.mp3"}
    )

@app.websocket("/voice-stream")
async def voice_stream(websocket: WebSocket):
    """
    Real-time voice conversation
    
    Client streams audio chunks → Lucy responds in real-time
    """
    await websocket.accept()
    
    # Streaming recognition config
    streaming_config = speech.StreamingRecognitionConfig(
        config=speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="cs-CZ"
        ),
        interim_results=True
    )
    
    try:
        while True:
            # Receive audio chunk from client
            audio_chunk = await websocket.receive_bytes()
            
            # Stream to Speech-to-Text
            # (Implementation details for streaming...)
            
            # For now, placeholder
            await websocket.send_json({
                "type": "transcript",
                "text": "Streaming transcript...",
                "is_final": False
            })
    
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
