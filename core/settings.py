import os

class Settings:
    TITLE = "V-Sports Launcher"
    S_WIDTH = 1280
    S_HEIGHT = 720
    FPS = 60
    BACKGROUND_COLOR = (12, 18, 35)
    TEXT_COLOR = (240, 240, 240)
    HIGHLIGHT_COLOR = (64, 176, 255)

    ROOT_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), os.pardir))
    ASSETS_DIR = os.path.join(ROOT_DIR, "assets")
    FONT_PATH = os.path.join(ASSETS_DIR, "font", "Font.otf")
    MENU_BACKGROUND_IMAGE = os.path.join(ASSETS_DIR, "decoration", "Background.jpeg")
    MAIN_TITLE_IMAGE = os.path.join(ASSETS_DIR, "decoration", "Title.jpeg")
    MUSIC_FILES = [
        os.path.join(ASSETS_DIR, "music", "Changing-Seasons.mp3"),
        os.path.join(ASSETS_DIR, "music", "Everything-Everything.mp3"),
        os.path.join(ASSETS_DIR, "music", "Slingshot_1.mp3"),
    ]
