# Hijack v1.1

Hijack is a Spotify to MP3 downloader using YouTube as the source, wrapped in a slick PyQt5 GUI.

---

## Quick Start

1. **Configure your Spotify API credentials**
   Rename `example.env.txt` to `.env` and fill in your Spotify API keys:
   SPOTIFY_CLIENT_ID=your_client_id
   SPOTIFY_CLIENT_SECRET=your_client_secret


2. **Run the app**


3. **Use the GUI**
Paste your Spotify track, album, or playlist URL and choose a save folder.
The app queues downloads and keeps album/playlist integrity.

---

## Notes

- Make sure you have Python 3 and required dependencies installed (`pip install -r requirements.txt`).
- This package does **not** include Spotify API keys — you need to supply your own in the `.env` file.
- Check `example.env.txt` for environment variable setup instructions.

---

Enjoy the tunes, responsibly.

---

*This is free software — use at your own risk.*

## Credits

- [Spotipy](https://spotipy.readthedocs.io/) — Spotify Web API client
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — YouTube downloader fork
- [Mutagen](https://mutagen.readthedocs.io/) — Audio metadata handling
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) — Python GUI framework

Thanks to all open-source maintainers for making these tools available!
