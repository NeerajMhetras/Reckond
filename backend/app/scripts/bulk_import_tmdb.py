import asyncio
import httpx

from app.database.database import SessionLocal
from app.models.media.entertainment import MediaType
from app.services.media_service import MediaService
from app.core.config import settings
from app.services.providers.tmdb import TMDBProvider
from app.services.providers.google_books import GoogleBooksProvider
from app.services.providers.igdb import IGDBProvider

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


CONCURRENCY = 5

TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_API_KEY = settings.TMDB_API_KEY
GOOGLE_BOOKS_API_KEY = settings.GOOGLE_BOOKS_API_KEY
IGDB_CLIENT_ID = settings.IGDB_CLIENT_ID
IGDB_CLIENT_SECRET = settings.IGDB_CLIENT_SECRET_KEY

tmdb_retry = retry(
    stop=stop_after_attempt(10),
    wait=wait_exponential(multiplier=1, min=2, max=6),
    retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException)),
    reraise=True 
)

@tmdb_retry
async def get_tmdb_ids(
    client: httpx.AsyncClient,
    api_key: str,
    media_type: str,
    endpoint: str,
    pages: int
):
    ids = []

    for page in range(1, pages + 1):

        url = f"{TMDB_BASE_URL}/{media_type}/{endpoint}"

        response = await client.get(
            url,
            params={
                "api_key": api_key,
                "page": page
            }
        )

        response.raise_for_status()

        data = response.json()

        for item in data.get("results", []):
            ids.append(
                str(item["id"])
            )

        print(
            f"Collected {media_type} page "
            f"{page}/{pages}"
        )

    return ids

async def import_one(
    external_id: str,
    media_type: MediaType,
    semaphore: asyncio.Semaphore
):
    async with semaphore:

        db = SessionLocal()

        try:
            tmdb_provider = TMDBProvider(TMDB_API_KEY)
            google_books = GoogleBooksProvider(
                GOOGLE_BOOKS_API_KEY
            )
            igdb_provider = IGDBProvider(
                client_id=IGDB_CLIENT_ID,
                client_secret=IGDB_CLIENT_SECRET
            )

            import_service = MediaService(
                tmdb_provider=tmdb_provider,
                google_books_provider=google_books,
                igdb_provider=igdb_provider
            )

            result = await import_service.import_media(
                db=db,
                external_id=external_id,
                media_type=media_type
            )

            return {
                "success": True,
                "title": result.title,
                "external_id": external_id
            }

        except Exception as e:

            return {
                "success": False,
                "external_id": external_id,
                "error": str(e)
            }

        finally:
            db.close()

async def import_batch(
    external_ids: list[str],
    media_type: MediaType
):

    semaphore = asyncio.Semaphore(
        CONCURRENCY
    )

    total = len(external_ids)

    tasks = [
        import_one(
            external_id=external_id,
            media_type=media_type,
            semaphore=semaphore
        )
        for external_id in external_ids
    ]

    results = []

    completed = 0

    for task in asyncio.as_completed(tasks):

        result = await task

        completed += 1

        if result["success"]:

            print(
                f"[{completed}/{total}] "
                f"✓ {result['title']}"
            )

        else:

            print(
                f"[{completed}/{total}] "
                f"✗ {result['external_id']} "
                f"→ {result['error']}"
            )

        results.append(result)

    return results

async def bulk_import(
    api_key: str,
    movie_pages: int = 10,
    series_pages: int = 10
):
    async with httpx.AsyncClient(
        timeout=60.0
    ) as client:

        print("\nCollecting movies...")

        movie_ids = await get_tmdb_ids(
            client=client,
            api_key=api_key,
            media_type="movie",
            endpoint="top_rated",
            pages=movie_pages
        )

        print(
            f"\nCollected {len(movie_ids)} movies"
        )

        print("\nCollecting series...")

        series_ids = await get_tmdb_ids(
            client=client,
            api_key=api_key,
            media_type="tv",
            endpoint="top_rated",
            pages=series_pages
        )

        print(
            f"\nCollected {len(series_ids)} series"
        )

    print("\n========================")
    print("IMPORTING MOVIES")
    print("========================")

    movie_results = await import_batch(
        movie_ids,
        MediaType.MOVIE
    )

    movie_success = sum(
        result["success"]
        for result in movie_results
    )

    movie_failed = (
        len(movie_results) - movie_success
    )

    print("\n========================")
    print("IMPORTING SERIES")
    print("========================")

    series_results = await import_batch(
        series_ids,
        MediaType.SERIES
    )

    series_success = sum(
        result["success"]
        for result in series_results
    )

    series_failed = (
        len(series_results) - series_success
    )

    print("\n========================")
    print("IMPORT COMPLETE")
    print("========================")

    print(
        f"Movies imported: {movie_success}"
    )

    print(
        f"Movies failed: {movie_failed}"
    )

    print(
        f"Series imported: {series_success}"
    )

    print(
        f"Series failed: {series_failed}"
    )


if __name__ == "__main__":

    API_KEY = settings.TMDB_API_KEY

    asyncio.run(
        bulk_import(
            api_key=API_KEY,
            movie_pages=10,
            series_pages=10
        )
    )