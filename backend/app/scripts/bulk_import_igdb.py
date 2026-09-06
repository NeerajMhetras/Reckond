import argparse
import asyncio
import time
from collections import Counter

import httpx

from app.core.config import settings
from app.database.database import SessionLocal
from app.services.bulk_media_service import BulkMediaService
from app.services.providers.igdb import IGDBProvider


DEFAULT_LIMIT = 200
DEFAULT_CONCURRENCY = 5
DEFAULT_BATCH_SIZE = 25


async def persist_batch(media_items: list[dict]) -> list[dict]:
    db = SessionLocal()
    try:
        return await asyncio.to_thread(
            BulkMediaService().bulk_import_games,
            db,
            media_items,
        )
    finally:
        db.close()


async def import_games(
    limit: int = DEFAULT_LIMIT,
    concurrency: int = DEFAULT_CONCURRENCY,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> list[dict]:
    started_at = time.perf_counter()
    provider = IGDBProvider(
        client_id=settings.IGDB_CLIENT_ID,
        client_secret=settings.IGDB_CLIENT_SECRET_KEY,
    )
    semaphore = asyncio.Semaphore(concurrency)

    async with httpx.AsyncClient(timeout=30.0) as client:
        print("Fetching games from IGDB...")
        fetched_items = await provider.get_popular_games(client=client, limit=limit)
        unique_items = list({item["external_id"]: item for item in fetched_items}.values())
        print(f"Found {len(unique_items)} unique games")

        results = []
        for start in range(0, len(unique_items), batch_size):
            batch = unique_items[start : start + batch_size]
            async with semaphore:
                batch_results = await persist_batch(batch)
            results.extend(batch_results)
            for result in batch_results:
                position = len(results)
                print(
                    f"[{position}/{len(unique_items)}] "
                    f"{result['status']}: {result.get('title') or result['external_id']}"
                )
                if result["status"] == "failed":
                    print(f"  {result.get('error')}")

    elapsed = time.perf_counter() - started_at
    counts = Counter(result["status"] for result in results)
    print("\nIGDB import complete")
    print(f"Requested: {limit}")
    print(f"Fetched: {len(unique_items)}")
    print(f"Imported: {counts['imported']}")
    print(f"Skipped: {counts['skipped']}")
    print(f"Failed: {counts['failed']}")
    print(f"Elapsed time: {elapsed:.1f} seconds")
    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bulk import popular IGDB games")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY)
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(
        import_games(
            limit=args.limit,
            concurrency=args.concurrency,
            batch_size=args.batch_size,
        )
    )
