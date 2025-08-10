from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel,
    QFileDialog, QListWidget, QListWidgetItem, QProgressBar, QHBoxLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPainter, QBrush

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

class AeroWindow(QWidget):
    def __init__(self, spotify_api, downloader):
        super().__init__()
        self.spotify_api = spotify_api
        self.downloader = downloader

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
        from pathlib import Path
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
            tracks, catalog_mode, playlist_folder = self.spotify_api.get_tracks_from_spotify_url(url)
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

        thread = self.downloader.DownloaderThread(query, metadata, self.save_folder, catalog_mode, playlist_folder)
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
