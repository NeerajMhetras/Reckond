from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.models.media.entertainment import Entertainment
from app.recommendation.feature_builder import build_feature_text


def get_all_media_with_features(db: Session):

    media_list = (
        db.query(Entertainment)
        .all()
    )

    feature_texts = [
        build_feature_text(media)
        for media in media_list
    ]

    return media_list, feature_texts

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

    media_list, feature_texts = (
        get_all_media_with_features(db)
    )

    if not media_list:
        return []

    vectorizer, tfidf_matrix = (
        build_tfidf_matrix(feature_texts)
    )

    target_index = None

    for index, media in enumerate(media_list):

        if media.id == entertainment_id:
            target_index = index
            break

    if target_index is None:
        return []

    similarity_scores = cosine_similarity(
        tfidf_matrix[target_index],
        tfidf_matrix
    )[0]

    ranked_indices = similarity_scores.argsort()[::-1]

    recommendations = []

    for index in ranked_indices:

        if index == target_index:
            continue

        recommendations.append(
            {
                "media": media_list[index],
                "score": float(
                    similarity_scores[index]
                )
            }
        )

        if len(recommendations) >= limit:
            break

    return recommendations