# H!JACK - TAKE YOUR TRACKS BACK

**H!JACK** is a streamlined desktop utility for converting Spotify playlists, albums, or tracks into high-quality MP3 files. It preserves full metadata (title, artist, album, cover art) and allows flexible organization of output files. Built with Python and PyQt5, H!JACK provides a lightweight local solution for music cataloging and backup.

---

## Features

- Convert any **Spotify playlist, album, or single track** to MP3
- Supports large playlists (**100+ tracks with auto-pagination**)
- Organizes files by:
  - Artist & Album structure (`Artist/Album/Track.mp3`)
  - Playlist folder structure (`Playlist Name/Track.mp3`)
- Applies full **ID3 metadata**:
  - Title
  - Artist
  - Album
  - Embedded album artwork
- Custom download location
- Clean GUI with progress tracking

---

## Installation

Clone the repo:

git clone https://github.com/StinkyBeaver/hijack.git
cd hijack
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
pip install -r requirements.txt

## Run the app:

python hijack.py


## Created and maintained by StinkyBeaver 
GitHub: github.com/StinkyBeaver 

## License
 MIT — free for personal and commercial use. No cloud. No tracking. No bullshit.

