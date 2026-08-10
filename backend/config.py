import os
from dotenv import load_dotenv

from itsdangerous import URLSafeTimedSerializer


load_dotenv()


# ===============================
# SEGURIDAD
# ===============================

SECRET_KEY = os.environ["APP_SECRET_KEY"]

serializer = URLSafeTimedSerializer(
    SECRET_KEY
)


# ===============================
# USUARIOS
# ===============================

USERS = dict(
    pair.split(":", 1)
    for pair in os.environ["APP_USERS"].split(",")
)


# ===============================
# SESIÓN
# ===============================

COOKIE_NAME = "session"

MAX_AGE_SECONDS = 60 * 60 * 24 * 30


# ===============================
# UPLOAD
# ===============================

PART_SIZE = 32 * 1024 * 1024

# ===============================
# YOUTUBE
# ===============================
CLIENT_ID = os.environ["YT_CLIENT_ID"]
CLIENT_SECRET = os.environ["YT_CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["YT_REFRESH_TOKEN"]
PLAYLIST_ID = os.environ["YT_PLAYLIST_ID"]

TOKEN_URL = "https://oauth2.googleapis.com/token"

UPLOAD_INIT_URL = (
    "https://www.googleapis.com/upload/youtube/v3/videos"
    "?uploadType=resumable&part=snippet,status"
)

PLAYLIST_INSERT_URL = (
    "https://www.googleapis.com/youtube/v3/playlistItems?part=snippet"
)

PLAYLISTS_URL = "https://www.googleapis.com/youtube/v3/playlists"

PLAYLIST_ITEMS_URL = (
    "https://www.googleapis.com/youtube/v3/playlistItems"
)

# Cache simple del access_token en memoria (dura ~1 hora)
_token_cache = {
    "access_token": None,
     "expires_at": 0
}
