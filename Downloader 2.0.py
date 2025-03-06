import subprocess
import sys
import os
import re
from yt_dlp import YoutubeDL

# Download directory (change if needed)
audio_path = '2. To burn/'
video_path = '3. Videos/'

# Path to ffmpeg (change if needed)
ffmpeg_path = 'ffmpeg-master-latest-win64-gpl-shared/bin/ffmpeg.exe'

# Function to check if a package is installed
def check_and_install(package):
    try:
        __import__(package)
        print(f"{package} is already installed.")
    except ImportError:
        print(f"{package} not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Ensure yt-dlp is installed
check_and_install("yt_dlp")

# Check if ffmpeg is installed
def is_ffmpeg_installed():
    try:
        subprocess.run(["ffmpeg", "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
    if not is_ffmpeg_installed():
        print("ffmpeg not found. Please install ffmpeg and ensure it is in your PATH.")
        input("Press Enter to continue...")
        sys.exit(1)
    else:
        print("ffmpeg is installed.")

# Progress hook to print custom messages
def my_hook(d):
    if d['status'] == 'finished':
        print(f"\nDownload complete: {d['filename']}\n")

# Download playlists
def audio_playlists():
    print("Input link:")
    link = input().strip()

    # Extract playlist information first
    ydl_opts_info = {
        'quiet': True,
        'extract_flat': True,  # Extracts only playlist info without downloading
    }

    with YoutubeDL(ydl_opts_info) as ydl:
        info_dict = ydl.extract_info(link, download=False)
        entries = info_dict.get('entries', [])
        playlist_title = info_dict.get('title', 'Unknown Playlist')

    count = 0  # Initialize counter before starting the download

    # Start downloading each track with track number
    for track_counter, track in enumerate(entries, start=1):  # Start counter from 1
        track_title = track.get('title', f"Track {track_counter}")
        print(f"Downloading: {track_title}")

        # Set up options for downloading with track number in metadata
        ydl_opts_download = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(audio_path, playlist_title, '%(title)s.%(ext)s'),
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio', 
                    'preferredcodec': 'mp3', 
                    'preferredquality': '192',
                },
                {
                    'key': 'FFmpegMetadata',
                    'add_metadata': True,  # Add metadata after download
                }
            ],
            'postprocessor_args': ['-metadata', f'track={track_counter}'],
            'ffmpeg_location': ffmpeg_path,
            'progress_hooks': [my_hook],
            'ignoreerrors': True,
            'quiet': True,
        }

        # Download the current track
        with YoutubeDL(ydl_opts_download) as ydl:
            ydl.download([track['url']])  # Download using the track URL





# Download single songs
def audio_singles():
    print("Input link:")
    link = input().strip()

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(audio_path, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        },
        {
            'key': 'FFmpegMetadata',
            'add_metadata': True,  # Add metadata after download
        }],
        'noplaylist': True,
        'ignoreerrors': True,
        'quiet': True,
        'ffmpeg_location': ffmpeg_path,
        'progress_hooks': [my_hook]
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])

# Download video playlists
def video_playlists():
    print("Input link:")
    link = input().strip()

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
        'outtmpl': os.path.join(video_path, '%(playlist_title)s', '%(playlist_index)s - %(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'ignoreerrors': True,
        'quiet': True,
        'ffmpeg_location': ffmpeg_path,
        'progress_hooks': [my_hook]
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])

# Download single video
def video_singles():
    print("Input link:")
    link = input().strip()

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
        'outtmpl': os.path.join(video_path, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'ignoreerrors': True,
        'quiet': True,
        'ffmpeg_location': ffmpeg_path,
        'progress_hooks': [my_hook]
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])

# Menu
close = 0
while close != 9:
    print("Select option \n1. Download an audio playlist \n2. Download a single song\n3. Download a video playlist \n4. Download a single video\n9. Quit")
    Selection = input().strip()

    if Selection == "1":
        audio_playlists()
    elif Selection == "2":
        audio_singles()
    elif Selection == "3":
        video_playlists()
    elif Selection == "4":
        video_singles()
    elif Selection == "9":
        exit()
    else:
        print("Invalid selection\n")
