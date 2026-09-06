import asyncio

import httpx

from app.core.config import settings
from app.database.database import SessionLocal
from app.models.media.entertainment import MediaType
from app.services.media_service import MediaService
from app.services.providers.google_books import GoogleBooksProvider
from app.services.providers.igdb import IGDBProvider
from app.services.providers.tmdb import TMDBProvider


CONCURRENCY = 5

POPULAR_GAMES = [
    "Grand Theft Auto V",
    "Red Dead Redemption 2",
    "The Witcher 3: Wild Hunt",
    "Elden Ring",
    "Minecraft",
    "The Legend of Zelda: Breath of the Wild",
    "God of War",
    "The Last of Us Part II",
    "Baldur's Gate 3",
    "Hades",
    "Cyberpunk 2077",
    "Dark Souls",
    "Dark Souls III",
    "Bloodborne",
    "Sekiro: Shadows Die Twice",
    "Hollow Knight",
    "Celeste",
    "Stardew Valley",
    "Terraria",
    "Portal 2",
    "Half-Life 2",
    "The Elder Scrolls V: Skyrim",
    "Fallout: New Vegas",
    "Mass Effect 2",
    "Mass Effect 3",
    "Red Dead Redemption",
    "Grand Theft Auto: San Andreas",
    "Grand Theft Auto IV",
    "God of War Ragnarök",
    "The Last of Us",
    "Uncharted 4: A Thief's End",
    "Marvel's Spider-Man",
    "Ghost of Tsushima",
    "Horizon Zero Dawn",
    "Horizon Forbidden West",
    "Death Stranding",
    "Resident Evil 4",
    "Resident Evil 2",
    "Doom",
    "Doom Eternal",
    "Metal Gear Solid V: The Phantom Pain",
    "Persona 5",
    "Final Fantasy VII",
    "Final Fantasy X",
    "Final Fantasy XVI",
    "Baldur's Gate 3",
    "Divinity: Original Sin 2",
    "Disco Elysium",
    "The Outer Worlds",
    "Control",
    "Alan Wake 2",
]


async def search_game(
    provider: IGDBProvider,
    search_term: str,
):
    try:
        results = await provider.search_game(search_term)

        if not results:
            print(f"No result: {search_term}")
            return None

        return results[0].external_id

    except Exception as error:
        print(f"Search failed: {search_term} -> {error}")
        return None


async def collect_game_ids():
    provider = IGDBProvider(
        client_id=settings.IGDB_CLIENT_ID,
        client_secret=settings.IGDB_CLIENT_SECRET_KEY,
    )

    ids = []

    for search_term in POPULAR_GAMES:
        game_id = await search_game(provider, search_term)

        if game_id:
            ids.append(game_id)
            print(f"Found: {search_term} -> {game_id}")

    return list(dict.fromkeys(ids))


async def import_one(
    external_id: str,
    semaphore: asyncio.Semaphore,
):
    async with semaphore:
        db = SessionLocal()

        try:
            service = MediaService(
                tmdb_provider=TMDBProvider(settings.TMDB_API_KEY),
                google_books_provider=GoogleBooksProvider(
                    settings.GOOGLE_BOOKS_API_KEY
                ),
                igdb_provider=IGDBProvider(
                    client_id=settings.IGDB_CLIENT_ID,
                    client_secret=settings.IGDB_CLIENT_SECRET_KEY,
                ),
            )

            result = await service.import_media(
                db=db,
                external_id=external_id,
                media_type=MediaType.GAME,
            )

            return {
                "success": True,
                "title": result.title,
                "external_id": external_id,
            }

        except Exception as error:
            return {
                "success": False,
                "external_id": external_id,
                "error": str(error),
            }

        finally:
            db.close()


async def import_batch(external_ids: list[str]):
    semaphore = asyncio.Semaphore(CONCURRENCY)

    tasks = [
        import_one(
            external_id=external_id,
            semaphore=semaphore,
        )
        for external_id in external_ids
    ]

    results = []
    completed = 0
    total = len(tasks)

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
                f"-> {result['error']}"
            )

        results.append(result)

    return results


async def main():
    print("========================")
    print("COLLECTING IGDB GAMES")
    print("========================")

    game_ids = await collect_game_ids()

    print(f"\nCollected {len(game_ids)} unique games")

    print("\n========================")
    print("IMPORTING GAMES")
    print("========================")

    results = await import_batch(game_ids)

    successful = sum(
        result["success"]
        for result in results
    )

    failed = len(results) - successful

    print("\n========================")
    print("IMPORT COMPLETE")
    print("========================")

    print(f"Games imported: {successful}")
    print(f"Games failed: {failed}")


if __name__ == "__main__":
    asyncio.run(main())