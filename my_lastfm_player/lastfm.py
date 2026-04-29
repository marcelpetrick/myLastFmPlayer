from __future__ import annotations

import logging
import re
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol
from urllib.parse import quote, urljoin

import requests
from bs4 import BeautifulSoup, Tag

from my_lastfm_player.models import Track
from my_lastfm_player.storage import JsonTrackRepository
from my_lastfm_player.version import __version__

LASTFM_BASE_URL = "https://www.last.fm"
REQUEST_TIMEOUT_SECONDS = 20
LASTFM_RETRY_ATTEMPTS = 3
LASTFM_RETRY_DELAY_SECONDS = 1.0
LASTFM_HEADERS = {
    "User-Agent": (
        f"myLastFmPlayer/{__version__} "
        "(https://github.com/local/myLastFmPlayer; mail@marcelpetrick.it)"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
LOGGER = logging.getLogger(__name__)
TOTAL_COUNT_PATTERNS = (
    re.compile(r"([\d,]+)\s+loved\s+tracks", re.IGNORECASE),
    re.compile(r"loved\s+tracks\s*\(([\d,]+)\)", re.IGNORECASE),
)
UNAVAILABLE_TITLE_PATTERN = re.compile(
    r"<title>\s*Last\.fm\s*-\s*Temporarily Unavailable\s*</title>",
    re.I,
)


class LastFmError(RuntimeError):
    """Raised when Last.fm loved tracks cannot be fetched or parsed."""


class HttpSession(Protocol):
    def get(self, url: str, *, timeout: int) -> requests.Response: ...


@dataclass(frozen=True, slots=True)
class LovedTracksPage:
    tracks: list[Track]
    next_url: str | None
    total_tracks: int | None = None


@dataclass(frozen=True, slots=True)
class FetchedHtmlPage:
    url: str
    html: str


@dataclass(frozen=True, slots=True)
class FetchProgress:
    fetched_count: int
    message: str
    total_count: int | None = None


ProgressCallback = Callable[[FetchProgress], None]


class LastFmLovedTracksFetcher:
    def __init__(
        self,
        session: HttpSession | None = None,
        base_url: str = LASTFM_BASE_URL,
        retry_attempts: int = LASTFM_RETRY_ATTEMPTS,
        retry_delay_seconds: float = LASTFM_RETRY_DELAY_SECONDS,
    ) -> None:
        self.session = session or requests.Session()
        self.base_url = base_url.rstrip("/")
        self.retry_attempts = retry_attempts
        self.retry_delay_seconds = retry_delay_seconds
        if isinstance(self.session, requests.Session):
            self.session.headers.update(LASTFM_HEADERS)

    def loved_tracks_url(self, username: str) -> str:
        url = f"{self.base_url}/user/{quote(username, safe='')}/loved"
        LOGGER.info("Recognized Last.fm user %s; loved-track URL is %s", username, url)
        return url

    def fetch_page(self, url: str) -> FetchedHtmlPage:
        attempts = max(1, self.retry_attempts)
        last_error: LastFmError | None = None

        for attempt in range(1, attempts + 1):
            LOGGER.info(
                "Fetching Last.fm HTML document: %s (attempt %s/%s)",
                url,
                attempt,
                attempts,
            )
            try:
                response = self.session.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
                self._raise_for_unsuccessful_response(response, url)
            except (LastFmError, requests.RequestException) as error:
                last_error = _to_lastfm_error(url, error)
                LOGGER.warning(
                    "Last.fm HTML fetch attempt %s/%s failed for %s: %s",
                    attempt,
                    attempts,
                    url,
                    last_error,
                )
                if attempt < attempts and _is_retryable_error(error):
                    time.sleep(self.retry_delay_seconds)
                    continue
                raise last_error from error

            html = response.text
            LOGGER.info("Fetched Last.fm HTML document from %s (%s bytes)", response.url, len(html))
            return FetchedHtmlPage(url=response.url, html=html)

        raise last_error or LastFmError(f"Could not fetch Last.fm loved tracks from {url}")

    def _raise_for_unsuccessful_response(self, response: requests.Response, url: str) -> None:
        status_code = response.status_code
        if status_code >= 400:
            raise LastFmError(
                f"Could not fetch Last.fm loved tracks from {url}: "
                f"Last.fm returned HTTP status {status_code}"
            )
        if UNAVAILABLE_TITLE_PATTERN.search(response.text):
            raise LastFmError(
                f"Could not fetch Last.fm loved tracks from {url}: "
                "Last.fm returned a temporary unavailable page"
            )
        response.raise_for_status()


class LastFmLovedTracksParser:
    def parse(self, html: str, page_url: str) -> LovedTracksPage:
        LOGGER.info("Parsing Last.fm loved-track HTML with BeautifulSoup: %s", page_url)
        soup = BeautifulSoup(html, "html.parser")
        tracks = [_parse_track_row(row, page_url) for row in _find_track_rows(soup)]
        parsed_tracks = [track for track in tracks if track is not None]
        page = LovedTracksPage(
            tracks=parsed_tracks,
            next_url=_find_next_page_url(soup, page_url),
            total_tracks=_find_total_tracks(soup),
        )
        LOGGER.info(
            "Parsed Last.fm loved-track page %s: tracks=%s total=%s next=%s",
            page_url,
            len(page.tracks),
            page.total_tracks,
            page.next_url,
        )
        return page


class LastFmLovedTracksScraper:
    def __init__(
        self,
        session: HttpSession | None = None,
        base_url: str = LASTFM_BASE_URL,
        fetcher: LastFmLovedTracksFetcher | None = None,
        parser: LastFmLovedTracksParser | None = None,
    ) -> None:
        self.fetcher = fetcher or LastFmLovedTracksFetcher(session=session, base_url=base_url)
        self.parser = parser or LastFmLovedTracksParser()

    def fetch_loved_tracks(
        self,
        username: str,
        max_pages: int | None = None,
        progress_callback: ProgressCallback | None = None,
    ) -> list[Track]:
        if not username:
            raise ValueError("Last.fm username must not be empty")
        if max_pages is not None and max_pages < 1:
            raise ValueError("max_pages must be positive when provided")

        tracks: list[Track] = []
        next_url: str | None = self.loved_tracks_url(username)
        page_count = 0
        total_count: int | None = None
        LOGGER.info(
            "Starting Last.fm loved-track fetch for user %s; pagination limit=%s",
            username,
            max_pages or "none",
        )

        while next_url is not None:
            if max_pages is not None and page_count >= max_pages:
                LOGGER.info(
                    "Stopping Last.fm loved-track fetch for user %s after %s page(s) due to limit",
                    username,
                    max_pages,
                )
                break
            page_count += 1

            LOGGER.info(
                "Fetching Last.fm loved-track page %s for user %s: %s",
                page_count,
                username,
                next_url,
            )
            fetched_page = self.fetcher.fetch_page(next_url)
            if page_count == 1:
                _emit_progress(
                    progress_callback,
                    FetchProgress(0, f"Found Last.fm user {username}"),
                )
            page = self.parser.parse(fetched_page.html, fetched_page.url)
            if page.total_tracks is not None:
                total_count = page.total_tracks
            tracks.extend(page.tracks)
            next_url = page.next_url
            LOGGER.info(
                "Fetched %s tracks from page %s for user %s; cumulative=%s total=%s",
                len(page.tracks),
                page_count,
                username,
                len(tracks),
                total_count,
            )
            _emit_progress(
                progress_callback,
                FetchProgress(
                    fetched_count=len(tracks),
                    total_count=total_count,
                    message=_progress_message(len(tracks), total_count),
                ),
            )

        LOGGER.info(
            "Finished Last.fm loved-track fetch for user %s with %s tracks across %s page(s)",
            username,
            len(tracks),
            page_count,
        )
        return tracks

    def fetch_and_store_loved_tracks(
        self,
        username: str,
        repository: JsonTrackRepository,
        max_pages: int | None = None,
        progress_callback: ProgressCallback | None = None,
    ) -> list[Track]:
        tracks = self.fetch_loved_tracks(
            username,
            max_pages=max_pages,
            progress_callback=progress_callback,
        )
        repository.save_tracks(username, tracks)
        LOGGER.info("Stored %s Last.fm loved tracks for user %s", len(tracks), username)
        return tracks

    def loved_tracks_url(self, username: str) -> str:
        return self.fetcher.loved_tracks_url(username)


def parse_loved_tracks_page(html: str, page_url: str) -> LovedTracksPage:
    return LastFmLovedTracksParser().parse(html, page_url)


def _find_track_rows(soup: BeautifulSoup) -> list[Tag]:
    rows = soup.select("tr.chartlist-row")
    if rows:
        return rows
    return [
        row
        for row in soup.select("tr")
        if row.select_one(".chartlist-name a") and row.select_one(".chartlist-artist a")
    ]


def _parse_track_row(row: Tag, page_url: str) -> Track | None:
    title_link = row.select_one(".chartlist-name a")
    artist_link = row.select_one(".chartlist-artist a")
    if title_link is None or artist_link is None:
        return None

    title = _clean_text(title_link.get_text(" ", strip=True))
    artist = _clean_text(artist_link.get_text(" ", strip=True))
    if not title or not artist:
        return None

    lastfm_url = None
    href = title_link.get("href")
    if isinstance(href, str) and href:
        lastfm_url = urljoin(page_url, href)

    return Track(artist=artist, title=title, lastfm_url=lastfm_url)


def _find_next_page_url(soup: BeautifulSoup, page_url: str) -> str | None:
    next_link = soup.select_one("a[rel='next']")
    if next_link is None:
        next_link = soup.select_one("a.pagination-next")
    if next_link is None:
        next_link = soup.select_one(".pagination-next a")
    if next_link is None:
        return None

    if "disabled" in next_link.get("class", []):
        return None
    if next_link.get("aria-disabled") == "true":
        return None

    href = next_link.get("href")
    if not isinstance(href, str) or not href:
        return None
    return urljoin(page_url, href)


def _clean_text(value: str) -> str:
    return " ".join(value.split())


def _find_total_tracks(soup: BeautifulSoup) -> int | None:
    explicit_total = soup.select_one("[data-total-tracks]")
    if explicit_total is not None:
        total_value = explicit_total.get("data-total-tracks")
        if isinstance(total_value, str):
            return _parse_count(total_value)

    page_text = _clean_text(soup.get_text(" ", strip=True))
    for pattern in TOTAL_COUNT_PATTERNS:
        match = pattern.search(page_text)
        if match:
            return _parse_count(match.group(1))
    return None


def _parse_count(value: str) -> int | None:
    try:
        return int(value.replace(",", ""))
    except ValueError:
        return None


def _progress_message(fetched_count: int, total_count: int | None) -> str:
    if total_count is None:
        return f"Fetched {fetched_count} tracks"
    return f"Fetched {fetched_count}/{total_count} tracks"


def _emit_progress(progress_callback: ProgressCallback | None, progress: FetchProgress) -> None:
    if progress_callback is not None:
        progress_callback(progress)


def _to_lastfm_error(url: str, error: LastFmError | requests.RequestException) -> LastFmError:
    if isinstance(error, LastFmError):
        return error
    return LastFmError(f"Could not fetch Last.fm loved tracks from {url}: {error}")


def _is_retryable_error(error: LastFmError | requests.RequestException) -> bool:
    if isinstance(error, requests.RequestException):
        return True
    return (
        "HTTP status 600" in str(error)
        or "HTTP status 502" in str(error)
        or "HTTP status 503" in str(error)
        or "HTTP status 504" in str(error)
        or "temporary unavailable page" in str(error)
    )
