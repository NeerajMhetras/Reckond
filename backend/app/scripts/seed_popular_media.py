import asyncio

from app.core.config import settings
from app.database.database import SessionLocal
from app.models.media.entertainment import MediaType
from app.services.media_service import MediaService
from app.services.providers.google_books import GoogleBooksProvider
from app.services.providers.igdb import IGDBProvider
from app.services.providers.tmdb import TMDBProvider


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
]

POPULAR_BOOKS = [
    "The Lord of the Rings",
    "Harry Potter and the Philosopher's Stone",
    "1984 George Orwell",
    "The Hobbit",
    "Dune Frank Herbert",
    "The Alchemist Paulo Coelho",
    "Pride and Prejudice Jane Austen",
    "The Great Gatsby F. Scott Fitzgerald",
    "Atomic Habits James Clear",
    "The Name of the Wind Patrick Rothfuss",
]


async def seed_media(searches: list[str], media_type: MediaType, service: MediaService):
    provider = service.igdb_provider if media_type == MediaType.GAME else service.google_books_provider
    imported = 0

    for search_term in searches:
        try:
            results = await (
                provider.search_game(search_term)
                if media_type == MediaType.GAME
                else provider.search_book(search_term)
            )
            if not results:
                print(f"Skipped: {search_term} (no result)")
                continue

            result = results[0]
            external_id = result.external_id if media_type == MediaType.GAME else result["external_id"]

            with SessionLocal() as db:
                media = await service.import_media(db, str(external_id), media_type)
                print(f"Imported: {media.title}")
                imported += 1
        except Exception as error:
            print(f"Failed: {search_term} -> {error}")

    return imported


async def main():
    service = MediaService(
        tmdb_provider=TMDBProvider(settings.TMDB_API_KEY),
        google_books_provider=GoogleBooksProvider(settings.GOOGLE_BOOKS_API_KEY),
        igdb_provider=IGDBProvider(settings.IGDB_CLIENT_ID, settings.IGDB_CLIENT_SECRET_KEY),
    )

    print("Seeding popular games...")
    game_count = await seed_media(POPULAR_GAMES, MediaType.GAME, service)
    print("Seeding popular books...")
    book_count = await seed_media(POPULAR_BOOKS, MediaType.BOOK, service)
    print(f"Finished: {game_count} games and {book_count} books processed.")


if __name__ == "__main__":
    asyncio.run(main())