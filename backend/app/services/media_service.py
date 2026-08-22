from sqlalchemy.orm import Session

from app.models.media.entertainment import Entertainment, MediaType
from app.models.media.movie import MovieDetails
from app.models.media.series import SeriesDetails
from app.models.media.book import BookDetails,Author
from app.models.media.game import Platform,GameDetails


from app.services.providers.tmdb import TMDBProvider
from app.services.providers.google_books import GoogleBooksProvider
from app.services.providers.igdb import IGDBProvider

from app.utils.media_serializer import build_media_response

class MediaService:

    def __init__(self, tmdb_provider: TMDBProvider, google_books_provider: GoogleBooksProvider, igdb_provider: IGDBProvider):
        self.tmdb_provider = tmdb_provider
        self.google_books_provider = google_books_provider
        self.igdb_provider = igdb_provider

    async def import_media(
        self,
        db: Session,
        external_id: str,
        media_type: MediaType
    ):

        if media_type not in (
            MediaType.MOVIE,
            MediaType.SERIES,
            MediaType.BOOK,
            MediaType.GAME
        ):
            raise ValueError(
                f"Import for {media_type} is not supported yet"
            )
        external_source = None
        if media_type in [MediaType.MOVIE,MediaType.SERIES]:
            external_source = "TMDB"
        elif media_type == MediaType.BOOK:
            external_source = "GoogleBooks"
        else:
            external_source = "IGDB"

        existing = (
            db.query(Entertainment)
            .filter(
                Entertainment.external_source == external_source,
                Entertainment.external_id == external_id,
                Entertainment.media_type == media_type
            )
            .first()
        )

        if existing:
            return existing

        # -------------------------
        # MOVIE
        # -------------------------

        if media_type == MediaType.MOVIE:

            media_data = await self.tmdb_provider.get_movie_details(
                external_id
            )

            entertainment = Entertainment(
                title=media_data["title"],
                description=media_data.get("description"),
                poster_url=media_data.get("poster_url"),
                release_date=media_data.get("release_date"),
                media_type=MediaType.MOVIE,
                language=media_data.get("language"),
                external_id=media_data["external_id"],
                external_source=media_data["external_source"],
            )

            db.add(entertainment)
            db.flush()

            movie_details = MovieDetails(
                entertainment_id=entertainment.id,
                runtime=media_data.get("runtime"),
                budget=media_data.get("budget"),
                revenue=media_data.get("revenue"),
            )

            db.add(movie_details)

        # -------------------------
        # SERIES
        # -------------------------

        elif media_type == MediaType.SERIES:

            media_data = await self.tmdb_provider.get_series_details(
                external_id
            )

            entertainment = Entertainment(
                title=media_data["title"],
                description=media_data.get("description"),
                poster_url=media_data.get("poster_url"),
                release_date=media_data.get("release_date"),
                media_type=MediaType.SERIES,
                language=media_data.get("language"),
                external_id=media_data["external_id"],
                external_source=media_data["external_source"],
            )

            db.add(entertainment)
            db.flush()

            series_details = SeriesDetails(
                entertainment_id=entertainment.id,
                series_type=media_data["series_type"],
                animation_type=media_data.get("animation_type"),
                number_of_seasons=media_data.get("number_of_seasons"),
                number_of_episodes=media_data.get("number_of_episodes"),
            )

            db.add(series_details)

        # -------------------------
                # BOOKS
        # -------------------------

        elif media_type == MediaType.BOOK:
            media_data = await self.google_books_provider.get_book_details(external_id)

            entertainment = Entertainment(
                title = media_data["title"],
                description=media_data.get("description"),
                poster_url=media_data.get("poster_url"),
                release_date=media_data.get("release_date"),
                media_type=MediaType.BOOK,
                language=media_data.get("language"),
                external_id=media_data["external_id"],
                external_source=media_data["external_source"],
            )
            db.add(entertainment)
            db.flush()

            book = BookDetails(
                entertainment_id=entertainment.id,
                isbn=media_data.get("isbn"),
                pages=media_data.get("pages"),
                publisher=media_data.get("publisher")
            )

            db.add(book)
            db.flush()

            for author_name in media_data.get("authors", []):
                author = (
                    db.query(Author)
                    .filter(Author.name == author_name)
                    .first()
                )

                if not author:
                    author = Author(
                        name=author_name
                    )

                    db.add(author)
                    db.flush()
                book.authors.append(author)

        # -------------------------
                # GAMES
        # -------------------------

        elif media_type == MediaType.GAME:
            media_data = await self.igdb_provider.get_game_details(external_id)
            entertainment = Entertainment(
                title = media_data["title"],
                description=media_data.get("description"),
                poster_url=media_data.get("poster_url"),
                release_date=media_data.get("release_date"),
                media_type=MediaType.GAME,
                language=media_data.get("language"),
                external_id=media_data["external_id"],
                external_source=media_data["external_source"],
            )
            db.add(entertainment)
            db.flush()

            game = GameDetails(
                entertainment_id = entertainment.id
            )
            db.add(game)
            db.flush()

            for platform_name in media_data.get("platforms",[]):
                platform = (db.query(Platform).filter(
                    Platform.name == platform_name
                ).first()
                )
                if not platform:
                    platform = Platform(
                        name = platform_name
                    )
                    db.add(platform)
                    db.flush()
                game.platforms.append(platform)
        db.commit()
        db.refresh(entertainment)

        return entertainment

    
    def get_media_by_id(
            self,
            db: Session,
            media_id: int,
    ):
        media = (db.query(Entertainment).filter(Entertainment.id == media_id).first())

        if not media:
            return None
        

        return build_media_response(media)

    def get_all_media(
        self,
        db: Session,
        media_type: MediaType | None = None,
        skip: int = 0,
        limit: int = 20
    ):
        query = db.query(Entertainment)

        if media_type:
            query = query.filter(
                Entertainment.media_type == media_type
            )

        total = query.count()
        
        media_list = (query.offset(skip).limit(limit).all())


        items = [build_media_response(media) for media in media_list]

        return {
            "items" : items,
            "total" : total,
            "skip" : skip,
            "limit": limit
        }
