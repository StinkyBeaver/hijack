import sys
from PyQt5.QtWidgets import QApplication
import spotify_api
import downloader
import ui_components

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ui_components.AeroWindow(spotify_api, downloader)
    window.show()
    sys.exit(app.exec_())
