#!/usr/bin/env python3
import sys
import os
import re
import requests
from pathlib import Path
from dotenv import load_dotenv

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel,
    QFileDialog, QListWidget, QListWidgetItem, QProgressBar, QHBoxLayout
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPainter, QBrush

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC, error

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

class DownloadItem(QWidget):
    def __init__(self, track_name):
        super().__init__()
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        self.label = QLabel(track_name)
        self.progress = QProgressBar()
        self.status = QLabel("Queued")

        self.label.setStyleSheet("color: white;")
        self.status.setStyleSheet("color: white;")
        self.progress.setMaximumWidth(150)

        layout.addWidget(self.label)
        layout.addWidget(self.progress)
        layout.addWidget(self.status)
        self.setLayout(layout)

    def update_progress(self, value):
        self.progress.setValue(value)

    def update_status(self, status_text):
        self.status.setText(status_text)

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
            self.download_from_youtube()
            self.update_progress.emit(100)
            self.update_status.emit("Done")
        except Exception as e:
            import traceback
            err_msg = traceback.format_exc()
            print(f"Download thread crashed:\n{err_msg}")
            self.update_status.emit(f"Error: {e}")
        self.finished.emit()

    def download_from_youtube(self):
        title = sanitize_filename(self.metadata['title'])
        artist = sanitize_filename(self.metadata['artist'])
        album = sanitize_filename(self.metadata['album'])
        artwork_url = self.metadata.get('artwork_url')

        target_folder = os.path.join(
            self.save_folder,
            self.playlist_folder if self.catalog_mode in ("playlist", "album") and self.playlist_folder else artist
        )

        os.makedirs(target_folder, exist_ok=True)
        mp3_path = os.path.join(target_folder, f"{title}.mp3")
        temp_filename = os.path.join(target_folder, f"temp_{title}.%(ext)s")

        opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'outtmpl': temp_filename.replace('\\', '/'),
            'progress_hooks': [self.ydl_hook],
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{self.query}", download=True)
            if 'entries' in info:
                info = info['entries'][0]

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

    def ydl_hook(self, d):
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded_bytes = d.get('downloaded_bytes', 0)
            if total_bytes:
                percent = int(downloaded_bytes / total_bytes * 100)
                self.update_progress.emit(percent)
                self.update_status.emit(f"Downloading... {percent}%")
        elif d['status'] == 'finished':
            self.update_progress.emit(100)
            self.update_status.emit("Processing...")

class AeroWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hijack v1.1")
        self.setGeometry(200, 200, 600, 400)
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

        self.queue_list = QListWidget()
        self.queue_list.setStyleSheet("background: rgba(0,0,0,0.3); color: white;")
        layout.addWidget(self.queue_list)

        self.setLayout(layout)
        self.save_folder = str(Path.home() / "Downloads")

        self.threads = []
        self.download_queue = []
        self.download_items = []
        self.current_download_index = 0
        self.downloading = False

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Save Folder", self.save_folder)
        if folder:
            self.save_folder = folder
            self.status.setText(f"Save folder: {self.save_folder}")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        color = QColor(0, 0, 0, 150)
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 15, 15)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_start_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self._drag_start_pos)
            event.accept()

    def start_download(self):
        url = self.url_input.text().strip()
        if not url:
            self.status.setText("Please enter a Spotify URL.")
            return

        self.status.setText("Fetching tracks...")
        try:
            tracks, catalog_mode, playlist_folder = self.get_tracks_from_spotify_url(url)
        except Exception as e:
            self.status.setText(f"Error: {e}")
            return

        if not tracks:
            self.status.setText("No tracks found.")
            return

        self.status.setText(f"{len(tracks)} tracks found. Preparing downloads...")

        self.queue_list.clear()
        self.download_queue = tracks
        self.download_items = []
        self.threads = []
        self.current_download_index = 0
        self.downloading = False

        for query, _ in tracks:
            item_widget = DownloadItem(query)
            list_item = QListWidgetItem(self.queue_list)
            list_item.setSizeHint(item_widget.sizeHint())
            self.queue_list.addItem(list_item)
            self.queue_list.setItemWidget(list_item, item_widget)
            self.download_items.append(item_widget)

        self.start_next_download(catalog_mode, playlist_folder)

    def start_next_download(self, catalog_mode, playlist_folder):
        if self.current_download_index >= len(self.download_queue):
            self.status.setText("All downloads complete.")
            return

        query, metadata = self.download_queue[self.current_download_index]
        item_widget = self.download_items[self.current_download_index]

        thread = DownloaderThread(query, metadata, self.save_folder, catalog_mode, playlist_folder)
        thread.update_progress.connect(item_widget.update_progress)
        thread.update_status.connect(item_widget.update_status)
        thread.finished.connect(self.download_finished)
        thread.start()

        self.threads.append(thread)
        self.status.setText(f"Downloading track {self.current_download_index + 1} of {len(self.download_queue)}")
        self.downloading = True

    def download_finished(self):
        self.current_download_index += 1
        self.downloading = False
        self.start_next_download(self.threads[-1].catalog_mode, self.threads[-1].playlist_folder)

    def get_tracks_from_spotify_url(self, url):
        sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET
        ))

        spotify_id = url.split("/")[-1].split("?")[0]
        url_type = url.split("/")[-2]

        tracks = []
        playlist_folder = None

        if url_type == "track":
            track = sp.track(spotify_id)
            metadata = self.extract_metadata(track)
            tracks.append((f"{track['name']} {track['artists'][0]['name']}", metadata))
            return tracks, "artist_album", None

        elif url_type == "album":
            album = sp.album(spotify_id)
            playlist_folder = sanitize_filename(album['name'])
            for item in sp.album_tracks(spotify_id)['items']:
                track = sp.track(item['id'])
                metadata = self.extract_metadata(track)
                tracks.append((f"{track['name']} {track['artists'][0]['name']}", metadata))
            return tracks, "album", playlist_folder

        elif url_type == "playlist":
            playlist = sp.playlist(spotify_id)
            playlist_folder = sanitize_filename(playlist['name'])
            offset = 0
            limit = 100
            while True:
                results = sp.playlist_tracks(spotify_id, offset=offset, limit=limit)
                items = results.get("items", [])
                if not items:
                    break
                for item in items:
                    track = item['track']
                    if track:
                        metadata = self.extract_metadata(track)
                        tracks.append((f"{track['name']} {track['artists'][0]['name']}", metadata))
                offset += limit
            return tracks, "playlist", playlist_folder

        else:
            raise Exception("Unsupported Spotify URL type.")

    def extract_metadata(self, track):
        return {
            "title": track['name'],
            "artist": track['artists'][0]['name'],
            "album": track['album']['name'],
            "artwork_url": track['album']['images'][0]['url'] if track['album']['images'] else None
        }

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AeroWindow()
    window.show()
    sys.exit(app.exec_())
