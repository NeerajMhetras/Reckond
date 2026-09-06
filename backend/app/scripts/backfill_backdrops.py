import asyncio

from app.core.config import settings
from app.database.database import SessionLocal
from app.models.media.entertainment import Entertainment, MediaType
from app.services.providers.tmdb import TMDBProvider


CONCURRENCY = 5


async def update_backdrop(media: Entertainment, provider: TMDBProvider, semaphore: asyncio.Semaphore):
    async with semaphore:
        backdrop_url = media.poster_url
        try:
            if media.media_type == MediaType.MOVIE:
                details = await provider.get_movie_details(media.external_id)
                backdrop_url = details.get("backdrop_url") or backdrop_url
            elif media.media_type == MediaType.SERIES:
                details = await provider.get_series_details(media.external_id)
                backdrop_url = details.get("backdrop_url") or backdrop_url

            if backdrop_url:
                with SessionLocal() as db:
                    record = db.get(Entertainment, media.id)
                    record.backdrop_url = backdrop_url
                    db.commit()
                return media.title, True
        except Exception as error:
            return media.title, error

        return media.title, False


async def main():
    with SessionLocal() as db:
        media = db.query(Entertainment).filter(Entertainment.backdrop_url.is_(None)).all()

    provider = TMDBProvider(settings.TMDB_API_KEY)
    semaphore = asyncio.Semaphore(CONCURRENCY)
    results = await asyncio.gather(*[
        update_backdrop(item, provider, semaphore)
        for item in media
    ])

    updated = sum(result[1] is True for result in results)
    failed = sum(result[1] not in (True, False) for result in results)
    print(f"Backdrops updated: {updated}; failed: {failed}; checked: {len(results)}")
    for title, result in results:
        if result not in (True, False):
            print(f"Failed: {title} -> {result}")


if __name__ == "__main__":
    asyncio.run(main())