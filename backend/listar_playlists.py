"""
Lista las playlists de tu canal con sus IDs completos.
Se corre una sola vez, para copiar el ID correcto.

Requiere las mismas variables de entorno que el backend
(YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN).
Si tenés un archivo .env en la misma carpeta, las va a leer solo.
"""

import os
import httpx
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.environ["YT_CLIENT_ID"]
CLIENT_SECRET = os.environ["YT_CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["YT_REFRESH_TOKEN"]


def get_access_token():
    resp = httpx.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": REFRESH_TOKEN,
            "grant_type": "refresh_token",
        },
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def main():
    access_token = get_access_token()

    resp = httpx.get(
        "https://www.googleapis.com/youtube/v3/playlists",
        params={"part": "snippet", "mine": "true", "maxResults": 50},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    resp.raise_for_status()
    data = resp.json()

    items = data.get("items", [])
    if not items:
        print("No se encontraron playlists en este canal.")
        return

    print("\nPlaylists encontradas:\n")
    for item in items:
        print(f"- {item['snippet']['title']}")
        print(f"  ID: {item['id']}\n")


if __name__ == "__main__":
    main()