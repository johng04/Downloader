# Version 3.1

import os
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from yt_dlp import YoutubeDL

# === Config ===
ffmpeg_path = 'ffmpeg-master-latest-win64-gpl-shared/bin/ffmpeg.exe'

# === Dependency check ===
def check_and_install(package):
    try:
        __import__(package)
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", package, "--upgrade"],
            creationflags=subprocess.CREATE_NO_WINDOW
        )
    except ImportError:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", package],
            creationflags=subprocess.CREATE_NO_WINDOW
        )

# Ensure yt-dlp is installed
check_and_install("yt_dlp")

# Check if ffmpeg is installed
def is_ffmpeg_installed():
    try:
        subprocess.run(
            [ffmpeg_path, "-version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        messagebox.showerror("Error", "ffmpeg not found. Please install ffmpeg and ensure it is in your PATH.")
        sys.exit(1)

is_ffmpeg_installed()

# === Download hook ===
def my_hook(d):
    if d['status'] == 'finished':
        filename = d.get('filename', 'Unknown File')
        status_label.config(text=f"Download complete: {filename}")
        root.update_idletasks()

# === Download logic ===
def audio_playlists():
    link = url_entry.get().strip()
    album_name = album_entry.get().strip()
    album_art = artwork_entry.get().strip()
    download_dir = download_dir_entry.get().strip()

    if not link:
        messagebox.showerror("Error", "Please enter a valid URL.")
        return

    status_label.config(text="Extracting playlist info...")
    root.update_idletasks()

    ydl_opts_info = {'quiet': True, 'extract_flat': True}
    with YoutubeDL(ydl_opts_info) as ydl:
        info_dict = ydl.extract_info(link, download=False)
        entries = info_dict.get('entries', [])
        playlist_title = info_dict.get('title', 'Unknown Playlist')
        album_name = album_name if album_name else playlist_title

    album_folder = os.path.join(download_dir, album_name)
    os.makedirs(album_folder, exist_ok=True)

    for track_counter, track in enumerate(entries, start=1):
        track_title = track.get('title', f"Track {track_counter}")
        print(f"Downloading: {track_title}")

        ydl_opts_download = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(album_folder, '%(title)s.%(ext)s'),
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                },
                {
                    'key': 'FFmpegMetadata',
                    'add_metadata': True,
                }
            ],
            'postprocessor_args': ['-metadata', f'track={track_counter}'],
            'ffmpeg_location': ffmpeg_path,
            'progress_hooks': [my_hook],
            'ignoreerrors': True,
            'quiet': True,
        }

        with YoutubeDL(ydl_opts_download) as ydl:
            ydl.download([track['url']])

def audio_singles():
    link = url_entry.get().strip()
    download_dir = download_dir_entry.get().strip()

    if not link:
        messagebox.showerror("Error", "Please enter a valid URL.")
        return

    status_label.config(text="Downloading song...")
    root.update_idletasks()

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            },
            {
                'key': 'FFmpegMetadata',
                'add_metadata': True,
            }
        ],
        'noplaylist': True,
        'ignoreerrors': True,
        'quiet': True,
        'ffmpeg_location': ffmpeg_path,
        'progress_hooks': [my_hook],
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])

def video_playlists():
    link = url_entry.get().strip()
    download_dir = download_dir_entry.get().strip()

    if not link:
        messagebox.showerror("Error", "Please enter a valid URL.")
        return

    status_label.config(text="Extracting video playlist...")
    root.update_idletasks()

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
        'outtmpl': os.path.join(download_dir, '%(playlist_title)s', '%(playlist_index)s - %(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'ignoreerrors': True,
        'quiet': True,
        'ffmpeg_location': ffmpeg_path,
        'progress_hooks': [my_hook]
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])

def video_singles():
    link = url_entry.get().strip()
    download_dir = download_dir_entry.get().strip()

    if not link:
        messagebox.showerror("Error", "Please enter a valid URL.")
        return

    status_label.config(text="Downloading video...")
    root.update_idletasks()

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
        'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'ignoreerrors': True,
        'quiet': True,
        'ffmpeg_location': ffmpeg_path,
        'progress_hooks': [my_hook],
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])

    status_label.config(text="Video download complete!")

# === GUI helper functions ===
def select_directory():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        download_dir_entry.delete(0, tk.END)
        download_dir_entry.insert(0, folder_selected)

def select_artwork():
    file_selected = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png;*.jpeg")])
    if file_selected:
        artwork_entry.delete(0, tk.END)
        artwork_entry.insert(0, file_selected)

# === GUI Setup ===
try:
    root = tk.Tk()
    root.title("YouTube Downloader")
    root.geometry("500x500")

    # URL
    tk.Label(root, text="YouTube URL:").pack(pady=5)
    url_entry = tk.Entry(root, width=80)
    url_entry.pack()

    # Album Name
    tk.Label(root, text="Album Name (Optional):").pack(pady=5)
    album_entry = tk.Entry(root, width=50)
    album_entry.pack()

    # Artwork
    tk.Label(root, text="Album Artwork (Optional):").pack(pady=5)
    artwork_entry = tk.Entry(root, width=50)
    artwork_entry.pack()
    tk.Button(root, text="Browse", command=select_artwork).pack(pady=2)

    # Download Dir
    tk.Label(root, text="Download Directory:").pack(pady=5)
    download_dir_entry = tk.Entry(root, width=50)
    download_dir_entry.pack()
    tk.Button(root, text="Select Folder", command=select_directory).pack(pady=2)

    # Action buttons
    tk.Button(root, text="Download Audio Playlist", command=lambda: threading.Thread(target=audio_playlists).start()).pack(pady=5)
    tk.Button(root, text="Download Single Song", command=audio_singles).pack(pady=5)
    tk.Button(root, text="Download Video Playlist", command=lambda: threading.Thread(target=video_playlists).start()).pack(pady=5)
    tk.Button(root, text="Download Single Video", command=video_singles).pack(pady=5)

    # Status label
    status_label = tk.Label(root, text="", fg="blue")
    status_label.pack()

    root.mainloop()
except Exception as e:
    messagebox.showerror("Fatal Error", f"Something went wrong:\n{e}")
    if 'root' in locals():
        root.destroy()
    sys.exit(1)
