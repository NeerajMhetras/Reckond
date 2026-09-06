import httpx
from datetime import datetime
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from app.models.media.entertainment import MediaType
from app.schemas.media.search import SearchResult


def should_retry_igdb(error: BaseException) -> bool:
    if isinstance(error, (httpx.ConnectError, httpx.TimeoutException)):
        return True
    return (
        isinstance(error, httpx.HTTPStatusError)
        and error.response.status_code in (429, 500, 502, 503, 504)
    )


class IGDBProvider:
    BASE_URL = "https://api.igdb.com/v4"
    TOKEN_URL = "https://id.twitch.tv/oauth2/token"

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None

    async def _get_access_token(self, client: httpx.AsyncClient | None = None):
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
        }

        if client is None:
            async with httpx.AsyncClient(timeout=30.0) as request_client:
                response = await request_client.post(self.TOKEN_URL, data=params)
        else:
            response = await client.post(self.TOKEN_URL, data=params)

        if response.is_error:
            detail = response.json().get("message", "IGDB authentication failed")
            raise RuntimeError(detail)

        data = response.json()
        self.access_token = data["access_token"]

        return self.access_token

    async def _get_headers(self, client: httpx.AsyncClient | None = None):
        if not self.access_token:
            await self._get_access_token(client=client)

        return {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
        }

    @staticmethod
    def _retryable_status(response: httpx.Response) -> bool:
        return response.status_code == 429 or response.status_code >= 500

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception(should_retry_igdb),
        reraise=True,
    )
    async def _post_games(
        self,
        body: str,
        client: httpx.AsyncClient,
    ) -> list[dict]:
        headers = await self._get_headers(client=client)
        response = await client.post(
            f"{self.BASE_URL}/games",
            headers=headers,
            content=body,
        )
        if self._retryable_status(response):
            raise httpx.HTTPStatusError(
                "Retryable IGDB response",
                request=response.request,
                response=response,
            )
        response.raise_for_status()
        return response.json()

    async def get_popular_games(
        self,
        client: httpx.AsyncClient,
        limit: int = 200,
    ) -> list[dict]:
        body = f"""
            fields id,name,summary,cover.url,first_release_date,platforms.name;
            where version_parent = null & name != null;
            sort rating_count desc;
            limit {min(limit, 500)};
        """
        games = await self._post_games(body, client)
        return [self._normalize_game_details(game) for game in games]

    async def get_games_by_ids(
        self,
        game_ids: list[str],
        client: httpx.AsyncClient,
    ) -> list[dict]:
        if not game_ids:
            return []
        ids = ",".join(str(game_id) for game_id in game_ids)
        body = f"""
            fields id,name,summary,cover.url,first_release_date,platforms.name;
            where id = ({ids});
            limit {min(len(game_ids), 500)};
        """
        games = await self._post_games(body, client)
        return [self._normalize_game_details(game) for game in games]

    async def search_game(self, query: str):
        headers = await self._get_headers()

        body = f'''
            search "{query}";
            fields id,name,summary,cover.url,first_release_date;
            where version_parent = null;
            limit 20;
        '''

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.BASE_URL}/games",
                headers=headers,
                content=body,
            )

        response.raise_for_status()

        games = response.json()

        return [
            self._normalize_search_result(game)
            for game in games
        ]

    def _normalize_search_result(self, game: dict) -> SearchResult:
        cover = game.get("cover")

        poster_url = None

        if cover and cover.get("url"):
            poster_url = cover["url"].replace(
                "t_thumb",
                "t_cover_big",
            )

        release_date = None

        if game.get("first_release_date"):
            release_date = datetime.fromtimestamp(
                game["first_release_date"]
            ).date().isoformat()

        return SearchResult(
            external_id=str(game["id"]),
            title=game["name"],
            media_type=MediaType.GAME,
            description=game.get("summary"),
            release_date=release_date,
            poster_url=poster_url,
        )

    async def get_game_details(
        self,
        game_id: str,
        client: httpx.AsyncClient | None = None,
    ):
        body = f'''
        fields
            name,summary,cover.url,first_release_date,platforms.name;
            where id = {game_id};
        '''
        if client is None:
            async with httpx.AsyncClient(timeout=30.0) as request_client:
                games = await self._post_games(body, request_client)
        else:
            games = await self._post_games(body, client)

        return self._normalize_game_details(games[0])

    def _normalize_game_details(self, game: dict):

        release_date = None

        if game.get("first_release_date"):
            release_date = datetime.fromtimestamp(
                game["first_release_date"]
            ).date()

        platforms = [
            platform["name"]
            for platform in game.get("platforms", [])
            if platform.get("name")
        ]

        cover_url = None

        if game.get("cover") and game["cover"].get("url"):
            cover_url = game["cover"]["url"]

            if cover_url.startswith("//"):
                cover_url = "https:" + cover_url

            cover_url = cover_url.replace(
                "t_thumb",
                "t_cover_big"
            )

        return {
            "external_id": str(game["id"]),
            "external_source": "IGDB",

            "title": game.get("name"),
            "description": game.get("summary"),

            "poster_url": cover_url,

            "release_date": release_date,

            "language": None,

            "platforms": platforms,

            "media_type": MediaType.GAME
        }
        