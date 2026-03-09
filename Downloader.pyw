# Version 3.10

#imports
import os
import subprocess
import sys
import threading
import shutil
import re
import tkinter as tk
from tkinter import filedialog, messagebox

#Dependency check
def check_and_install(package):
    root = tk.Tk()
    root.title("Updating")
    root.geometry("250x80")

    label = tk.Label(root, text=f"Updating {package}...")
    label.pack(pady=20)

    root.update()

    try:
        __import__(package)
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", package, "--upgrade"],
            creationflags=subprocess.CREATE_NO_WINDOW
        )
    except ImportError:
        label.config(text=f"Installing {package}...")
        root.update()
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", package],
            creationflags=subprocess.CREATE_NO_WINDOW
        )

    root.destroy()

# Ensure yt-dlp is installed
check_and_install("yt_dlp")
from yt_dlp import YoutubeDL

# Check if ffmpeg is installed
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ffmpeg_path = os.path.join(BASE_DIR, 'ffmpeg-master-latest-win64-gpl-shared/bin/ffmpeg.exe')
if not os.path.exists(ffmpeg_path):
    messagebox.showwarning(
        "Warning",
        "ffmpeg.exe not found in the script folder. Some downloads may fail."
    )

# Download hook
def my_hook(d):
    if d['status'] == 'finished':
        filename = d.get('filename', 'Unknown File')
        status_label.config(text=f"Download complete: {filename}")
        root.update_idletasks()

# Sanitise filename
def Sanitise_filename(name: str, default_name="unknown_song") -> str:
    name = re.sub(r'[<>:"/\\|?*\n\r\t]', '', name)  # Remove forbidden characters

    reserved = {"CON", "PRN", "AUX", "NUL", "COM1", "LPT1", "COM2", "LPT2",
                "COM3", "LPT3", "COM4", "LPT4", "COM5", "LPT5", "COM6",
                "LPT6", "COM7", "LPT7", "COM8", "LPT8", "COM9", "LPT9"}
    if name.upper() in reserved or name.strip('.') == '' or not name.strip():
        return default_name

    return name
    
# Download logic
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
        raw_title = track.get('title', f"Track {track_counter}")
        track_title = Sanitise_filename(raw_title)
        artist_name = track.get('uploader', 'Unknown Artist')
        print(f"Downloading: {track_title}")

        # Paths
        temp_output = os.path.join(album_folder, f"{track_title}.%(ext)s")
        final_output = os.path.join(album_folder, f"{track_title}.mp3")
        temp_mp3 = os.path.join(album_folder, f"{track_title}.mp3")

        # Download audio only
        ydl_opts_download = {
            'format': 'bestaudio/best',
            'outtmpl': temp_output,
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }
            ],
            'ffmpeg_location': ffmpeg_path,
            'progress_hooks': [my_hook],
            'quiet': True,
            'ignoreerrors': True,
        }

        with YoutubeDL(ydl_opts_download) as ydl:
            ydl.download([track['url']])

        #Embed album art with ffmpeg
        if (album_art):
            tagged_output = os.path.join(album_folder, f"{track_title}_tagged.mp3")

            ffmpeg_cmd = [
                ffmpeg_path, '-y',
                '-i', temp_mp3,          
                '-i', album_art,
                '-map', '0:a',
                '-map', '1:v',
                '-c', 'copy',
                '-id3v2_version', '3',
                '-metadata', f'title={track_title}',
                '-metadata', f'album={album_name}',
                '-metadata', f'artist={artist_name}',
                '-metadata', f'track={track_counter}',
                tagged_output
            ]

            subprocess.run(ffmpeg_cmd, creationflags=subprocess.CREATE_NO_WINDOW)

            # Replace original with tagged
            if os.path.exists(tagged_output):
                os.remove(temp_mp3)
                os.rename(tagged_output, final_output)
        else:
            tagged_output = os.path.join(album_folder, f"{track_title}_tagged.mp3")
            ffmpeg_cmd = [
                ffmpeg_path, '-y',
                '-i', temp_mp3,          
                '-metadata', f'title={track_title}',
                '-metadata', f'album={album_name}',
                '-metadata', f'artist={artist_name}',
                '-metadata', f'track={track_counter}',
                tagged_output
            ]

            subprocess.run(ffmpeg_cmd, creationflags=subprocess.CREATE_NO_WINDOW)

            # Replace original with tagged
            if os.path.exists(tagged_output):
                os.remove(temp_mp3)
                os.rename(tagged_output, final_output)
    status_label.config(text=f"Download complete: {album_name}") 
    
def audio_singles():
    link = url_entry.get().strip()
    album_name = album_entry.get().strip()
    album_art = artwork_entry.get().strip()
    download_dir = download_dir_entry.get().strip()

    if not link:
        messagebox.showerror("Error", "Please enter a valid URL.")
        return

    status_label.config(text="Downloading song...")
    root.update_idletasks()

    ydl_opts_info = {'quiet': True}
    with YoutubeDL(ydl_opts_info) as ydl:
        info_dict = ydl.extract_info(link, download=False)
        raw_title = info_dict.get('title', 'Unknown Song')
        track_title = Sanitise_filename(raw_title)
        artist_name = info_dict.get('uploader', 'Unknown Artist')
        album_name = album_name if album_name else track_title

    temp_output = os.path.join(download_dir, f"{track_title}.%(ext)s")
    temp_mp3 = os.path.join(download_dir, f"{track_title}.mp3")
    final_output = os.path.join(download_dir, f"{track_title}.mp3")

    ydl_opts_download = {
        'format': 'bestaudio/best',
        'outtmpl': temp_output,
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }
        ],
        'ffmpeg_location': ffmpeg_path,
        'progress_hooks': [my_hook],
        'quiet': True,
        'ignoreerrors': True,
    }

    with YoutubeDL(ydl_opts_download) as ydl:
        ydl.download([link])

    tagged_output = os.path.join(download_dir, f"{track_title}_tagged.mp3")

    if album_art:
        ffmpeg_cmd = [
            ffmpeg_path, '-y',
            '-i', temp_mp3,
            '-i', album_art,
            '-map', '0:a', '-map', '1:v',
            '-c', 'copy',
            '-id3v2_version', '3',
            '-metadata', f'title={track_title}',
            '-metadata', f'album={album_name}',
            '-metadata', f'artist={artist_name}',
            tagged_output
        ]
    else:
        ffmpeg_cmd = [
            ffmpeg_path, '-y',
            '-i', temp_mp3,
            '-id3v2_version', '3',
            '-metadata', f'title={track_title}',
            '-metadata', f'album={album_name}',
            '-metadata', f'artist={artist_name}',
            tagged_output
        ]

    subprocess.run(ffmpeg_cmd, creationflags=subprocess.CREATE_NO_WINDOW)

    if os.path.exists(tagged_output):
        os.remove(temp_mp3)
        os.rename(tagged_output, final_output)

    status_label.config(text=f"Download complete: {track_title}")


def video_playlists():
    link = url_entry.get().strip()
    album_name = album_entry.get().strip()
    album_art = artwork_entry.get().strip()
    download_dir = download_dir_entry.get().strip()

    if not link:
        messagebox.showerror("Error", "Please enter a valid URL.")
        return

    status_label.config(text="Extracting video playlist...")
    root.update_idletasks()

    # Default to using playlist title if no custom folder name is provided
    album_name = album_name if album_name else '%(playlist_title)s'

    outtmpl = os.path.join(download_dir, album_name, '%(playlist_index)s - %(title)s.%(ext)s')

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
        'outtmpl': outtmpl,
        'merge_output_format': 'mp4',
        'ignoreerrors': True,
        'quiet': True,
        'ffmpeg_location': ffmpeg_path,
        'progress_hooks': [my_hook]
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])
    
    status_label.config(text=f"Download complete: {album_name}") 
    
def video_singles():
    link = url_entry.get().strip()
    album_name = album_entry.get().strip()
    album_art = artwork_entry.get().strip()
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

# GUI helper functions
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

# GUI Setup
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
    tk.Button(root, text="Download Single Song", command=lambda: threading.Thread(target=audio_singles).start()).pack(pady=5)
    tk.Button(root, text="Download Video Playlist", command=lambda: threading.Thread(target=video_playlists).start()).pack(pady=5)
    tk.Button(root, text="Download Single Video", command=lambda: threading.Thread(target=video_singles).start()).pack(pady=5)

    # Status label
    status_label = tk.Label(root, text="", fg="blue")
    status_label.pack()

    root.mainloop()
except Exception as e:
    messagebox.showerror("Fatal Error", f"Something went wrong:\n{e}")
    if 'root' in locals():
        root.destroy()
    sys.exit(1)
