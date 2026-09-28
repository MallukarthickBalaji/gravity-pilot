"""
voice_agent.py — Voice handling module for Text-to-Speech (TTS).
"""
import logging
import threading

logger = logging.getLogger(__name__)

# Try importing pyttsx3, fallback gracefully if not installed
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    logger.warning("pyttsx3 is not installed. Text-to-speech will be disabled.")


def speak_text_async(text: str):
    """Speaks the given text asynchronously so it doesn't block the GUI."""
    if not TTS_AVAILABLE:
        return

    def run_speech():
        try:
            # Re-initialize engine per thread in pyttsx3 for stability
            engine = pyttsx3.init()
            # Optional: Configure voice rate/volume
            engine.setProperty("rate", 165)
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            logger.error(f"TTS error: {e}")

    thread = threading.Thread(target=run_speech, daemon=True)
    thread.start()
