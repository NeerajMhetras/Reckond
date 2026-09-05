from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.models.media.entertainment import Entertainment
from app.recommendation.feature_builder import build_feature_text


_feature_cache = None


def get_all_media_with_features(db: Session):
    global _feature_cache

    media_ids = tuple(
        media_id
        for (media_id,) in db.query(Entertainment.id)
        .order_by(Entertainment.id)
        .all()
    )

    if _feature_cache and _feature_cache["media_ids"] == media_ids:
        return _feature_cache["media_ids"], _feature_cache["feature_texts"]

    media_list = (
        db.query(Entertainment)
        .filter(Entertainment.id.in_(media_ids))
        .order_by(Entertainment.id)
        .all()
    )

    feature_texts = [build_feature_text(media) for media in media_list]
    _feature_cache = {
        "media_ids": media_ids,
        "feature_texts": feature_texts,
        "vectorizer": None,
        "tfidf_matrix": None,
    }

    return media_ids, feature_texts

def build_tfidf_matrix(feature_texts):

    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    tfidf_matrix = vectorizer.fit_transform(
        feature_texts
    )

    return vectorizer, tfidf_matrix

def get_similar_media(
    db: Session,
    entertainment_id: int,
    limit: int = 10
):

    media_ids, feature_texts = (
        get_all_media_with_features(db)
    )

    if not media_ids:
        return []

    global _feature_cache
    if _feature_cache["tfidf_matrix"] is None:
        _feature_cache["vectorizer"], _feature_cache["tfidf_matrix"] = build_tfidf_matrix(feature_texts)

    tfidf_matrix = _feature_cache["tfidf_matrix"]
    media_index = {
        media_id: index
        for index, media_id in enumerate(media_ids)
    }

    try:
        target_index = media_ids.index(entertainment_id)
    except ValueError:
        target_index = None

    if target_index is None:
        return []

    similarity_scores = cosine_similarity(
        tfidf_matrix[target_index],
        tfidf_matrix
    )[0]

    ranked_indices = similarity_scores.argsort()[::-1]

    ranked_media_ids = []

    for index in ranked_indices:

        if index == target_index:
            continue

        ranked_media_ids.append(media_ids[index])

        if len(ranked_media_ids) >= limit:
            break

    media_list = (
        db.query(Entertainment)
        .filter(Entertainment.id.in_(ranked_media_ids))
        .all()
    )
    media_map = {media.id: media for media in media_list}

    return [
        {
            "media": media_map[media_id],
            "score": float(similarity_scores[media_index[media_id]]),
        }
        for media_id in ranked_media_ids
        if media_id in media_map
    ]