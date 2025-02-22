import os
import subprocess
import sys
from pathlib import Path

# Required Python packages
required_packages = ["yt-dlp", "pillow", "mutagen"]

def install_packages(packages):
    for package in packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            print(f"📦 Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_packages(required_packages)

from yt_dlp import YoutubeDL
from PIL import Image
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, error

def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except FileNotFoundError:
        return False

if not check_ffmpeg():
    print("❌ FFmpeg is not installed! Please install it manually.")
    sys.exit(1)

# Get the user's Downloads folder
downloads_path = Path.home() / "Downloads"

def main_menu():
    while True:
        print("\n🎵 YouTube Downloader 🎥")
        print("[1] Download Audio (MP3 with Cover Art)")
        print("[2] Download Video (MP4)")
        print("[3] Exit")
        choice = input("Enter your choice (1/2/3): ")

        if choice == "3":
            print("👋 Exiting...")
            break

        video_url = input("📌 Enter YouTube video URL: ")

        if choice == "1":
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': str(downloads_path / '%(title)s.mp3'),
                'postprocessors': [
                    {
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192'
                    }
                ],
                'writethumbnail': True,
            }

            print("⬇️ Downloading audio and cover art...")
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                title = info.get("title", "Unknown Title")
                output_audio = downloads_path / f"{title}.mp3"
                output_thumbnail = downloads_path / f"{title}.jpg"

            for ext in ["jpg", "png", "webp"]:
                possible_thumbnail = downloads_path / f"{title}.{ext}"
                if possible_thumbnail.exists():
                    possible_thumbnail.rename(output_thumbnail)
                    break

            if output_thumbnail.exists():
                with Image.open(output_thumbnail) as img:
                    img = img.resize((500, 500))
                    img.save(output_thumbnail)

            def embed_cover(mp3_file, cover_image, title):
                try:
                    audio = MP3(mp3_file, ID3=ID3)
                    try:
                        audio.add_tags()
                    except error:
                        pass

                    with open(cover_image, "rb") as img:
                        audio.tags.add(APIC(
                            encoding=3,
                            mime="image/jpeg",
                            type=3,
                            desc="Cover",
                            data=img.read()
                        ))

                    audio.tags["TIT2"] = TIT2(encoding=3, text=title)
                    audio.save()
                    print("✅ Cover art and metadata added successfully!")
                except Exception as e:
                    print(f"❌ Failed to embed cover art: {e}")

            if output_audio.exists() and output_thumbnail.exists():
                embed_cover(output_audio, output_thumbnail, title)

            print(f"🎵 Audio download complete! Saved in {downloads_path}")

        elif choice == "2":
            output_file = downloads_path / "music_video.mp4"
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
                'outtmpl': str(output_file),
                'merge_output_format': 'mp4'
            }

            print("⬇️ Downloading video...")
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])

            print(f"🎬 Video downloaded successfully! Saved in {downloads_path}")
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

main_menu()
