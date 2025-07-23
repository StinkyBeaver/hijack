# HIJACK — Take Your Tracks Back 

**Hijack** is a sleek desktop tool that lets you download any **Spotify playlist, album, or single** as clean, tagged MP3 files — fully offline, fully yours. Built in Python with a PyQt GUI, it's a no-nonsense way to take control of your music library.

---

## Features

- 🎵 Download **tracks, albums, or full playlists** from Spotify
- 🧠 Smart queue system with real-time status + progress bars
- 📁 Organized output:
  - `Artist/Album/Track.mp3` for albums
  - `Playlist Name/Track.mp3` for playlists
- 🏷️ Automatically applies full **ID3 metadata**:
  - Title
  - Artist
  - Album
  - Embedded cover art
- 💾 Custom download folder
- 💻 Lightweight GUI (PyQt5) — fast and responsive

---

## 📦 Installation (From Source)

```bash
git clone https://github.com/StinkyBeaver/hijack.git
cd hijack
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```
---

## 📂 .env Setup

Place a .env file in the same directory as hijack.py.
You can rename the included example env.txt to .env and fill in your Spotify API credentials:

SPOTIFY_CLIENT_ID=your_client_id

SPOTIFY_CLIENT_SECRET=your_client_secret

---

## ▶️ Running Hijack

python hijack.py

---

## 👨‍💻 Credits

    Developed by StinkyBeaver

    Powered by:

        spotipy

        yt-dlp

        mutagen

        PyQt5
