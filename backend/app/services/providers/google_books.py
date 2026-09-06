import httpx
from app.schemas.media.entertainment import MediaType
from datetime import date
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential


def should_retry_google_books(error: BaseException) -> bool:
    if isinstance(error, (httpx.ConnectError, httpx.TimeoutException)):
        return True
    return (
        isinstance(error, httpx.HTTPStatusError)
        and error.response.status_code in (429, 500, 502, 503, 504)
    )


google_books_retry = retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception(should_retry_google_books),
    reraise=True,
)


class GoogleBooksProvider:

    BASE_URL = "https://www.googleapis.com/books/v1"

    def __init__(self, api_key: str):
        self.api_key = api_key

    @google_books_retry
    async def search_book(
        self,
        query: str,
        client: httpx.AsyncClient | None = None,
        start_index: int = 0,
        max_results: int = 40,
    ):

        url = f"{self.BASE_URL}/volumes"

        params = {
            "q": query,
            "key": self.api_key,
            "startIndex": start_index,
            "maxResults": min(max_results, 40),
        }

        if client is None:
            async with httpx.AsyncClient(timeout=30.0) as request_client:
                response = await request_client.get(url, params=params)
        else:
            response = await client.get(url, params=params)

        if response.status_code != 200:
            if response.status_code == 429 or response.status_code >= 500:
                raise httpx.HTTPStatusError(
                    "Retryable Google Books response",
                    request=response.request,
                    response=response,
                )
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

    @google_books_retry
    async def get_book_details(
        self,
        book_id: str,
        client: httpx.AsyncClient | None = None,
    ):

        url = f"{self.BASE_URL}/volumes/{book_id}"

        params = {
            "key": self.api_key
        }

        if client is None:
            async with httpx.AsyncClient(timeout=30.0) as request_client:
                response = await request_client.get(url, params=params)
        else:
            response = await client.get(url, params=params)

        if response.status_code == 429 or response.status_code >= 500:
            raise httpx.HTTPStatusError(
                "Retryable Google Books response",
                request=response.request,
                response=response,
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