from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.media.entertainment import Entertainment, MediaType
from app.models.media.movie.movie import MovieDetails
from app.models.media.series.series import SeriesDetails
from app.models.media.book.book import BookDetails,Author
from app.models.media.game.game import Platform,GameDetails
from app.models.media.common.genre import Genre
from app.models.media.common.keyword import Keyword
from app.models.media.common.person import Person
from app.models.media.movie.cast import MovieCast
from app.models.media.movie.crew import MovieCrew
from app.models.media.series.series import SeriesDetails
from app.models.media.series.cast import SeriesCast
from app.models.media.series.crew import SeriesCrew

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
            db.flush()

            for genre_data in media_data.get("genres", []):
                genre = (
                    db.query(Genre)
                    .filter(
                        Genre.external_id == genre_data["external_id"]
                    )
                    .first()
                )

                if not genre:
                    genre = Genre(
                        external_id=genre_data["external_id"],
                        name=genre_data["name"]
                    )

                    db.add(genre)
                    db.flush()

                movie_details.genres.append(genre)

            for keyword_data in media_data.get("keywords", []):

                keyword = (
                    db.query(Keyword)
                    .filter(
                        Keyword.external_id == keyword_data["external_id"]
                    )
                    .first()
                )

                if not keyword:
                    keyword = Keyword(
                        external_id=keyword_data["external_id"],
                        name=keyword_data["name"]
                    )

                    db.add(keyword)
                    db.flush()

                movie_details.keywords.append(keyword)      

            for cast_data in media_data.get("cast", [])[:20]:
                person = (
                    db.query(Person)
                    .filter(
                        Person.external_id == cast_data["external_id"]
                    )
                    .first()
                )

                if not person:
                    person = Person(
                        external_id=cast_data["external_id"],
                        name=cast_data["name"]
                    )

                    db.add(person)
                    db.flush()

                movie_cast = MovieCast(
                    movie_id=movie_details.id,
                    person_id=person.id,
                    character=cast_data.get("character"),
                    cast_order=cast_data.get("cast_order")
                )

                db.add(movie_cast)

            important_jobs = {
                "Director",
                "Writer",
                "Screenplay",
                "Story",
                "Original Music Composer",
                "Director of Photography"
            }

            for crew_data in media_data.get("crew", []):
                if crew_data.get("job") not in important_jobs:
                    continue

                person = (
                    db.query(Person)
                    .filter(
                        Person.external_id == crew_data["external_id"]
                    )
                    .first()
                )

                if not person:
                    person = Person(
                        external_id=crew_data["external_id"],
                        name=crew_data["name"]
                    )

                    db.add(person)
                    db.flush()

                movie_crew = MovieCrew(
                    movie_id=movie_details.id,
                    person_id=person.id,
                    department=crew_data.get("department"),
                    job=crew_data.get("job")
                )

                db.add(movie_crew)

            
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
            db.flush()

            for genre_data in media_data.get("genres", []):

                genre = (
                    db.query(Genre)
                    .filter(
                        Genre.external_id == genre_data["external_id"]
                    )
                    .first()
                )

                if not genre:

                    genre = Genre(
                        external_id=genre_data["external_id"],
                        name=genre_data["name"]
                    )

                    db.add(genre)
                    db.flush()

                series_details.genres.append(genre)

            for keyword_data in media_data.get("keywords", []):
                    keyword = (
                        db.query(Keyword)
                        .filter(
                            Keyword.external_id ==
                            keyword_data["external_id"]
                        )
                        .first()
                    )

                    if not keyword:

                        keyword = Keyword(
                            external_id=keyword_data["external_id"],
                            name=keyword_data["name"]
                        )

                        db.add(keyword)
                        db.flush()

                    series_details.keywords.append(keyword)

            for cast_data in media_data.get("cast", []):

                person = (
                    db.query(Person)
                    .filter(
                        Person.external_id ==
                        cast_data["external_id"]
                    )
                    .first()
                )

                if not person:

                    person = Person(
                        external_id=cast_data["external_id"],
                        name=cast_data["name"]
                    )

                    db.add(person)
                    db.flush()

                cast_member = SeriesCast(
                    series_id=series_details.id,
                    person_id=person.id,
                    character=cast_data.get("character"),
                    cast_order=cast_data.get("cast_order")
                )

                db.add(cast_member)

            for crew_data in media_data.get("crew", []):

                person = (
                    db.query(Person)
                    .filter(
                        Person.external_id ==
                        crew_data["external_id"]
                    )
                    .first()
                )

                if not person:

                    person = Person(
                        external_id=crew_data["external_id"],
                        name=crew_data["name"]
                    )

                    db.add(person)
                    db.flush()

                crew_member = SeriesCrew(
                    series_id=series_details.id,
                    person_id=person.id,
                    department=crew_data.get("department"),
                    job=crew_data.get("job")
                )

                db.add(crew_member)

            
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

        try:
            db.commit()
            db.refresh(entertainment)

        except IntegrityError:
            db.rollback()

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
