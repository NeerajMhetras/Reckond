import argparse
import asyncio
import time
from collections import Counter

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.database.database import SessionLocal
from app.models.media.entertainment import MediaType
from app.services.bulk_media_service import BulkMediaService
from app.services.providers.tmdb import TMDBProvider


TMDB_BASE_URL = "https://api.themoviedb.org/3"
DEFAULT_CONCURRENCY = 5
DEFAULT_BATCH_SIZE = 10

tmdb_retry = retry(
    stop=stop_after_attempt(10),
    wait=wait_exponential(multiplier=1, min=2, max=6),
    retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException)),
    reraise=True,
)


@tmdb_retry
async def get_tmdb_ids(
    client: httpx.AsyncClient,
    api_key: str,
    media_type: str,
    endpoint: str,
    pages: int,
) -> list[str]:
    ids = []
    for page in range(1, pages + 1):
        response = await client.get(
            f"{TMDB_BASE_URL}/{media_type}/{endpoint}",
            params={"api_key": api_key, "page": page},
        )
        response.raise_for_status()
        ids.extend(str(item["id"]) for item in response.json().get("results", []))
        print(f"Collected {media_type} page {page}/{pages}")
    return list(dict.fromkeys(ids))


async def fetch_details(
    external_id: str,
    media_type: MediaType,
    provider: TMDBProvider,
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
) -> dict:
    async with semaphore:
        if media_type == MediaType.MOVIE:
            return await provider.get_movie_details(external_id, client=client)
        return await provider.get_series_details(external_id, client=client)


async def fetch_batch(
    external_ids: list[str],
    media_type: MediaType,
    provider: TMDBProvider,
    client: httpx.AsyncClient,
    concurrency: int,
) -> list[dict]:
    semaphore = asyncio.Semaphore(concurrency)
    tasks = [
        asyncio.create_task(
            fetch_details(
                external_id=external_id,
                media_type=media_type,
                provider=provider,
                client=client,
                semaphore=semaphore,
            )
        )
        for external_id in external_ids
    ]
    fetched = []
    for external_id, task in zip(external_ids, tasks):
        try:
            fetched.append(await task)
        except Exception as error:
            fetched.append(
                {
                    "external_id": external_id,
                    "title": None,
                    "fetch_error": str(error),
                }
            )
    return fetched


def persist_batch(media_items: list[dict], media_type: MediaType) -> list[dict]:
    valid_items = [item for item in media_items if "fetch_error" not in item]
    results = [
        {
            "success": False,
            "skipped": False,
            "external_id": str(item["external_id"]),
            "title": item.get("title"),
            "error": item["fetch_error"],
        }
        for item in media_items
        if "fetch_error" in item
    ]
    if not valid_items:
        return results

    db = SessionLocal()
    try:
        results.extend(
            BulkMediaService().bulk_import_media(
                db=db,
                media_items=valid_items,
                media_type=media_type,
            )
        )
    finally:
        db.close()
    return results


async def import_batch(
    external_ids: list[str],
    media_type: MediaType,
    provider: TMDBProvider,
    client: httpx.AsyncClient,
    concurrency: int,
    batch_size: int,
) -> list[dict]:
    started_at = time.perf_counter()
    results = []
    total = len(external_ids)

    for start in range(0, total, batch_size):
        batch_ids = external_ids[start : start + batch_size]
        media_items = await fetch_batch(
            external_ids=batch_ids,
            media_type=media_type,
            provider=provider,
            client=client,
            concurrency=concurrency,
        )
        batch_results = await asyncio.to_thread(persist_batch, media_items, media_type)
        results.extend(batch_results)

        for result in batch_results:
            completed = len(results)
            elapsed = time.perf_counter() - started_at
            status = "skipped" if result.get("skipped") else "imported" if result["success"] else "failed"
            title = result.get("title") or "(title unavailable)"
            print(
                f"[{completed}/{total}] {status}: {title} "
                f"({elapsed / completed:.2f}s avg)"
            )
            if not result["success"] and not result.get("skipped"):
                print(f"  {result['external_id']}: {result.get('error')}")

    elapsed = time.perf_counter() - started_at
    print(f"Total time: {elapsed:.1f} seconds")
    print(f"Average: {elapsed / total:.2f} seconds/item" if total else "Average: n/a")
    return results


def print_summary(media_type: MediaType, results: list[dict]) -> None:
    counts = Counter(
        "skipped" if result.get("skipped") else "successful" if result["success"] else "failed"
        for result in results
    )
    print(f"\n{media_type.value.title()}:")
    print(f"    successful: {counts['successful']}")
    print(f"    skipped: {counts['skipped']}")
    print(f"    failed: {counts['failed']}")


async def bulk_import(
    api_key: str,
    movie_pages: int = 10,
    series_pages: int = 10,
    limit: int | None = None,
    concurrency: int = DEFAULT_CONCURRENCY,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> None:
    tmdb_provider = TMDBProvider(api_key)

    async with httpx.AsyncClient(timeout=100.0) as client:
        movie_ids = await get_tmdb_ids(
            client, api_key, "movie", "top_rated", movie_pages
        )
        series_ids = await get_tmdb_ids(
            client, api_key, "tv", "top_rated", series_pages
        )
        if limit is not None:
            movie_ids = movie_ids[:limit]
            series_ids = series_ids[:limit]

        print(f"\nImporting {len(movie_ids)} movies")
        movie_results = await import_batch(
            movie_ids,
            MediaType.MOVIE,
            tmdb_provider,
            client,
            concurrency,
            batch_size,
        )
        print_summary(MediaType.MOVIE, movie_results)

        print(f"\nImporting {len(series_ids)} series")
        series_results = await import_batch(
            series_ids,
            MediaType.SERIES,
            tmdb_provider,
            client,
            concurrency,
            batch_size,
        )
        print_summary(MediaType.SERIES, series_results)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed TMDB movies and series")
    parser.add_argument("--movie-pages", type=int, default=10)
    parser.add_argument("--series-pages", type=int, default=10)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY)
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(
        bulk_import(
            api_key=settings.TMDB_API_KEY,
            movie_pages=args.movie_pages,
            series_pages=args.series_pages,
            limit=args.limit,
            concurrency=args.concurrency,
            batch_size=args.batch_size,
        )
    )
