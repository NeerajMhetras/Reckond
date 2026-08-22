from app.models.media.entertainment import MediaType
from app.services.providers.tmdb import TMDBProvider
from app.services.providers.google_books import GoogleBooksProvider
from app.services.providers.igdb import IGDBProvider
class SearchService:
    def __init__(self, tmdb_provider: TMDBProvider, google_books_provider: GoogleBooksProvider, igdb_provider: IGDBProvider):
        self.tmdb_provider = tmdb_provider
        self.google_books_provider = google_books_provider
        self.igdb_provider = igdb_provider

    async def search(
        self,
        query: str,
        media_type: MediaType
    ):
        if media_type == MediaType.MOVIE:
            return await self.tmdb_provider.search_movie(query)

        if media_type == MediaType.SERIES:
            return await self.tmdb_provider.search_series(query)

        if media_type == MediaType.BOOK:
            return await self.google_books_provider.search_book(query)

        if media_type == MediaType.GAME:
            return await self.igdb_provider.search_game(query)

        raise ValueError(
            f"Search provider not implemented for {media_type}"
        )