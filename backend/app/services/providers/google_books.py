import httpx
from app.schemas.media.entertainment import MediaType
from datetime import date
class GoogleBooksProvider:

    BASE_URL = "https://www.googleapis.com/books/v1"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def search_book(self, query: str):

        url = f"{self.BASE_URL}/volumes"

        params = {
            "q": query,
            "key": self.api_key
        }

        async with httpx.AsyncClient(
            timeout=30.0
        ) as client:

            response = await client.get(
                url,
                params=params
            )

        if response.status_code != 200:
            print("Google Books status:", response.status_code)
            print("Google Books response:", response.text)
        response.raise_for_status()

        data = response.json()

        return self._normalize_search_results(data)

    def _normalize_search_results(self, data: dict):
        results = []
        for item in data.get("items",[]):
            volume = item.get("volumeInfo",{})
            title = volume.get("title")
            if not title:
                continue
            results.append({
                "external_id": item["id"],
                "title": title,
                "description": volume.get("description"),
                "poster_url":(
                    volume.get("imageLinks",{}).get("thumbnail")
                ),
                "release_date": volume.get("publishedDate"),
                "media_type": "book",
                "language": volume.get("language")
            })

        return results

    async def get_book_details(self, book_id: str):

        url = f"{self.BASE_URL}/volumes/{book_id}"

        params = {
            "key": self.api_key
        }

        async with httpx.AsyncClient(
            timeout=30.0
        ) as client:

            response = await client.get(
                url,
                params=params
            )

        response.raise_for_status()

        data = response.json()
        return self._normalize_book_details(data)

    def _parse_release_date(self, value: str | None):

        if not value:
            return None

        try:
            # YYYY-MM-DD
            if len(value) == 10:
                return date.fromisoformat(value)

            # YYYY-MM
            if len(value) == 7:
                return date.fromisoformat(value + "-01")

            # YYYY
            if len(value) == 4:
                return date.fromisoformat(value + "-01-01")

        except ValueError:
            return None

        return None
    
    def _normalize_book_details(self, data: dict):

        volume = data.get("volumeInfo", {})

        isbn = None

        for identifier in volume.get("industryIdentifiers", []):
            if identifier.get("type") == "ISBN_13":
                isbn = identifier.get("identifier")
                break

        if isbn is None:
            for identifier in volume.get("industryIdentifiers", []):
                if identifier.get("type") == "ISBN_10":
                    isbn = identifier.get("identifier")
                    break

        return {
            "external_id": data["id"],
            "external_source": "GOOGLE_BOOKS",

            "title": volume.get("title"),
            "description": volume.get("description"),

            "poster_url": (
                volume.get("imageLinks", {})
                .get("thumbnail")
            ),

            "release_date": self._parse_release_date(volume.get("publishedDate")),
            "language": volume.get("language"),

            "isbn": isbn,
            "pages": volume.get("pageCount"),
            "publisher": volume.get("publisher"),

            "authors": volume.get("authors", []),

            "media_type": MediaType.BOOK
        }