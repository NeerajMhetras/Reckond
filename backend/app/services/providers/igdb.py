import httpx
from datetime import datetime

from app.models.media.entertainment import MediaType
from app.schemas.media.search import SearchResult


class IGDBProvider:
    BASE_URL = "https://api.igdb.com/v4"
    TOKEN_URL = "https://id.twitch.tv/oauth2/token"

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None

    async def _get_access_token(self):
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.TOKEN_URL,
                params=params,
            )

        response.raise_for_status()

        data = response.json()
        self.access_token = data["access_token"]

        return self.access_token

    async def _get_headers(self):
        if not self.access_token:
            await self._get_access_token()

        return {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
        }

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

    async def get_game_details(self, game_id: str):
        headers = await self._get_headers()
        body = f'''
        fields
            name,summary,cover.url,first_release_date,platforms.name;
            where id = {game_id};
        '''
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url=f"{self.BASE_URL}/games",
                headers=headers,
                content=body
            )

        response.raise_for_status()

        games = response.json()

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
        