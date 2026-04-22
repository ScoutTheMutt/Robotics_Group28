"""
SpeechRecognizer — Captures audio and recognizes bathroom/lab requests.

Uses Google Speech Recognition (requires internet or local alternative).
Returns 'bathroom', 'lab', or None if no match.
"""

import threading
import time

class SpeechRecognizer:
    """Recognizes spoken destination requests."""

    def __init__(self):
        """Initialize speech recognition."""
        try:
            import speech_recognition as sr
            self._recognizer = sr.Recognizer()
            self._microphone = sr.Microphone()
            self._available = True
        except ImportError:
            print("[SPEECH] WARNING: speech_recognition not installed")
            print("[SPEECH]   Run: pip install SpeechRecognition")
            self._recognizer = None
            self._available = False

    def recognize_destination(self, timeout_seconds=10):
        """
        Listen for destination request with timeout.
        
        Args:
            timeout_seconds: max listening time
            
        Returns:
            'bathroom', 'lab', or None
        """
        if not self._available or self._recognizer is None:
            print("[SPEECH] Recognition unavailable")
            return None

        try:
            with self._microphone as source:
                self._recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print(f"[SPEECH] Listening for {timeout_seconds}s...")
                audio = self._recognizer.listen(source, timeout=timeout_seconds)
            
            text = self._recognizer.recognize_google(audio).lower()
            print(f"[SPEECH] Recognized: '{text}'")
            
            if 'bathroom' in text or 'restroom' in text:
                return 'bathroom'
            elif 'robot' in text and 'lab' in text:
                return 'lab'
            
            return None
            
        except Exception as e:
            print(f"[SPEECH] Error: {e}")
            return None
