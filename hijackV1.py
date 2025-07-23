
import sys
import os
import re
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QFileDialog, QProgressBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPainter, QBrush
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC, error

from dotenv import load_dotenv
load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

def sanitize_filename(name):
    return re.sub(r'[\/*?:"<>|]', "", name)

class DownloaderThread(QThread):
    update_progress = pyqtSignal(int, str)
    finished = pyqtSignal()

    def __init__(self, parent, url):
        super().__init__()
        self.parent = parent
        self.url = url

    def run(self):
        self.parent._download_spotify_url(self.url, self.update_progress)
        self.finished.emit()

class AeroWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MPFree Aero Edition")
        self.setGeometry(200, 200, 480, 220)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        self.label = QLabel("Enter Spotify URL (track, album, playlist):")
        self.label.setFont(QFont("Segoe UI", 11))
        self.label.setStyleSheet("color: white;")
        layout.addWidget(self.label)

        self.url_input = QLineEdit()
        self.url_input.setFont(QFont("Segoe UI", 10))
        self.url_input.setStyleSheet("background: rgba(255, 255, 255, 0.2); color: white; border: none; padding: 8px; border-radius: 5px;")
        layout.addWidget(self.url_input)

        self.folder_button = QPushButton("Choose Save Folder")
        self.folder_button.clicked.connect(self.choose_folder)
        layout.addWidget(self.folder_button)

        self.download_button = QPushButton("Download MP3s")
        self.download_button.clicked.connect(self.start_download)
        layout.addWidget(self.download_button)

        self.status = QLabel("")
        self.status.setFont(QFont("Segoe UI", 9))
        self.status.setStyleSheet("color: white;")
        layout.addWidget(self.status)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        self.setLayout(layout)

        from pathlib import Path
        self.save_folder = str(Path.home() / "Downloads")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_start_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self._drag_start_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_start_pos = None

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Save Folder", self.save_folder)
        if folder:
            self.save_folder = folder
            self.status.setText(f"Save folder: {self.save_folder}")

    def start_download(self):
        url = self.url_input.text().strip()
        if not url:
            self.status.setText("Please enter a Spotify URL.")
            return
        self.status.setText("Starting download...")
        self.thread = DownloaderThread(self, url)
        self.thread.update_progress.connect(self.update_progress)
        self.thread.finished.connect(self.download_finished)
        self.thread.start()

    def update_progress(self, value, message):
        self.progress.setValue(value)
        self.status.setText(message)

    def download_finished(self):
        self.status.setText("All downloads complete.")
        self.progress.setValue(100)

    def _download_spotify_url(self, spotify_url, signal):
        sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET
        ))

        spotify_id = spotify_url.split("/")[-1].split("?")[0]
        url_type = spotify_url.split("/")[-2]

        tracks = []
        playlist_folder = None

        if url_type == "track":
            track = sp.track(spotify_id)
            metadata = self.extract_metadata(track)
            tracks.append((f"{track['name']} {track['artists'][0]['name']}", metadata))
            catalog_mode = "artist_album"

        elif url_type == "album":
            album_tracks = sp.album_tracks(spotify_id)
            for item in album_tracks['items']:
                track = sp.track(item['id'])
                metadata = self.extract_metadata(track)
                tracks.append((f"{track['name']} {track['artists'][0]['name']}", metadata))
            catalog_mode = "artist_album"

        elif url_type == "playlist":
            playlist = sp.playlist(spotify_id)
            playlist_folder = sanitize_filename(playlist['name'])
            offset = 0
            limit = 100
            while True:
                playlist_tracks = sp.playlist_tracks(spotify_id, offset=offset, limit=limit)
                items = playlist_tracks.get('items', [])
                if not items:
                    break
                for item in items:
                    track = item['track']
                    if track is None:
                        continue
                    metadata = self.extract_metadata(track)
                    tracks.append((f"{track['name']} {track['artists'][0]['name']}", metadata))
                offset += limit
            catalog_mode = "playlist"

        else:
            signal.emit(0, "Unsupported Spotify URL type.")
            return

        total = len(tracks)
        for i, (query, metadata) in enumerate(tracks):
            signal.emit(int(((i + 1) / total) * 100), f"Downloading {i + 1}/{total}: {query}")
            self.download_from_youtube(query, metadata, catalog_mode, playlist_folder)

    def extract_metadata(self, track):
        return {
            "title": track['name'],
            "artist": track['artists'][0]['name'],
            "album": track['album']['name'],
            "artwork_url": track['album']['images'][0]['url'] if track['album']['images'] else None
        }

    def download_from_youtube(self, query, metadata, catalog_mode="artist_album", playlist_folder=None):
        title = sanitize_filename(metadata['title'])
        artist = sanitize_filename(metadata['artist'])
        album = sanitize_filename(metadata['album'])
        artwork_url = metadata.get('artwork_url')

        if catalog_mode == "playlist" and playlist_folder:
            target_folder = os.path.join(self.save_folder, playlist_folder)
        else:
            target_folder = os.path.join(self.save_folder, artist, album)

        os.makedirs(target_folder, exist_ok=True)
        mp3_path = os.path.join(target_folder, f"{title}.mp3")
        temp_filename = os.path.join(target_folder, f"temp_{title}.%(ext)s")

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

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(f"ytsearch:{query}", download=True)
                if 'entries' in info:
                    info = info['entries'][0]
        except Exception:
            return

        final_mp3_path = temp_filename.replace("%(ext)s", "mp3")
        if not os.path.exists(final_mp3_path):
            return

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

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        color = QColor(0, 0, 0, 150)
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 15, 15)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AeroWindow()
    window.show()
    sys.exit(app.exec_())
