import argparse
import asyncio
import time
from collections import Counter

import httpx

from app.core.config import settings
from app.database.database import SessionLocal
from app.services.bulk_media_service import BulkMediaService
from app.services.providers.google_books import GoogleBooksProvider


DEFAULT_LIMIT = 200
DEFAULT_CONCURRENCY = 5
DEFAULT_BATCH_SIZE = 25
SEARCH_QUERIES = (
    "subject:fiction",
    "subject:fantasy",
    "subject:science fiction",
    "subject:mystery",
    "subject:classics",
    "subject:romance",
    "subject:biography",
    "subject:psychology",
    "subject:technology",
    "subject:business",
)


async def search_query(
    provider: GoogleBooksProvider,
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    query: str,
) -> list[dict]:
    async with semaphore:
        return await provider.search_book(
            query=query,
            client=client,
            max_results=40,
        )


async def fetch_details(
    provider: GoogleBooksProvider,
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    item: dict,
) -> dict:
    async with semaphore:
        try:
            return await provider.get_book_details(
                book_id=str(item["external_id"]),
                client=client,
            )
        except Exception as error:
            return {
                "external_id": str(item["external_id"]),
                "title": item.get("title"),
                "fetch_error": str(error),
            }


async def persist_batch(media_items: list[dict]) -> list[dict]:
    db = SessionLocal()
    try:
        return await asyncio.to_thread(
            BulkMediaService().bulk_import_books,
            db,
            media_items,
        )
    finally:
        db.close()


async def import_books(
    limit: int = DEFAULT_LIMIT,
    concurrency: int = DEFAULT_CONCURRENCY,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> list[dict]:
    started_at = time.perf_counter()
    provider = GoogleBooksProvider(settings.GOOGLE_BOOKS_API_KEY)
    semaphore = asyncio.Semaphore(concurrency)

    async with httpx.AsyncClient(timeout=30.0) as client:
        print("Fetching book search results from Google Books...")
        search_results = await asyncio.gather(
            *(
                search_query(provider, client, semaphore, query)
                for query in SEARCH_QUERIES
            ),
            return_exceptions=True,
        )
        candidates = []
        for result in search_results:
            if isinstance(result, Exception):
                print(f"Search failed: {result}")
                continue
            candidates.extend(result)

        unique_candidates = list(
            {
                item["external_id"]: item
                for item in candidates
                if item.get("external_id")
            }.values()
        )[:limit]
        print(f"Found {len(unique_candidates)} unique book candidates")

        detail_results = await asyncio.gather(
            *(
                fetch_details(provider, client, semaphore, item)
                for item in unique_candidates
            )
        )
        valid_items = [
            item for item in detail_results if "fetch_error" not in item
        ]
        results = [
            {
                "external_id": item["external_id"],
                "title": item.get("title"),
                "status": "failed",
                "error": item["fetch_error"],
            }
            for item in detail_results
            if "fetch_error" in item
        ]
        print(f"Fetched {len(valid_items)} book details")

        for start in range(0, len(valid_items), batch_size):
            batch_results = await persist_batch(
                valid_items[start : start + batch_size]
            )
            results.extend(batch_results)
            for result in batch_results:
                position = len(results)
                print(
                    f"[{position}/{len(detail_results)}] "
                    f"{result['status']}: {result.get('title') or result['external_id']}"
                )
                if result["status"] == "failed":
                    print(f"  {result.get('error')}")

    elapsed = time.perf_counter() - started_at
    counts = Counter(result["status"] for result in results)
    print("\nGoogle Books import complete")
    print(f"Requested: {limit}")
    print(f"Fetched: {len(valid_items)}")
    print(f"Imported: {counts['imported']}")
    print(f"Skipped: {counts['skipped']}")
    print(f"Failed: {counts['failed']}")
    print(f"Elapsed time: {elapsed:.1f} seconds")
    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bulk import books from Google Books")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY)
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(
        import_books(
            limit=args.limit,
            concurrency=args.concurrency,
            batch_size=args.batch_size,
        )
    )
