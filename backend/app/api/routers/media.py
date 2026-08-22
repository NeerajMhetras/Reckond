from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session

from app.core.config import settings

from app.database.dependencies import get_db

from app.models.media.entertainment import MediaType

from app.schemas.media.search import SearchResult
from app.schemas.media.entertainment import MediaResponse,MediaImportRequest, MediaListResponse

from app.services.providers.tmdb import TMDBProvider
from app.services.providers.google_books import GoogleBooksProvider
from app.services.providers.igdb import IGDBProvider


from app.services.search_service import SearchService
from app.services.media_service import MediaService

router = APIRouter(
    prefix="/media",
    tags=["Media"]
)

tmdb = TMDBProvider(settings.TMDB_API_KEY)
google_books = GoogleBooksProvider(settings.GOOGLE_BOOKS_API_KEY)
igdb = IGDBProvider(
    client_id=settings.IGDB_CLIENT_ID,
    client_secret=settings.SECRET_KEY
)


@router.get(
    "/",
    response_model=MediaListResponse
)
async def get_media_list(
    media_type: MediaType | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    
    media_service = MediaService(
        tmdb_provider=tmdb,
        google_books_provider=google_books,
        igdb_provider=igdb
    )

    return media_service.get_all_media(
        db=db,
        media_type=media_type,
        skip=skip,
        limit=limit
    )


@router.get(
    "/search",
    response_model=list[SearchResult]
)
async def search_media(
    query: str = Query(..., min_length=1),
    media_type: MediaType = Query(...)
):
    search_service = SearchService(tmdb_provider=tmdb, 
                                   google_books_provider=google_books, 
                                   igdb_provider= igdb)

    try:
        return await search_service.search(query=query,media_type=media_type)
    except ValueError as e:
        raise HTTPException(status_code=400,
                            detail=str(e))


@router.post("/import", response_model=MediaResponse)

async def import_media_endpoint(
    request: MediaImportRequest,
    db: Session = Depends(get_db)
):
    media_service = MediaService(tmdb_provider= tmdb, google_books_provider = google_books, igdb_provider=igdb)
    try:
        media = await media_service.import_media(
            db=db,
            external_id=request.external_id,
            media_type=request.media_type
        )
        return media
    except ValueError as e:
        raise HTTPException(status_code=400,detail=str(e))


@router.get("/{media_id}", response_model=MediaResponse)

async def get_media(
    media_id: int,
    db: Session = Depends(get_db)
):
    media_service = MediaService(
        tmdb_provider=tmdb,
        google_books_provider=google_books,
        igdb_provider=igdb
    )
    media = media_service.get_media_by_id(media_id=media_id,db=db)

    if not media:
        raise HTTPException(
            status_code = 404,
            detail="Media not found"
        )

    return media
