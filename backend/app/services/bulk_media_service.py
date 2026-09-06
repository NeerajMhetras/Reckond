from collections.abc import Iterable

from sqlalchemy import or_, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.models.media.common.genre import Genre
from app.models.media.common.keyword import Keyword
from app.models.media.common.person import Person
from app.models.media.entertainment import Entertainment, MediaType
from app.models.media.game.game import GameDetails, Platform, game_platforms
from app.models.media.book.book import Author, BookDetails, book_authors
from app.models.media.movie.associations import movie_genres, movie_keywords
from app.models.media.movie.cast import MovieCast
from app.models.media.movie.crew import MovieCrew
from app.models.media.movie.movie import MovieDetails
from app.models.media.series.associations import series_genres, series_keywords
from app.models.media.series.cast import SeriesCast
from app.models.media.series.crew import SeriesCrew
from app.models.media.series.series import SeriesDetails


class BulkMediaService:
    """Persist already-fetched provider payloads in database-sized batches.

    The normal MediaService path intentionally remains item-oriented for API
    imports. API fetching stays outside the database transaction, and each
    catalog type uses its own persistence mapping.
    """

    def get_existing_external_ids(
        self,
        db: Session,
        external_ids: Iterable[str],
        media_type: MediaType,
    ) -> set[str]:
        ids = {str(external_id) for external_id in external_ids}
        if not ids:
            return set()

        source = "TMDB"
        rows = db.execute(
            select(Entertainment.external_id).where(
                Entertainment.external_source == source,
                Entertainment.media_type == media_type,
                Entertainment.external_id.in_(ids),
            )
        ).scalars()
        return {str(external_id) for external_id in rows}

    def bulk_import_media(
        self,
        db: Session,
        media_items: list[dict],
        media_type: MediaType,
    ) -> list[dict]:
        if media_type not in (MediaType.MOVIE, MediaType.SERIES):
            raise ValueError("Bulk TMDB import supports movies and series only")

        items_by_external_id = {
            str(item["external_id"]): item
            for item in media_items
        }
        external_ids = set(items_by_external_id)
        existing_ids = self.get_existing_external_ids(
            db=db,
            external_ids=external_ids,
            media_type=media_type,
        )

        results = [
            {
                "success": False,
                "skipped": True,
                "external_id": external_id,
                "title": items_by_external_id[external_id].get("title"),
            }
            for external_id in sorted(existing_ids)
        ]
        pending_items = [
            item
            for external_id, item in items_by_external_id.items()
            if external_id not in existing_ids
        ]

        if not pending_items:
            return results

        try:
            self._persist_batch(
                db=db,
                media_items=pending_items,
                media_type=media_type,
            )
            results.extend(
                {
                    "success": True,
                    "skipped": False,
                    "external_id": str(item["external_id"]),
                    "title": item.get("title"),
                }
                for item in pending_items
            )
        except Exception as error:
            db.rollback()
            results.extend(
                {
                    "success": False,
                    "skipped": False,
                    "external_id": str(item["external_id"]),
                    "title": item.get("title"),
                    "error": str(error),
                }
                for item in pending_items
            )

        return results

    def bulk_import_games(
        self,
        db: Session,
        media_items: list[dict],
    ) -> list[dict]:
        return self._bulk_import_simple_media(
            db=db,
            media_items=media_items,
            media_type=MediaType.GAME,
            source="IGDB",
            detail_model=GameDetails,
            detail_rows=lambda media, entertainment_id: {
                "entertainment_id": entertainment_id
            },
            lookup_model=Platform,
            lookup_values=lambda item: item.get("platforms", []),
            association_table=game_platforms,
            detail_id_key="game_id",
            lookup_id_key="platform_id",
        )

    def bulk_import_books(
        self,
        db: Session,
        media_items: list[dict],
    ) -> list[dict]:
        return self._bulk_import_simple_media(
            db=db,
            media_items=media_items,
            media_type=MediaType.BOOK,
            source="GOOGLE_BOOKS",
            detail_model=BookDetails,
            detail_rows=lambda media, entertainment_id: {
                "entertainment_id": entertainment_id,
                "isbn": media.get("isbn"),
                "pages": media.get("pages"),
                "publisher": media.get("publisher"),
            },
            lookup_model=Author,
            lookup_values=lambda item: item.get("authors", []),
            association_table=book_authors,
            detail_id_key="book_id",
            lookup_id_key="author_id",
        )

    def _bulk_import_simple_media(
        self,
        db: Session,
        media_items: list[dict],
        media_type: MediaType,
        source: str,
        detail_model,
        detail_rows,
        lookup_model,
        lookup_values,
        association_table,
        detail_id_key: str,
        lookup_id_key: str,
    ) -> list[dict]:
        items_by_external_id = {
            str(item["external_id"]): item
            for item in media_items
            if item.get("external_id") and item.get("title")
        }
        if not items_by_external_id:
            return []

        external_ids = list(items_by_external_id)
        existing_ids = {
            str(external_id)
            for external_id in db.execute(
                select(Entertainment.external_id).where(
                    Entertainment.external_source == source,
                    Entertainment.external_id.in_(external_ids),
                )
            ).scalars()
        }
        results = [
            {
                "external_id": external_id,
                "title": items_by_external_id[external_id].get("title"),
                "status": "skipped",
            }
            for external_id in existing_ids
        ]
        pending_items = [
            item
            for external_id, item in items_by_external_id.items()
            if external_id not in existing_ids
        ]
        if not pending_items:
            return results

        try:
            entertainment_rows = [
                {
                    "title": item["title"],
                    "description": item.get("description"),
                    "poster_url": item.get("poster_url"),
                    "backdrop_url": item.get("backdrop_url") or item.get("poster_url"),
                    "release_date": item.get("release_date"),
                    "media_type": media_type,
                    "language": item.get("language"),
                    "external_id": str(item["external_id"]),
                    "external_source": source,
                }
                for item in pending_items
            ]
            db.execute(
                pg_insert(Entertainment)
                .values(entertainment_rows)
                .on_conflict_do_nothing(
                    index_elements=["external_source", "external_id"]
                )
            )
            entertainment_by_external_id = {
                str(media.external_id): media
                for media in db.execute(
                    select(Entertainment).where(
                        Entertainment.external_source == source,
                        Entertainment.external_id.in_(external_ids),
                    )
                ).scalars()
            }
            detail_values = [
                detail_rows(
                    item,
                    entertainment_by_external_id[str(item["external_id"])].id,
                )
                for item in pending_items
            ]
            db.execute(
                pg_insert(detail_model)
                .values(detail_values)
                .on_conflict_do_nothing(index_elements=["entertainment_id"])
            )
            detail_by_entertainment_id = {
                detail.entertainment_id: detail
                for detail in db.execute(
                    select(detail_model).where(
                        detail_model.entertainment_id.in_(
                            [row["entertainment_id"] for row in detail_values]
                        )
                    )
                ).scalars()
            }

            lookup_names = {
                str(value)
                for item in pending_items
                for value in lookup_values(item)
                if value
            }
            existing_lookup = {
                row.name: row
                for row in db.execute(
                    select(lookup_model).where(lookup_model.name.in_(lookup_names))
                ).scalars()
            }
            missing_lookup = [
                {"name": name}
                for name in lookup_names
                if name not in existing_lookup
            ]
            if missing_lookup:
                db.execute(
                    pg_insert(lookup_model)
                    .values(missing_lookup)
                    .on_conflict_do_nothing()
                )
            lookup_by_name = {
                row.name: row.id
                for row in db.execute(
                    select(lookup_model).where(lookup_model.name.in_(lookup_names))
                ).scalars()
            }

            association_rows = []
            for item in pending_items:
                detail = detail_by_entertainment_id[
                    entertainment_by_external_id[str(item["external_id"])].id
                ]
                for value in lookup_values(item):
                    if value and str(value) in lookup_by_name:
                        association_rows.append(
                            {
                                detail_id_key: detail.id,
                                lookup_id_key: lookup_by_name[str(value)],
                            }
                        )
            if association_rows:
                db.execute(
                    pg_insert(association_table)
                    .values(association_rows)
                    .on_conflict_do_nothing()
                )
            db.commit()
            results.extend(
                {
                    "external_id": str(item["external_id"]),
                    "title": item.get("title"),
                    "status": "imported",
                }
                for item in pending_items
            )
        except Exception as error:
            db.rollback()
            results.extend(
                {
                    "external_id": str(item["external_id"]),
                    "title": item.get("title"),
                    "status": "failed",
                    "error": str(error),
                }
                for item in pending_items
            )
        return results

    def _persist_batch(
        self,
        db: Session,
        media_items: list[dict],
        media_type: MediaType,
    ) -> None:
        source = "TMDB"
        entertainment_rows = [
            {
                "title": item["title"],
                "description": item.get("description"),
                "poster_url": item.get("poster_url"),
                "backdrop_url": item.get("backdrop_url") or item.get("poster_url"),
                "release_date": item.get("release_date"),
                "media_type": media_type,
                "language": item.get("language"),
                "external_id": str(item["external_id"]),
                "external_source": source,
            }
            for item in media_items
        ]

        db.execute(
            pg_insert(Entertainment)
            .values(entertainment_rows)
            .on_conflict_do_nothing(
                index_elements=["external_source", "external_id"]
            )
        )

        external_ids = [row["external_id"] for row in entertainment_rows]
        entertainment_by_external_id = {
            str(media.external_id): media
            for media in db.execute(
                select(Entertainment).where(
                    Entertainment.external_source == source,
                    Entertainment.media_type == media_type,
                    Entertainment.external_id.in_(external_ids),
                )
            ).scalars()
        }

        if len(entertainment_by_external_id) != len(media_items):
            raise RuntimeError("Could not resolve all inserted entertainment rows")

        if media_type == MediaType.MOVIE:
            detail_model = MovieDetails
            detail_rows = [
                {
                    "entertainment_id": entertainment_by_external_id[
                        str(item["external_id"])
                    ].id,
                    "runtime": item.get("runtime"),
                    "budget": item.get("budget"),
                    "revenue": item.get("revenue"),
                }
                for item in media_items
            ]
        else:
            detail_model = SeriesDetails
            detail_rows = [
                {
                    "entertainment_id": entertainment_by_external_id[
                        str(item["external_id"])
                    ].id,
                    "series_type": item["series_type"],
                    "animation_type": item.get("animation_type"),
                    "number_of_seasons": item.get("number_of_seasons"),
                    "number_of_episodes": item.get("number_of_episodes"),
                }
                for item in media_items
            ]

        db.execute(
            pg_insert(detail_model)
            .values(detail_rows)
            .on_conflict_do_nothing(index_elements=["entertainment_id"])
        )

        detail_by_entertainment_id = {
            detail.entertainment_id: detail
            for detail in db.execute(
                select(detail_model).where(
                    detail_model.entertainment_id.in_(
                        [row["entertainment_id"] for row in detail_rows]
                    )
                )
            ).scalars()
        }

        genre_ids = self._ensure_lookup_rows(
            db=db,
            model=Genre,
            rows=(
                genre
                for item in media_items
                for genre in item.get("genres", [])
            ),
        )
        keyword_ids = self._ensure_lookup_rows(
            db=db,
            model=Keyword,
            rows=(
                keyword
                for item in media_items
                for keyword in item.get("keywords", [])
            ),
        )
        people_ids = self._ensure_people(
            db=db,
            rows=(
                person
                for item in media_items
                for person in (*item.get("cast", []), *item.get("crew", []))
            ),
        )

        genre_associations = []
        keyword_associations = []
        cast_rows = []
        crew_rows = []

        for item in media_items:
            detail = detail_by_entertainment_id[
                entertainment_by_external_id[str(item["external_id"])].id
            ]

            for genre in item.get("genres", []):
                genre_id = genre_ids[int(genre["external_id"])]
                association = {
                    "genre_id": genre_id,
                }
                association["movie_id" if media_type == MediaType.MOVIE else "series_id"] = detail.id
                genre_associations.append(association)

            for keyword in item.get("keywords", []):
                keyword_id = keyword_ids[int(keyword["external_id"])]
                association = {
                    "keyword_id": keyword_id,
                }
                association["movie_id" if media_type == MediaType.MOVIE else "series_id"] = detail.id
                keyword_associations.append(association)

            for cast in item.get("cast", []):
                cast_row = {
                    "person_id": people_ids[int(cast["external_id"])],
                    "character": cast.get("character"),
                    "cast_order": cast.get("cast_order"),
                }
                cast_row["movie_id" if media_type == MediaType.MOVIE else "series_id"] = detail.id
                cast_rows.append(cast_row)

            for crew in item.get("crew", []):
                crew_row = {
                    "person_id": people_ids[int(crew["external_id"])],
                    "department": crew.get("department"),
                    "job": crew.get("job"),
                }
                crew_row["movie_id" if media_type == MediaType.MOVIE else "series_id"] = detail.id
                crew_rows.append(crew_row)

        association_tables = (
            (movie_genres, movie_keywords, MovieCast, MovieCrew)
            if media_type == MediaType.MOVIE
            else (series_genres, series_keywords, SeriesCast, SeriesCrew)
        )
        genre_table, keyword_table, cast_model, crew_model = association_tables

        self._insert_rows(db, genre_table, genre_associations)
        self._insert_rows(db, keyword_table, keyword_associations)
        self._insert_rows(db, cast_model, cast_rows)
        self._insert_rows(db, crew_model, crew_rows)
        db.commit()

    @staticmethod
    def _ensure_lookup_rows(
        db: Session,
        model,
        rows: Iterable[dict],
    ) -> dict[int, int]:
        unique_rows = {
            int(row["external_id"]): row
            for row in rows
        }
        if not unique_rows:
            return {}

        external_ids = list(unique_rows)
        existing = db.execute(
            select(model).where(model.external_id.in_(external_ids))
        ).scalars().all()
        by_external_id = {
            int(row.external_id): row
            for row in existing
        }
        existing_names = {row.name for row in existing}
        missing_rows = [
            {
                "external_id": external_id,
                "name": row["name"],
            }
            for external_id, row in unique_rows.items()
            if external_id not in by_external_id
            and row["name"] not in existing_names
        ]

        if missing_rows:
            db.execute(
                pg_insert(model)
                .values(missing_rows)
                .on_conflict_do_nothing()
            )

        all_rows = db.execute(
            select(model).where(
                or_(
                    model.external_id.in_(external_ids),
                    model.name.in_([row["name"] for row in unique_rows.values()]),
                )
            )
        ).scalars().all()
        by_external_id = {
            int(row.external_id): row
            for row in all_rows
            if int(row.external_id) in unique_rows
        }
        by_name = {row.name: row for row in all_rows}
        for external_id, lookup_row in unique_rows.items():
            if external_id not in by_external_id and lookup_row["name"] in by_name:
                by_external_id[external_id] = by_name[lookup_row["name"]]
        missing_ids = set(unique_rows) - set(by_external_id)
        if missing_ids:
            raise RuntimeError(f"Could not resolve lookup rows: {sorted(missing_ids)}")
        return {external_id: row.id for external_id, row in by_external_id.items()}

    @staticmethod
    def _ensure_people(db: Session, rows: Iterable[dict]) -> dict[int, int]:
        unique_rows = {
            int(row["external_id"]): row
            for row in rows
        }
        if not unique_rows:
            return {}

        external_ids = list(unique_rows)
        existing = db.execute(
            select(Person).where(Person.external_id.in_(external_ids))
        ).scalars().all()
        existing_ids = {int(person.external_id) for person in existing}
        missing_rows = [
            {
                "external_id": external_id,
                "name": row["name"],
            }
            for external_id, row in unique_rows.items()
            if external_id not in existing_ids
        ]
        if missing_rows:
            db.execute(
                pg_insert(Person)
                .values(missing_rows)
                .on_conflict_do_nothing()
            )

        people = db.execute(
            select(Person).where(Person.external_id.in_(external_ids))
        ).scalars()
        return {int(person.external_id): person.id for person in people}

    @staticmethod
    def _insert_rows(db: Session, model_or_table, rows: list[dict]) -> None:
        if not rows:
            return
        db.execute(
            pg_insert(model_or_table)
            .values(rows)
            .on_conflict_do_nothing()
        )