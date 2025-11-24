import os

# Application Configuration
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Asset Paths
SPACE_BG_PATH = os.path.join(BASE_DIR, "assets", "space_bg.gif")
PLANET_BG_PATH = os.path.join(BASE_DIR, "assets", "planet_bg.gif")
GALAXY_BG_PATH = os.path.join(BASE_DIR, "assets", "galaxy_bg.gif")
MENU_BG_PATH = os.path.join(BASE_DIR, "assets", "planet_menu.gif")
DIFFICULTY_BG_PATH = os.path.join(BASE_DIR, "assets", "difficulty_bg.gif")
START_IMG_PATH = os.path.join(BASE_DIR, "assets", "rocket_btn.png")
QUIT_IMG_PATH = os.path.join(BASE_DIR, "assets", "exit_btn.png")
BACK_IMG_PATH = os.path.join(BASE_DIR, "assets", "back_btn.png")

# Game Settings
APP_WIDTH = 960
APP_HEIGHT = 540
GAME_DURATION = 25
MAX_CHALLENGES = 10