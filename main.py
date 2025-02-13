import os
import subprocess
import sys

# Required Python packages
required_packages = ["yt-dlp", "pillow", "mutagen"]

# Function to install missing packages
def install_packages(packages):
    for package in packages:
        try:
            __import__(package.replace("-", "_"))  # Try importing (yt-dlp -> yt_dlp)
        except ImportError:
            print(f"📦 Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Install required packages
install_packages(required_packages)

# Import after installation
from yt_dlp import YoutubeDL
from PIL import Image
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, error

# Check if FFmpeg is installed
def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except FileNotFoundError:
        return False

if not check_ffmpeg():
    print("❌ FFmpeg is not installed! Please install it manually.")
    print("Linux: sudo apt install ffmpeg  |  Mac: brew install ffmpeg  |  Windows: Download from https://ffmpeg.org/")
    sys.exit(1)

# Get user choice
print("\n🎵 YouTube Downloader 🎥")
print("[1] Download Audio (MP3 with Cover Art)")
print("[2] Download Video (MP4)")
choice = input("Enter your choice (1/2): ")

# Get YouTube URL
video_url = input("📌 Enter YouTube video URL: ")

if choice == "1":
    # Download audio and thumbnail
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s',  # Save as video title
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            }
        ],
        'writethumbnail': True,  # Download thumbnail
        'postprocessor_args': [
            '-metadata', 'title=YouTube Audio',
            '-metadata', 'artist=Unknown Artist'
        ],
        'merge_output_format': 'mp3'
    }

    print("⬇️ Downloading audio and cover art...")
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)
        title = info.get("title", "Unknown Title")
        artist = info.get("uploader", "Unknown Artist")
        output_audio = f"{title}.mp3"
        output_thumbnail = f"{title}.jpg"

    # Find the downloaded thumbnail file (varies by format)
    for ext in ["jpg", "png", "webp"]:
        possible_thumbnail = f"{title}.{ext}"
        if os.path.exists(possible_thumbnail):
            os.rename(possible_thumbnail, output_thumbnail)
            break

    # Resize the cover art
    if os.path.exists(output_thumbnail):
        with Image.open(output_thumbnail) as img:
            img = img.resize((500, 500))  # Resize to 500x500
            img.save(output_thumbnail)

    # Embed the cover art and metadata into the MP3 file using Mutagen
    def embed_cover(mp3_file, cover_image, title, artist):
        try:
            audio = MP3(mp3_file, ID3=ID3)
            try:
                audio.add_tags()
            except error:
                pass
            
            with open(cover_image, "rb") as img:
                audio.tags.add(APIC(
                    encoding=3,  # UTF-8
                    mime="image/jpeg",  # Image format
                    type=3,  # Cover (front)
                    desc="Cover",
                    data=img.read()
                ))

            audio.tags["TIT2"] = TIT2(encoding=3, text=title)  # Set title
            audio.tags["TPE1"] = TPE1(encoding=3, text=artist)  # Set artist
            audio.save()
            print("✅ Cover art and metadata added successfully!")
        except Exception as e:
            print(f"❌ Failed to embed cover art: {e}")

    # Embed cover art into MP3
    if os.path.exists(output_audio) and os.path.exists(output_thumbnail):
        embed_cover(output_audio, output_thumbnail, title, artist)

    print(f"🎵 Audio download complete with cover art! Saved as {output_audio}")

elif choice == "2":
    # Download video
    output_file = "music_video.mp4"
    
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
        'outtmpl': output_file,
        'merge_output_format': 'mp4'
    }

    print("⬇️ Downloading video...")
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

    print(f"🎬 Video downloaded successfully! Saved as {output_file}")

else:
    print("❌ Invalid choice. Please restart and select 1 or 2.")
