"""
Lógica de comunicación con la API de YouTube.

Responsabilidades:
- Obtener y refrescar el access token.
- Iniciar subidas resumables.
- Subir bloques de un video.
- Agregar videos a playlists.
- Obtener playlists.
- Obtener videos de una playlist.

No guarda videos en disco.
"""

import os
import time
import httpx
import config
import re

# ------------------------------
#  AUTENTICACION
# ------------------------------
async def get_access_token() -> str:
    """
    Devuelve un access token válido.

    Si el token almacenado todavía sirve,
    lo reutiliza. Si expiró, obtiene uno nuevo
    utilizando el refresh token.
    """

    """Devuelve un access_token válido, refrescándolo si hace falta."""

    if config._token_cache["access_token"] and time.time() < config._token_cache["expires_at"] - 60:
        return config._token_cache["access_token"]

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            config.TOKEN_URL,
            data={
                "client_id": config.CLIENT_ID,
                "client_secret": config.CLIENT_SECRET,
                "refresh_token": config.REFRESH_TOKEN,
                "grant_type": "refresh_token",
            },
        )

        #print("STATUS TOKEN:", resp.status_code)
        #print("RESPUESTA TOKEN:", resp.text)

        resp.raise_for_status()
        data = resp.json()
    


    config._token_cache["access_token"] = data["access_token"]
    config._token_cache["expires_at"] = time.time() + data["expires_in"]
    return config._token_cache["access_token"]


# ------------------------------
#  SUBIDA DE VIDEOS
# ------------------------------
async def initiate_upload(title: str, description: str, content_length: int, content_type: str) -> str:
    """
    Inicia una subida resumable en YouTube.

    Devuelve la URL de la sesión de subida.
    """
    access_token = await get_access_token()

    metadata = {
        "snippet": {"title": title, "description": description},
        "status": {"privacyStatus": "unlisted"},
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            config.UPLOAD_INIT_URL,
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

    """
    Envía un bloque del video a YouTube.

    Devuelve:
    - status 308 si YouTube recibió el bloque
      pero todavía falta más video.
    - status 200 cuando terminó la subida.
    """

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


    print("STATUS:", resp.status_code)
    print("RANGE:", resp.headers.get("Range"))


    # YouTube recibió el bloque,
    # pero todavía faltan bytes.
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


    print("ERROR YOUTUBE")
    print(resp.text)

    return {
        "status":resp.status_code,
        "range":resp.headers.get("Range")
    }

# -----------------------------
#  PLAYLISTS    
# -----------------------------
async def add_to_playlist(video_id: str, playlist_id: str) -> None:

    """
    Agrega un video a una playlist de YouTube.
    """

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
            config.PLAYLIST_INSERT_URL,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            json=body,
        )
        resp.raise_for_status()


async def get_playlists():

    """
    Obtiene las playlists del canal autenticado.
    """

    access_token = await get_access_token()

    playlists = []

    params = {
        "part": "snippet",
        "mine": "true",
        "maxResults": 50
    }

    async with httpx.AsyncClient() as client:

        resp = await client.get(
            config.PLAYLISTS_URL,
            headers={
                "Authorization": f"Bearer {access_token}"
            },
            params=params
        )

        #print("STATUS PLAYLISTS:", resp.status_code)
        #print("RESPUESTA PLAYLISTS:", resp.text)

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

# videos de un a fecha, lo voy a utilizar para tener los videos ordenados visualmente
def _numero_fecha(titulo: str) -> int:
    """
    Extrae el número de fecha del título del video.
    Ejemplo: "Fecha 3 - Equipo A vs Equipo B" -> 3
    """

    match = re.search(r"Fecha (\d+)", titulo)
    if match:
        return int(match.group(1))
    return 9999

# -----------------------------
# VIDEOS DE UNA PLAYLIST
# -----------------------------
async def get_playlist_videos(playlist_id: str):

    """
    Obtiene los videos pertenecientes a una playlist.
    """

    access_token = await get_access_token()

    params = {
        "part": "snippet",
        "playlistId": playlist_id,
        "maxResults": 50
    }

    async with httpx.AsyncClient() as client:

        resp = await client.get(
            config.PLAYLIST_ITEMS_URL,
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

            "playlistItemId": item["id"],

            "url":
                f"https://youtu.be/{snippet['resourceId']['videoId']}",

            "archivo": snippet["title"] + ".mp4"

        })

    # antes de devolver, ordeno los videos por número de fecha (extraído del título)
    videos.sort(key=lambda x: _numero_fecha(x["titulo"]))

    return videos

# metodo usado cuand elimine un video de una playlist, no elimina el video en si, solo de la playlist
async def delete_playlist_item(playlist_item_id: str):
    """
    Elimina la entrada de la playlist (no el video en sí).
    """
    access_token = await get_access_token()

    async with httpx.AsyncClient() as client:
        resp = await client.delete(
            config.PLAYLIST_ITEMS_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            params={"id": playlist_item_id},
        )
        resp.raise_for_status()

# obtener un video puntual para editar videos
async def get_video(video_id: str):
    """
    Obtiene el snippet completo de un video (para editar).
    """
    access_token = await get_access_token()

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            config.VIDEOS_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            params={"part": "snippet", "id": video_id},
        )
        resp.raise_for_status()
        data = resp.json()

    items = data.get("items", [])

    if not items:
        return None

    return items[0]["snippet"]


# -----------------------------
# ACTUALIZAR UN VIDEO (EDITAR)
# -----------------------------
async def update_video(video_id: str, title: str, description: str):
    """
    Actualiza título y descripción de un video ya subido.
    Mantiene intacto el resto del snippet (categoryId, tags, etc.),
    porque la API de YouTube pisa TODO lo que no se le mande en este part.
    """
    access_token = await get_access_token()

    snippet = await get_video(video_id)

    if snippet is None:
        raise ValueError("Video no encontrado")

    snippet["title"] = title
    snippet["description"] = description

    body = {
        "id": video_id,
        "snippet": snippet,
    }

    async with httpx.AsyncClient() as client:
        resp = await client.put(
            config.VIDEOS_URL,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            params={"part": "snippet"},
            json=body,
        )
        resp.raise_for_status()
        return resp.json()


# -----------------------------
# Eliminar un video de YouTube (no se usa en la app)
# -----------------------------
async def delete_video(video_id: str):
    """
    Elimina un video de YouTube.
    """
    access_token = await get_access_token()

    async with httpx.AsyncClient() as client:
        resp = await client.delete(
            "https://www.googleapis.com/youtube/v3/videos",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"id": video_id},
        )
        resp.raise_for_status() 