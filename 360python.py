import os
import time
import random
import string
import shutil  # Added for shutil.move usage
import ffmpeg
import requests  # Added to import requests module
import json
from datetime import datetime

# Configuration variables
input_folder = 'input'  # Main folder where original videos are stored
output_folder = 'vid'  # Folder where converted videos will be saved
backup_folder = 'backup'  # New folder for backup
check_interval = 10  # Time in seconds between scans for new videos
bot_token = '6790570140:AAFDgvRUfhLz1h5lPYT4CJep1hjzBMsuSrg'  # Replace with your Telegram bot token
random_name_length = 10  # Length of the random string for renaming files
group_id = '-4162965435'  # Replace with your Telegram group ID
channel_id = '-1002215202966'
renamed_files = False
telegram_stop = 30
processed_messages_file = 'processed_messages.json'

# Ensure input and output directories exist
os.makedirs(input_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)
os.makedirs(backup_folder, exist_ok=True)

# Set to track processed message IDs
processed_messages = set()

# Function to generate a random string of fixed length
def generate_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))

# Function to rename .mp4 files in a folder to random names
def randomize_mp4_names(folder_path, length):
    try:
        mp4_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and f.endswith('.mp4')]
        
        for filename in mp4_files:
            random_name = generate_random_string(length)
            new_filename = os.path.join(folder_path, random_name + '.mp4')
            os.rename(os.path.join(folder_path, filename), new_filename)
            print(f'Renamed {filename} to {random_name}.mp4')
    except Exception as e:
        print(f'Error during renaming: {e}')

# Function to convert video to .mp4 using FFmpeg
def convert_to_mp4(input_file, output_file):
    try:
        stream = ffmpeg.input(input_file)
        output_path = os.path.join(output_folder, output_file)
        stream = ffmpeg.output(stream, output_path, vf='scale=-2:420', vcodec='libx264')
        ffmpeg.run(stream, overwrite_output=True)
        print(f'Conversion successful: {output_path}')

        # Send the video to the Telegram group
        send_video_to_telegram(input_file)

        # Move original file to backup folder
        backup_path = os.path.join(backup_folder, os.path.basename(input_file))
        shutil.move(input_file, backup_path)
        print(f'Moved {input_file} to {backup_folder}')

    except ffmpeg.Error as e:
        print(f'Error during conversion: {e.stderr}')
    except Exception as e:
        print(f'Unexpected error: {e}')

# Function to interact with Telegram bot and continuously download videos
def telegram_bot():
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"

        while True:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if 'result' in data:
                    for result in data['result']:
                        if 'message' in result and 'video' in result['message']:
                            message_id = result['message']['message_id']
                            if message_id not in processed_messages:
                                video_file_id = result['message']['video']['file_id']
                                download_video(video_file_id)
                                processed_messages.add(message_id)  # Add message_id to processed set
                                save_processed_messages()
                            else:
                                print(f"Already processed message {message_id}. Skipping...")
                else:
                    print("No 'result' key in Telegram API response.")
            else:
                print(f"Error fetching updates: {response.status_code} - {response.text}")

            break

    except Exception as e:
        print(f"Error in telegram_bot: {e}")

# Function to download video file from Telegram
def download_video(file_id):
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getFile"
        params = {'file_id': file_id}

        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if 'result' in data and 'file_path' in data['result']:
                file_path = data['result']['file_path']
                download_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
                video_name = os.path.join("input", f"video_{time.time()}.mp4")
                with open(video_name, 'wb') as f:
                    video_response = requests.get(download_url)
                    f.write(video_response.content)
                    print(f"Downloaded video: {video_name}")
            else:
                print(f"Error downloading file: {data}")
        else:
            print(f"Error fetching file info: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"Error in download_video: {e}")

        # Function to save processed_messages set to file
def save_processed_messages():
    try:
        with open(processed_messages_file, 'w') as f:
            json.dump(list(processed_messages), f)
            print(f"Saved processed messages to {processed_messages_file}")
    except Exception as e:
        print(f"Error saving processed messages: {e}")

# Function to load processed_messages set from JSON file
def load_processed_messages():
    global processed_messages
    try:
        if os.path.exists(processed_messages_file):
            with open(processed_messages_file, 'r') as f:
                processed_messages = set(json.load(f))
                print(f"Loaded processed messages from {processed_messages_file}")
    except Exception as e:
        print(f"Error loading processed messages: {e}")

# Function to send video to Telegram group
def send_video_to_telegram(video_path):
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendVideo"
        with open(video_path, 'rb') as video_file:
            files = {'video': video_file}
            data = {'chat_id': channel_id}
            response = requests.post(url, files=files, data=data)
            if response.status_code == 200:
                print(f"Video sent to Telegram group {channel_id}")
            else:
                print(f"Error sending video: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error in send_video_to_telegram: {e}")

# Main function to process downloaded videos and convert them
def main():
    global renamed_files

    load_processed_messages()  # Load processed messages from file

    if not renamed_files:
        randomize_mp4_names(output_folder, random_name_length)
        renamed_files = True

    while True:
        try:
            telegram_bot()

            for root, dirs, files in os.walk(input_folder):
                for file in files:
                    if file.endswith(('.avi', '.mp4', '.mkv', '.mov', '.MOV')):
                        input_file = os.path.join(root, file)
                        random_string = generate_random_string(10)
                        output_file = f'{random_string}_converted.mp4'
                        convert_to_mp4(input_file, output_file)

        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(check_interval)  # Wait and retry


if __name__ == '__main__':
    main()

