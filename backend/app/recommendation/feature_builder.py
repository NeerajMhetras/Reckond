def add_feature(features, value, weight=1):

    if value:
        features.extend(
            [value] * weight
        )


def build_feature_text(media):

    features = []

    # -------------------------
    # Common fields
    # -------------------------

    add_feature(
        features,
        media.title,
        weight=2
    )

    add_feature(
        features,
        media.description,
        weight=1
    )

    # Language has very little recommendation
    # value compared to the other features.
    # We can leave it out for now.

    # -------------------------
    # Movie
    # -------------------------

    if media.movie_details:

        details = media.movie_details

        for genre in details.genres:
            add_feature(
                features,
                genre.name,
                weight=3
            )

        for keyword in details.keywords:
            add_feature(
                features,
                keyword.name,
                weight=2
            )

        for cast in details.cast:

            if cast.person:
                add_feature(
                    features,
                    cast.person.name,
                    weight=2
                )

        for crew in details.crew:

            if crew.person:
                add_feature(
                    features,
                    crew.person.name,
                    weight=3
                )

    # -------------------------
    # Series
    # -------------------------

    elif media.series_details:

        details = media.series_details

        for genre in details.genres:
            add_feature(
                features,
                genre.name,
                weight=3
            )

        for keyword in details.keywords:
            add_feature(
                features,
                keyword.name,
                weight=2
            )

        for cast in details.cast:

            if cast.person:
                add_feature(
                    features,
                    cast.person.name,
                    weight=2
                )

        for crew in details.crew:

            if crew.person:
                add_feature(
                    features,
                    crew.person.name,
                    weight=3
                )

        if details.series_type:
            add_feature(
                features,
                details.series_type.value,
                weight=2
            )

        if details.animation_type:
            add_feature(
                features,
                details.animation_type.value,
                weight=2
            )

    # -------------------------
    # Book
    # -------------------------

    elif media.book_details:

        details = media.book_details

        for author in details.authors:
            add_feature(
                features,
                author.name,
                weight=3
            )

        if details.publisher:
            add_feature(
                features,
                details.publisher,
                weight=1
            )

    # -------------------------
    # Game
    # -------------------------

    elif media.game_details:

        details = media.game_details

        for platform in details.platforms:
            add_feature(
                features,
                platform.name,
                weight=1
            )

    return " ".join(features).lower()