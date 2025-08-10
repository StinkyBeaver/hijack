import os
import re
import requests
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC, error
from PyQt5.QtCore import QThread, pyqtSignal
import yt_dlp

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

def download_track(query, metadata, save_folder, catalog_mode, playlist_folder):
    bad_keywords = [
        "live", "karaoke", "cover", "remix", "instrumental",
        "official video", "lyric video", "video clip", "music video"
    ]

    def pick_best_result(entries):
        # Pick all official audio first
        official = [e for e in entries if "official audio" in e['title'].lower() or "official track" in e['title'].lower()]
        if official:
            return official[0]
        # Then pick first without any bad keywords
        for e in entries:
            title_lower = e['title'].lower()
            if not any(bad in title_lower for bad in bad_keywords):
                return e
        # Fallback to first entry
        return entries[0]

    title = sanitize_filename(metadata['title'])
    artist = sanitize_filename(metadata['artist'])
    album = sanitize_filename(metadata['album'])
    artwork_url = metadata.get('artwork_url')
    spotify_duration_ms = metadata.get('duration_ms', 0)

    target_folder = os.path.join(
        save_folder,
        playlist_folder if catalog_mode in ("playlist", "album") and playlist_folder else artist
    )

    os.makedirs(target_folder, exist_ok=True)
    mp3_path = os.path.join(target_folder, f"{title}.mp3")
    temp_filename = os.path.join(target_folder, f"temp_{title}.%(ext)s")

    search_query = f"{query} audio"

    opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'outtmpl': temp_filename.replace('\\', '/'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(f"ytsearch5:{search_query}", download=False)

        if 'entries' not in info or not info['entries']:
            raise Exception("No suitable results found")

        candidates = info['entries']

        def closest_by_duration(entries, target_ms):
            best = None
            best_diff = float('inf')
            for e in entries:
                if 'duration' in e:
                    diff = abs(e['duration'] * 1000 - target_ms)
                    if diff < best_diff:
                        best = e
                        best_diff = diff
            return best

        best_by_title = pick_best_result(candidates)
        best_by_duration = closest_by_duration(candidates, spotify_duration_ms)

        if best_by_duration and (best_by_duration == best_by_title or abs(best_by_duration['duration'] * 1000 - spotify_duration_ms) < 10000):
            chosen = best_by_duration
        else:
            chosen = best_by_title

        ydl.download([chosen['webpage_url']])

    final_mp3_path = temp_filename.replace("%(ext)s", "mp3")
    if not os.path.exists(final_mp3_path):
        raise Exception("Failed to download")

    img_path = None
    if artwork_url:
        try:
            img_data = requests.get(artwork_url).content
            img_path = os.path.join(target_folder, "cover_temp.jpg")
            with open(img_path, 'wb') as f:
                f.write(img_data)
        except:
            img_path = None

    try:
        audio = EasyID3(final_mp3_path)
    except error:
        audio = EasyID3()

    audio['title'] = title
    audio['artist'] = artist
    audio['album'] = album
    audio.save(final_mp3_path)

    if img_path:
        try:
            tags = ID3(final_mp3_path)
            with open(img_path, 'rb') as albumart:
                tags.add(APIC(encoding=3, mime='image/jpeg', type=3, desc='Cover', data=albumart.read()))
            tags.save(final_mp3_path, v2_version=3)
            os.remove(img_path)
        except Exception:
            pass

    os.rename(final_mp3_path, mp3_path)

class DownloaderThread(QThread):
    update_progress = pyqtSignal(int)
    update_status = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, query, metadata, save_folder, catalog_mode, playlist_folder):
        super().__init__()
        self.query = query
        self.metadata = metadata
        self.save_folder = save_folder
        self.catalog_mode = catalog_mode
        self.playlist_folder = playlist_folder

    def run(self):
        self.update_status.emit("Starting")
        try:
            download_track(self.query, self.metadata, self.save_folder, self.catalog_mode, self.playlist_folder)
            self.update_progress.emit(100)
            self.update_status.emit("Done")
        except Exception as e:
            import traceback
            err_msg = traceback.format_exc()
            print(f"Download thread crashed:\n{err_msg}")
            self.update_status.emit(f"Error: {e}")
        self.finished.emit()
