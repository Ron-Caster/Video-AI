"""Google Cloud Speech-to-Text integration for automatic caption generation."""
from __future__ import annotations
from pathlib import Path


def transcribe_to_srt(audio_wav: Path, language: str = "en-US", sample_rate: int = 16000) -> str:
    """Transcribe audio file to SRT format using Google Cloud Speech-to-Text.
    
    Args:
        audio_wav: Path to WAV audio file
        language: Language code (e.g., 'en-US', 'es-ES')
        sample_rate: Audio sample rate in Hz
        
    Returns:
        SRT-formatted subtitle string
        
    Raises:
        RuntimeError: If Google Cloud Speech client is unavailable
    """
    try:
        from google.cloud import speech
    except Exception as e:
        raise RuntimeError("google-cloud-speech is required for --generate-captions. Install deps and set GOOGLE_APPLICATION_CREDENTIALS.") from e

    client = speech.SpeechClient()

    with audio_wav.open("rb") as f:
        content = f.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=sample_rate,
        language_code=language,
        enable_automatic_punctuation=True,
        model="default",
    )

    response = client.recognize(config=config, audio=audio)

    # Build a naive SRT with each alternative as a short sequential caption.
    # Note: synchronous recognize has a limit (~1 min). For longer, use long_running_recognize.
    # For simplicity here, we chunk per result in 5-second windows.
    srt_lines = []
    idx = 1
    t = 0.0
    for result in response.results:
        text = result.alternatives[0].transcript.strip()
        if not text:
            continue
        start = t
        end = t + max(2.0, min(6.0, len(text) / 12.0))
        srt_lines.append(f"{idx}\n{_fmt_ts(start)} --> {_fmt_ts(end)}\n{text}\n\n")
        idx += 1
        t = end

    return "".join(srt_lines)


def _fmt_ts(seconds: float) -> str:
    import math
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - math.floor(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
