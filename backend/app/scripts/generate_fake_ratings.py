import random

from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models.user.user import User
from app.models.media.entertainment import Entertainment
from app.models.interactions.rating import Rating


FAKE_USERS = 20

MIN_RATINGS = 30
MAX_RATINGS = 50


# Different types of users with different tastes
TASTE_PROFILES = [
    ["Action", "Adventure", "Science Fiction"],
    ["Science Fiction", "Adventure", "Fantasy"],
    ["Comedy", "Animation"],
    ["Comedy", "Drama"],
    ["Crime", "Thriller", "Drama"],
    ["Drama", "Romance"],
    ["Fantasy", "Adventure"],
    ["Action", "Crime", "Thriller"],
    ["Animation", "Fantasy", "Adventure"],
    ["Horror", "Thriller"],
]


def create_fake_users(
    db: Session,
    count: int
):
    users = []

    for i in range(1, count + 1):

        username = f"fake_user_{i}"
        email = f"fake_user_{i}@test.com"

        user = (
            db.query(User)
            .filter(
                User.username == username
            )
            .first()
        )

        if not user:

            user = User(
                username=username,
                email=email,
                password_hash="fake_password_hash"
            )

            db.add(user)
            db.flush()

        users.append(user)

    db.commit()

    return users


def delete_old_fake_ratings(
    db: Session,
    users: list[User]
):
    user_ids = [
        user.id
        for user in users
    ]

    deleted = (
        db.query(Rating)
        .filter(
            Rating.user_id.in_(user_ids)
        )
        .delete(
            synchronize_session=False
        )
    )

    db.commit()

    print(
        f"Deleted {deleted} old fake ratings."
    )


def get_media_genres(media):

    genres = set()

    # -------------------------
    # Movie
    # -------------------------

    if media.movie_details:

        for genre in media.movie_details.genres:
            genres.add(
                genre.name.lower()
            )

    # -------------------------
    # Series
    # -------------------------

    elif media.series_details:

        for genre in media.series_details.genres:
            genres.add(
                genre.name.lower()
            )

    return genres


def calculate_rating(
    media_genres: set[str],
    preferred_genres: list[str]
):

    preferred_genres = {
        genre.lower()
        for genre in preferred_genres
    }

    matching_genres = (
        media_genres
        &
        preferred_genres
    )

    match_count = len(matching_genres)

    # No matching genres
    if match_count == 0:

        rating = random.randint(3, 5)

    # One matching genre
    elif match_count == 1:

        rating = random.randint(6, 8)

    # Two matching genres
    elif match_count == 2:

        rating = random.randint(7, 9)

    # Three or more matching genres
    else:

        rating = random.randint(8, 10)

    # Individual user variation
    rating += random.choice(
        [-1, 0, 0, 0, 1]
    )

    return max(
        1,
        min(10, rating)
    )


def generate_ratings(
    db: Session,
    users: list[User],
    media: list[Entertainment]
):

    for index, user in enumerate(users):

        # Cycle through taste profiles
        preferred_genres = TASTE_PROFILES[
            index % len(TASTE_PROFILES)
        ]

        number_of_ratings = random.randint(
            MIN_RATINGS,
            min(MAX_RATINGS, len(media))
        )

        # --------------------------------
        # Prefer media matching user's taste
        # --------------------------------

        scored_media = []

        for item in media:

            genres = get_media_genres(item)

            matching_genres = (
                genres
                &
                {
                    genre.lower()
                    for genre in preferred_genres
                }
            )

            match_count = len(
                matching_genres
            )

            # Higher chance of selecting
            # media matching user's taste
            if match_count >= 2:

                selection_weight = 5

            elif match_count == 1:

                selection_weight = 3

            else:

                selection_weight = 1

            scored_media.append(
                (item, selection_weight)
            )

        # --------------------------------
        # Weighted selection
        # --------------------------------

        selected_media = []

        available_media = scored_media.copy()

        while (
            available_media
            and
            len(selected_media) < number_of_ratings
        ):

            items = [
                item
                for item, weight
                in available_media
            ]

            weights = [
                weight
                for item, weight
                in available_media
            ]

            selected = random.choices(
                items,
                weights=weights,
                k=1
            )[0]

            selected_media.append(
                selected
            )

            available_media = [
                pair
                for pair in available_media
                if pair[0].id != selected.id
            ]

        # --------------------------------
        # Create ratings
        # --------------------------------

        for item in selected_media:

            genres = get_media_genres(item)

            rating = calculate_rating(
                media_genres=genres,
                preferred_genres=preferred_genres
            )

            db.add(
                Rating(
                    user_id=user.id,
                    entertainment_id=item.id,
                    rating=rating
                )
            )

        print(
            f"{user.username}: "
            f"{len(selected_media)} ratings "
            f"| likes {preferred_genres}"
        )

    db.commit()


def main():

    db = SessionLocal()

    try:

        print(
            "\nCreating fake users..."
        )

        users = create_fake_users(
            db,
            FAKE_USERS
        )

        print(
            f"Using {len(users)} fake users."
        )

        # --------------------------------
        # Delete previous fake ratings
        # --------------------------------

        delete_old_fake_ratings(
            db,
            users
        )

        # --------------------------------
        # Get media
        # --------------------------------

        media = (
            db.query(Entertainment)
            .all()
        )

        print(
            f"Found {len(media)} media items."
        )

        if not media:
            print(
                "No entertainment found."
            )
            return

        # --------------------------------
        # Generate ratings
        # --------------------------------

        print(
            "\nGenerating meaningful ratings..."
        )

        generate_ratings(
            db,
            users,
            media
        )

        print(
            "\nFake ratings generated successfully."
        )

    finally:

        db.close()


if __name__ == "__main__":
    main()