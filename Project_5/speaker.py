"""
Speaker Component Class
Handles text-to-speech with background threading
"""

import threading
import queue
import os

class Speaker:
    def __init__(self):
        """Initialize speaker with background thread"""
        self.queue = queue.Queue()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        
    def say(self, text):
        """
        Queue text to be spoken
        Non-blocking - returns immediately
        
        Args:
            text: String to speak
        """
        self.queue.put(text)
        
    def _run(self):
        """Background worker that processes speech queue"""
        while True:
            text = self.queue.get()
            
            # Sanitize text to prevent command injection
            safe_text = text.replace("'", "").replace('"', '').replace(';', '')
            
            # Use espeak to speak
            os.system(f"espeak '{safe_text}'")
            
            self.queue.task_done()
