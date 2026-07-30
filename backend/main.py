"""
Backend FastAPI: login simple + subida de videos a YouTube en streaming.
"""
from dotenv import load_dotenv
load_dotenv()

import os

from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from itsdangerous import URLSafeTimedSerializer, BadSignature
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
#from r2_storage import subir_a_r2, generar_url_firmada
import httpx
import r2
import asyncio
import uuid

import youtube

app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory="../frontend/static"),
    name="static"
)

templates = Jinja2Templates(
    directory="../frontend/templates"
)

# Permite que el frontend (servido desde otro origen) llame a esta API.
# En producción, reemplazá "*" por el dominio real de tu frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = os.environ["APP_SECRET_KEY"]
serializer = URLSafeTimedSerializer(SECRET_KEY)

# Usuarios permitidos: los definís vos como variable de entorno,
# formato "usuario1:clave1,usuario2:clave2"
USERS = dict(
    pair.split(":", 1) for pair in os.environ["APP_USERS"].split(",")
)

COOKIE_NAME = "session"
MAX_AGE_SECONDS = 60 * 60 * 24 * 30  # 30 días


def create_session_cookie(username: str) -> str:
    return serializer.dumps({"username": username})


def get_current_user(request: Request) -> str:
    token = request.cookies.get(COOKIE_NAME)

    if not token:
        raise HTTPException(status_code=401, detail="No autenticado")
    try:
        data = serializer.loads(token, max_age=MAX_AGE_SECONDS)
    except BadSignature:
        raise HTTPException(status_code=401, detail="Sesión inválida")
    return data["username"]


# funcion para que cuando entre a subir sin login
# lo redireccione a login y no de error
def require_user_or_login(request: Request):

    token = request.cookies.get(COOKIE_NAME)

    if not token:
        return RedirectResponse(
            "/login",
            status_code=302
        )

    try:

        data = serializer.loads(
            token,
            max_age=MAX_AGE_SECONDS
        )

        return data["username"]

    except BadSignature:

        return RedirectResponse(
            "/login",
            status_code=302
        )

def get_optional_user(request: Request):

    token = request.cookies.get(COOKIE_NAME)
    # No hay usuario logueado
    if not token:
        return None

    try:
        data = serializer.loads(
            token,
            max_age=MAX_AGE_SECONDS
        )

        return data["username"]

    except BadSignature:

        return None

@app.get("/test-r2")
async def test_r2():

    r2.list_files()

    return {
        "ok": True
    }

# para el inicio  
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    usuario = get_optional_user(request)

    return templates.TemplateResponse(
        request=request,
        name="inicio.html",
        context={
            "request": request,
            "usuario": usuario
        }
    )


# para subir videos
@app.get("/subir", response_class=HTMLResponse)
async def subir(request: Request):

    usuario = require_user_or_login(request)

    if isinstance(usuario, RedirectResponse):
        return usuario

    return templates.TemplateResponse(
        request=request,
        name="subir.html",
        context={
            "usuario": usuario,
            "active_page": "subir"
        }
    )
@app.get("/download/{filename:path}")
async def download(filename: str):

    url = r2.generate_download_url(
        filename
    )

    return {
        "url": url
    }

# todas las fechas (playlist de youtube)
@app.get("/partidos", response_class=HTMLResponse)
async def partidos(request: Request):

    playlists = await youtube.get_playlists()

    return templates.TemplateResponse(
        request=request,
        name="partidos.html",
        context={
            "active_page": "partidos",
            "playlists": playlists,
            "usuario": get_optional_user(request)
        }
    )

# partidos dentro de una fecha
@app.get("/partidos/{playlist_id}", response_class=HTMLResponse)
async def partidos_fecha(
    request: Request,
    playlist_id: str
):

    videos = await youtube.get_playlist_videos(
        playlist_id
    )

    #print("VIDEOS:")

    return templates.TemplateResponse(
        request=request,
        name="partidos_fecha.html",
        context={
            "active_page": "partidos",
            "videos": videos,
            "usuario": get_optional_user(request)
        }
    )

# para ver el fixture
@app.get("/fixture", response_class=HTMLResponse)
async def subir(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="fixture.html"
    )
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "usuario": get_optional_user(request)
        }
    )

@app.post("/login")
async def login(request: Request, response: Response):
    body = await request.json()
    username = body.get("username")
    password = body.get("password")

    if USERS.get(username) != password:
        raise HTTPException(status_code=401, detail="Usuario o clave incorrectos")

    token = create_session_cookie(username)
    response.set_cookie(
        COOKIE_NAME,
        token,
        max_age=MAX_AGE_SECONDS,
        httponly=True,
        samesite="lax",
        secure=False,  # requiere HTTPS (necesario en producción)
    )
    return {"ok": True, "username": username}

@app.get("/logout")
async def logout():

    response = RedirectResponse(
        "/",
        status_code=302
    )

    response.delete_cookie(
        key=COOKIE_NAME
    )
    return response

@app.post("/crear-upload")
async def crear_upload(request: Request):

    data = await request.json()

    filename = data["filename"]

    url = r2.create_upload_url(filename)

    return {
        "upload_url": url,
        "filename": filename
    }  

# funcion upload que funciona para r2 y para youtube
@app.post("/upload")
async def upload(
    request: Request
):

    title = request.headers.get(
        "X-Title",
        "Video hockey"
    )

    playlist_id = request.headers.get(
        "X-Playlist-ID"
    )

    if not playlist_id:
        raise HTTPException(
            status_code=400,
            detail="No se recibió playlist"
        )


    content_length = int(
        request.headers["Content-Length"]
    )

    content_type = request.headers.get(
        "Content-Type",
        "video/mp4"
    )


    description = request.headers.get(
        "X-Description",
        ""
    )


    # ===============================
    # INICIAR YOUTUBE
    # ===============================

    upload_url = await youtube.initiate_upload(
        title=title,
        description=description,
        content_length=content_length,
        content_type=content_type
    )


    # ===============================
    # INICIAR R2
    # ===============================

    filename = f"{title}.mp4"
    print("GUARDANDO EN R2:", repr(filename))


    upload_id = r2.initiate_upload(
        filename
    )


    # ===============================
    # VARIABLES DE CONTROL
    # ===============================

    part_number = 1
    youtube_offset = 0

    partes_r2 = []

    video_result = None


    # YouTube necesita mínimo 256 KB
    # Usamos 32 MB para que también sirva para R2
    #BUFFER_SIZE = 8 * 1024 * 1024
    PART_SIZE = 32 * 1024 * 1024

    buffer = bytearray()



    # Un único cliente HTTP
    async with httpx.AsyncClient(
        timeout=httpx.Timeout(
            600.0,
            connect=60.0
        )
       # timeout=None
    ) as client:


        # Leer archivo una sola vez
        async for chunk in request.stream():


            buffer.extend(chunk)



            # Cuando juntamos 8 MB
            #if len(buffer) >= BUFFER_SIZE:
            while len(buffer) >= PART_SIZE:

                data = bytes(buffer[:PART_SIZE])
                del buffer[:PART_SIZE]
                #data = bytes(buffer)



                # ===============================
                # SUBIR A YOUTUBE
                # ===============================

                #respuesta = await youtube.upload_chunk(

                respuesta, etag = await asyncio.gather( 
                    youtube.upload_chunk(
                        upload_url=upload_url,
                        chunk=data,
                        start=youtube_offset,
                        content_length=content_length,
                        content_type=content_type,
                        client=client
                    ),

                    asyncio.to_thread(
                        r2.upload_part,
                        filename,
                        upload_id,
                        part_number,
                        data
                    )
                )
            
                #if respuesta:
                #    video_result = respuesta



                # ===============================
                # SUBIR A R2
                # ===============================

                #etag = await asyncio.to_thread(
                #    r2.upload_part,
                #    filename,
                #    upload_id,
                #    part_number,
                #    data
                #)

                # ===============================
                # PROCESAR RESPUESTA YOUTUBE
                # ===============================

                if respuesta:

                    if respuesta.get("status") == 200:
                        video_result = respuesta["data"]

                    elif respuesta.get("range"):

                        ultimo_byte = int(
                            respuesta["range"].split("-")[1]
                        )
                        youtube_offset = ultimo_byte + 1

                # ===============================
                # GUARDAR PARTE R2
                # ===============================

                partes_r2.append(
                    {
                        "ETag": etag,
                        "PartNumber": part_number
                    }
                )

                #offset += len(data)
                part_number += 1


                #buffer.clear()



        # ===============================
        # ÚLTIMO BLOQUE
        # ===============================

        if buffer:


            data = bytes(buffer)



            # ---- YouTube ----

            respuesta = await youtube.upload_chunk(
                upload_url=upload_url,
                chunk=data,
                start=youtube_offset,
                content_length=content_length,
                content_type=content_type,
                client=client
            )


            if respuesta:
                #video_result = respuesta
                if respuesta.get("status") == 200:
                    video_result = respuesta["data"]



            # ---- R2 ----

            etag = await asyncio.to_thread(
                r2.upload_part,
                filename,
                upload_id,
                part_number,
                data
            )


            partes_r2.append(
                {
                    "ETag": etag,
                    "PartNumber": part_number
                }
            )



    # ===============================
    # FINALIZAR R2
    # ===============================

    await asyncio.to_thread(
        r2.complete_upload,
        filename,
        upload_id,
        partes_r2
    )



    if not video_result:

        raise HTTPException(
            status_code=500,
            detail="YouTube no devolvió el ID del video"
        )

    video_id = video_result["id"]

    # ===============================
    # AGREGAR A PLAYLIST
    # ===============================

    await youtube.add_to_playlist(
        video_id,
        playlist_id
    )



    return {
        "ok": True,
        "video_url":
            f"https://youtu.be/{video_id}",
        "r2_file":
            filename
    }


@app.get("/me")
async def me(username: str = Depends(get_current_user)):
    return {"username": username}


# endponit para listar las playlists
@app.get("/playlists")
async def playlists():

    return await youtube.get_playlists()

@app.get("/playlists/{playlist_id}/videos")
async def playlist_videos(playlist_id: str):

    return await youtube.get_playlist_videos(
        playlist_id
    )



# R2
'''
@app.get("/test-r2")
async def test():

    return r2.listar_bucket()'''