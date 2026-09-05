from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import httpx

from app.schemas.media.search import SearchResult
from app.models.media.entertainment import MediaType
from app.models.media.series.series import SeriesType, AnimationType


tmdb_retry = retry(
    stop=stop_after_attempt(10),
    wait=wait_exponential(multiplier=1, min=2, max=6),
    retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException)),
    reraise=True 
)


class TMDBProvider:

    def __init__(self, api_key: str):
        self.api_key = api_key

    @tmdb_retry
    async def search_movie(self, query: str):
        url = "https://api.themoviedb.org/3/search/movie"

        params = {
            "api_key": self.api_key,
            "query": query
        }

        transport = httpx.AsyncHTTPTransport(
            local_address="0.0.0.0"
        )

        async with httpx.AsyncClient(
            transport=transport,
            timeout=100.0,
            verify=False
        ) as client:
            response = await client.get(
                url,
                params=params
            )

        response.raise_for_status()

        data = response.json()

        return [
            self._normalize_movie_search_results(movie)
            for movie in data["results"]
        ]
    
    @tmdb_retry
    async def search_series(self, query: str):
        url = "https://api.themoviedb.org/3/search/tv"

        params = {"api_key": self.api_key, "query": query}

        transport = httpx.AsyncHTTPTransport(local_address="0.0.0.0")

        async with httpx.AsyncClient(transport=transport,timeout=100.0) as client:
            response = await client.get(url,params=params)

        response.raise_for_status()
        data = response.json()

        return self._normalize_series_search_results(data)

    @tmdb_retry
    async def get_series_details(self, series_id: str):
    
            url = f"https://api.themoviedb.org/3/tv/{series_id}"
    
            params = {
                "api_key": self.api_key,
                "append_to_response": "credits,keywords"
            }
    
            transport = httpx.AsyncHTTPTransport(
                local_address="0.0.0.0"
            )
    
            async with httpx.AsyncClient(
                transport=transport,
                timeout=100.0
            ) as client:
    
                response = await client.get(
                    url,
                    params=params
                )
    
            response.raise_for_status()
    
            data = response.json()

            return self._normalize_series_details(data)

    @tmdb_retry
    async def get_movie_details(self, movie_id: str):
            url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    
            params = {
                "api_key": self.api_key,
                "append_to_response": "credits,keywords",
            }
    
            transport = httpx.AsyncHTTPTransport(
                local_address="0.0.0.0"
            )
    
            async with httpx.AsyncClient(
                transport=transport,
                timeout=100.0
            ) as client:
    
                response = await client.get(
                    url,
                    params=params
                )
    
            response.raise_for_status()
    
            data = response.json()
            return self._normalize_movie_details(data)

    def _normalize_movie_search_results(self, movie: dict) -> SearchResult:

        poster_path = movie.get("poster_path")

        poster_url = None

        if poster_path:
            poster_url = (
                "https://image.tmdb.org/t/p/w500"
                + poster_path
            )

        return SearchResult(
            external_id=str(movie["id"]),
            title=movie["title"],
            media_type=MediaType.MOVIE,
            description=movie.get("overview"),
            release_date=movie.get("release_date"),
            poster_url=poster_url
        )

    def _normalize_movie_details(self, movie: dict):

        credits = movie.get("credits", {})

        return {
            "external_id": str(movie["id"]),
            "external_source": "TMDB",

            "title": movie["title"],
            "description": movie.get("overview"),

            "poster_url": (
                f"https://image.tmdb.org/t/p/w500{movie['poster_path']}"
                if movie.get("poster_path")
                else None
            ),

            "backdrop_url": (
                f"https://image.tmdb.org/t/p/w1280{movie['backdrop_path']}"
                if movie.get("backdrop_path")
                else None
            ),

            "release_date": movie.get("release_date"),
            "language": movie.get("original_language"),

            "runtime": movie.get("runtime"),
            "budget": movie.get("budget"),
            "revenue": movie.get("revenue"),

            "genres": [
                {
                    "external_id": genre["id"],
                    "name": genre["name"]
                }
                for genre in movie.get("genres", [])
            ],

            "keywords": [
                {
                    "external_id": keyword["id"],
                    "name": keyword["name"]
                }
                for keyword in movie.get("keywords", {}).get("keywords", [])
            ],

            "cast": [
                {
                    "external_id": person["id"],
                    "name": person["name"],
                    "character": person.get("character"),
                    "cast_order": person.get("order")
                }
                for person in credits.get("cast", [])
            ],

            "crew": [
                {
                    "external_id": person["id"],
                    "name": person["name"],
                    "department": person.get("department"),
                    "job": person.get("job")
                }
                for person in credits.get("crew", [])
            ]
        }

    def _normalize_series_search_results(self, data: dict):
        results = []
        for series in data.get("results",[]):
            results.append({
                "external_id": str(series["id"]),
                "title": series["name"],
                "description": series.get("overview"),
                "poster_url": (
                    f"https://image.tmdb.org/t/p/w500"
                    f"{series['poster_path']}"
                    if series.get("poster_path")
                    else None
                ),
                "release_date": series.get("first_air_date"),
                "media_type": "series",
                "language": series.get("original_language"),
            })
        return results

    def _normalize_series_details(self, series: dict):

        genre_ids = {
            genre["id"]
            for genre in series.get("genres", [])
        }

        is_animated = 16 in genre_ids

        if is_animated:
            series_type = SeriesType.ANIMATED

            language = series.get("original_language")

            if language == "ja":
                animation_type = AnimationType.ANIME
            elif language == "en":
                animation_type = AnimationType.WESTERN
            else:
                animation_type = AnimationType.OTHER

        else:
            series_type = SeriesType.TV
            animation_type = None

        # -------------------------
        # Genres
        # -------------------------

        genres = [
            {
                "external_id": genre["id"],
                "name": genre["name"]
            }
            for genre in series.get("genres", [])
        ]

        # -------------------------
        # Keywords
        # -------------------------

        keyword_data = series.get("keywords", {})

        keywords = [
            {
                "external_id": keyword["id"],
                "name": keyword["name"]
            }
            for keyword in keyword_data.get("results", [])
        ]

        # -------------------------
        # Credits
        # -------------------------

        credits = series.get("credits", {})

        cast = [
            {
                "external_id": person["id"],
                "name": person["name"],
                "character": person.get("character"),
                "cast_order": person.get("order")
            }
            for person in credits.get("cast", [])[:20]
        ]
        IMPORTANT_CREW_JOBS = {
            "Director",
            "Creator",
            "Executive Producer",
            "Writer",
            "Screenplay",
            "Story"
        }

        crew = [
            {
                "external_id": person["id"],
                "name": person["name"],
                "department": person.get("department"),
                "job": person.get("job")
            }
            for person in credits.get("crew", [])[:20]
            if person.get("job") in IMPORTANT_CREW_JOBS
        ]

        return {
            # -------------------------
            # Entertainment
            # -------------------------

            "external_id": str(series["id"]),
            "external_source": "TMDB",

            "title": series["name"],
            "description": series.get("overview"),

            "poster_url": (
                f"https://image.tmdb.org/t/p/w500"
                f"{series['poster_path']}"
                if series.get("poster_path")
                else None
            ),

            "backdrop_url": (
                f"https://image.tmdb.org/t/p/w1280"
                f"{series['backdrop_path']}"
                if series.get("backdrop_path")
                else None
            ),

            "release_date": series.get("first_air_date"),

            "language": series.get(
                "original_language"
            ),

            "media_type": MediaType.SERIES,

            # -------------------------
            # SeriesDetails
            # -------------------------

            "series_type": series_type,

            "animation_type": animation_type,

            "number_of_seasons": series.get(
                "number_of_seasons"
            ),

            "number_of_episodes": series.get(
                "number_of_episodes"
            ),

            # -------------------------
            # Recommendation metadata
            # -------------------------

            "genres": genres,

            "keywords": keywords,

            "cast": cast,

            "crew": crew
        }