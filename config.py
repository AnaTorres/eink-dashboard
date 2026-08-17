import os

BASE_DIR = os.path.dirname(
    os.path.realpath(__file__)
)

DATABASE_FILE = os.path.join(
    BASE_DIR,
    "actividades.db"
)

FONT_FILE = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

ITEMS_PER_PAGE = 4

DEFAULT_MINUTES = 10

MINUTES_STEP = 5

MIN_MINUTES = 5

SCREEN_WIDTH = 122
SCREEN_HEIGHT = 250

PAGE_ACTIVITY_LIST = 0
PAGE_DURATION = 1