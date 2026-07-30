"""
Lógica de comunicación con la API de YouTube.
No guarda nada en disco: todo se hace en streaming.
"""

import os
import time
import httpx

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
_token_cache = {"access_token": None, "expires_at": 0}


async def get_access_token() -> str:
    """Devuelve un access_token válido, refrescándolo si hace falta."""
    if _token_cache["access_token"] and time.time() < _token_cache["expires_at"] - 60:
        return _token_cache["access_token"]

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            TOKEN_URL,
            data={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "refresh_token": REFRESH_TOKEN,
                "grant_type": "refresh_token",
            },
        )
        resp.raise_for_status()
        data = resp.json()

    _token_cache["access_token"] = data["access_token"]
    _token_cache["expires_at"] = time.time() + data["expires_in"]
    return _token_cache["access_token"]


async def initiate_upload(title: str, description: str, content_length: int, content_type: str) -> str:
    """
    Abre una sesión de subida resumable en YouTube.
    Devuelve la URL a la que hay que mandar los bytes del video.
    """
    access_token = await get_access_token()

    metadata = {
        "snippet": {"title": title, "description": description},
        "status": {"privacyStatus": "unlisted"},
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            UPLOAD_INIT_URL,
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-Upload-Content-Length": str(content_length),
                "X-Upload-Content-Type": content_type,
                "Content-Type": "application/json",
            },
            json=metadata,
        )
        resp.raise_for_status()

    upload_url = resp.headers["Location"]
    return upload_url

async def upload_chunk(
    upload_url: str,
    chunk: bytes,
    start: int,
    content_length: int,
    content_type: str,
    client
):

    end = start + len(chunk) - 1

    #print("========== UPLOAD CHUNK ==========")
    #print("START:", start)
    #print("END:", end)
    #print("CHUNK SIZE:", len(chunk))
    #print("TOTAL:", content_length)


    resp = await client.put(
        upload_url,
        headers={
            "Content-Length": str(len(chunk)),
            "Content-Range": f"bytes {start}-{end}/{content_length}",
            "Content-Type": content_type,
        },
        content=chunk,
    )


   # print("STATUS:", resp.status_code)
   # print("RANGE:", resp.headers.get("Range"))



    if resp.status_code == 308:
       # print(
       # "YouTube aceptó hasta:",
       # resp.headers.get("Range")
       # )

        return {
            "status": 308,
            "range": resp.headers.get("Range")
        }

        # terminado
    if resp.status_code in (200,201):

        return {
            "status":200,
            "data":resp.json()
        }


   # print("ERROR YOUTUBE")
   # print(resp.text)

    return {
        "status":resp.status_code,
        "range":resp.headers.get("Range")
    }

async def add_to_playlist(video_id: str, playlist_id: str) -> None:
    """Inserta el video ya subido dentro de la playlist configurada."""
    access_token = await get_access_token()
    body = {
        "snippet": {
            "playlistId": playlist_id,
            "resourceId": {
                "kind": "youtube#video",
                "videoId": video_id
            },
        }
    }


    async with httpx.AsyncClient() as client:
        resp = await client.post(
            PLAYLIST_INSERT_URL,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            json=body,
        )
        resp.raise_for_status()


async def get_playlists():

    access_token = await get_access_token()

    playlists = []

    params = {
        "part": "snippet",
        "mine": "true",
        "maxResults": 50
    }

    async with httpx.AsyncClient() as client:

        resp = await client.get(
            PLAYLISTS_URL,
            headers={
                "Authorization": f"Bearer {access_token}"
            },
            params=params
        )

        resp.raise_for_status()

        data = resp.json()


    for item in data.get("items", []):

        playlists.append({
            "id": item["id"],
            "nombre": item["snippet"]["title"]
        })
        # Ordenar alfabéticamente por nombre
        playlists.sort(
        key=lambda x: x["nombre"].lower()
        )


    return playlists

async def get_playlist_videos(playlist_id: str):

    access_token = await get_access_token()

    params = {
        "part": "snippet",
        "playlistId": playlist_id,
        "maxResults": 50
    }

    async with httpx.AsyncClient() as client:

        resp = await client.get(
            PLAYLIST_ITEMS_URL,
            headers={
                "Authorization": f"Bearer {access_token}"
            },
            params=params
        )

        resp.raise_for_status()

    data = resp.json()

    videos = []

    for item in data.get("items", []):

        snippet = item["snippet"]

        description = snippet["description"]

        resultado = description.replace( 
            "Torneo Clausura 2026, Resultado: ",
            ""
        )

        videos.append({

            "titulo": snippet["title"],

            "resultado": resultado, 

            "videoId":
                snippet["resourceId"]["videoId"],

            "url":
                f"https://youtu.be/{snippet['resourceId']['videoId']}",

            "archivo": snippet["title"] + ".mp4"

        })

    return videos