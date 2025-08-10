# HIJACK — Take Your Tracks Back 

**Hijack** is a sleek desktop tool that lets you download any **Spotify playlist, album, or single** as clean, tagged MP3 files — fully offline, fully yours. Built in Python with a PyQt GUI, it's a no-nonsense way to take control of your music library.

---

#V1.2 UNOFFICIAL RELEASE - WIP

Split everything into multiple files/modules for clarity and maintainability.

    downloader.py now handles all the actual downloading and tagging logic.
    Main UI code lives seperate

Improved YouTube Search and Filtering Logic (big deal)

    Replaced the original simple search query with a more refined one:

    Added filters in the YouTube search query to exclude obvious “music videos,” “live,” “karaoke,” and other unwanted stuff.

    Added logic to parse multiple search results and pick the best candidate by:

        Checking for keywords like “official audio” or “official track” in the title.

        Excluding entries with “live,” “cover,” “remix,” “instrumental,” etc.

     Added comparison of YouTube video duration vs Spotify track duration (in milliseconds) to pick the closest match.
        (This helped avoid weird 30-second clips or hour-long live concerts being downloaded mistakenly.)

Error Handling & Reporting

    More robust try-except around the download process, with tracebacks printed for debugging.

    UI status messages updated properly on error or progress.


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
