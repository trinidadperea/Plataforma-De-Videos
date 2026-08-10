from fastapi import (
    APIRouter,
    Request,
    Response,
    HTTPException,
    Depends
)

from fastapi.responses import (
    HTMLResponse,
    RedirectResponse
)

from fastapi.templating import Jinja2Templates

import youtube
import r2

from auth import (
    create_session_cookie,
    get_current_user,
    get_optional_user,
    require_user_or_login
)

from config import (
    USERS,
    COOKIE_NAME,
    MAX_AGE_SECONDS
)

from upload_service import (
    obtener_datos_upload,
    upload_video
)


router = APIRouter()


templates = Jinja2Templates(
    directory="../frontend/templates"
)

#----------------------------------------------------------------------------

# INICIO
@router.get("/", response_class=HTMLResponse)
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

#SUBIR VIDEOS
@router.get("/subir", response_class=HTMLResponse)
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

#PARTIDOS
@router.get("/partidos", response_class=HTMLResponse)
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

#PARTIDOS DE UNA FECHA
@router.get("/partidos/{playlist_id}", response_class=HTMLResponse)
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

#PLAYLISTS
@router.get("/playlists")
async def playlists():

    return await youtube.get_playlists()

@router.get("/playlists/{playlist_id}/videos")
async def playlist_videos(playlist_id: str):

    return await youtube.get_playlist_videos(
        playlist_id
    )


@router.post("/crear-upload")
async def crear_upload(request: Request):

    data = await request.json()

    filename = data["filename"]

    url = r2.create_upload_url(filename)

    return {
        "upload_url": url,
        "filename": filename
    }  


#FIXTURE
@router.get("/fixture", response_class=HTMLResponse)
async def fixture(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="fixture.html"
    )


# LOGIN ----------------------------------------
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "usuario": get_optional_user(request)
        }
    )

@router.post("/login")
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

@router.get("/logout")
async def logout():

    response = RedirectResponse(
        "/",
        status_code=302
    )

    response.delete_cookie(
        key=COOKIE_NAME
    )
    return response

## ---------------------------------------------------

#UPLOAD 
@router.post("/upload")
async def upload(request: Request):

    (
        title,
        playlist_id,
        description,
        content_length,
        content_type
    ) = obtener_datos_upload(request)

    #print("========== DATOS UPLOAD ==========")
    #print("Título:", title)
    #print("Fecha incluida:", request.headers.get("X-Fecha"))
    #print("Playlist:", playlist_id)
    #print("Descripción:", description)
    #print("Content-Length:", content_length)
    #print("Content-Type:", content_type)
    #print("==================================")

    return await upload_video(
        request=request,
        title=title,
        playlist_id=playlist_id,
        description=description,
        content_length=content_length,
        content_type=content_type
    )
