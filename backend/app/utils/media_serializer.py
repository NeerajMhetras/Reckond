from app.models.media.entertainment import MediaType


def get_media_details(media):

    if media.media_type == MediaType.MOVIE:

        details = media.movie_details

        if not details:
            return None

        return {
            "runtime": details.runtime,
            "budget": details.budget,
            "revenue": details.revenue,

            "genres": [
                {
                    "id": genre.id,
                    "name": genre.name
                }
                for genre in details.genres
            ],

            "keywords": [
                {
                    "id": keyword.id,
                    "name": keyword.name
                }
                for keyword in details.keywords
            ],

            "cast": [
                {
                    "person": {
                        "id": cast.person.id,
                        "name": cast.person.name
                    },
                    "character": cast.character,
                    "cast_order": cast.cast_order
                }
                for cast in details.cast
            ],

            "crew": [
                {
                    "person": {
                        "id": crew.person.id,
                        "name": crew.person.name
                    },
                    "department": crew.department,
                    "job": crew.job
                }
                for crew in details.crew
            ]
        }

    if media.media_type == MediaType.SERIES:

        details = media.series_details

        if not details:
            return None

        return {
            "series_type": details.series_type,
            "animation_type": details.animation_type,
            "number_of_seasons": details.number_of_seasons,
            "number_of_episodes": details.number_of_episodes
        }

    if media.media_type == MediaType.BOOK:

        details = media.book_details

        if not details:
            return None

        return {
            "isbn": details.isbn,
            "pages": details.pages,
            "publisher": details.publisher,
            "authors": [
                author.name
                for author in details.authors
            ]
        }

    if media.media_type == MediaType.GAME:

        details = media.game_details

        if not details:
            return None

        return {
            "platforms": [
                platform.name
                for platform in details.platforms
            ]
        }

    return None


def build_media_response(media):

    return {
        "id": media.id,
        "title": media.title,
        "description": media.description,
        "poster_url": media.poster_url,
        "release_date": media.release_date,
        "media_type": media.media_type,
        "language": media.language,
        "external_id": media.external_id,
        "external_source": media.external_source,
        "details": get_media_details(media)
    }