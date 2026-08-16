import os

BASE_DIR = os.path.dirname(
    os.path.realpath(__file__)
)

ACTIVITIES_FILE = os.path.join(
    BASE_DIR,
    "activities.json"
)

RECORDS_FILE = os.path.join(
    BASE_DIR,
    "time_records.json"
)

FONT_FILE = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

ITEMS_PER_PAGE = 4

DEFAULT_MINUTES = 30

MINUTES_STEP = 15

MIN_MINUTES = 15

SCREEN_WIDTH = 122
SCREEN_HEIGHT = 250

PAGE_ACTIVITY_LIST = 0
PAGE_DURATION = 1