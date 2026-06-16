from __future__ import annotations

import logging
import re
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC
from datetime import datetime as _Datetime
from html.parser import HTMLParser as _HTMLParser
from typing import Protocol
from urllib.parse import quote, urljoin

import requests

from my_lastfm_player.app_credentials import lastfm_api_credentials
from my_lastfm_player.i18n import translate
from my_lastfm_player.models import Track
from my_lastfm_player.storage import JsonTrackRepository
from my_lastfm_player.version import __display_version__

LASTFM_BASE_URL = "https://www.last.fm"
LASTFM_API_URL = "https://ws.audioscrobbler.com/2.0/"
REQUEST_TIMEOUT_SECONDS = 20
LASTFM_RETRY_ATTEMPTS = 8
LASTFM_RETRY_DELAY_SECONDS = 2.0
LASTFM_PAGE_DELAY_SECONDS = 0.2
LASTFM_API_PAGE_LIMIT = 200
LASTFM_HEADERS = {
    "User-Agent": (
        f"myLastFmPlayer/{__display_version__} "
        "(https://github.com/local/myLastFmPlayer; mail@marcelpetrick.it)"
    ),
    "Accept": "application/json,text/html;q=0.8,*/*;q=0.5",
    "Accept-Language": "en-US,en;q=0.9",
}
LASTFM_PLACEHOLDER_IMAGE_MARKERS = (
    "2a96cbd8b46e442fc41c2b86b821562f",
)
LOGGER = logging.getLogger(__name__)


class LastFmError(RuntimeError):
    """Raised when Last.fm loved tracks cannot be fetched or parsed."""


class HttpSession(Protocol):
    """Minimal HTTP session protocol used by the Last.fm fetchers."""

    def get(
        self,
        url: str,
        *,
        params: dict[str, object] | None = None,
        timeout: int,
    ) -> requests.Response:
        """Fetch ``url`` and return a ``requests``-compatible response."""

        ...


@dataclass(frozen=True, slots=True)
class LovedTracksPage:
    """Parsed Last.fm loved-track page plus pagination metadata."""

    tracks: list[Track]
    next_url: str | None
    total_tracks: int | None = None


@dataclass(frozen=True, slots=True)
class LovedTracksApiPage:
    """Parsed Last.fm Web API page plus pagination metadata."""

    tracks: list[Track]
    page: int
    total_pages: int | None = None
    total_tracks: int | None = None

    @property
    def next_page(self) -> int | None:
        """Return the next API page number when the response advertises one."""

        if self.total_pages is None or self.page >= self.total_pages:
            return None
        return self.page + 1


@dataclass(frozen=True, slots=True)
class ArtistImage:
    """Last.fm artist image metadata and downloaded image bytes."""

    artist: str
    page_url: str
    image_url: str | None = None
    image_bytes: bytes | None = None


@dataclass(frozen=True, slots=True)
class FetchProgress:
    """Progress event emitted while fetching paginated loved tracks."""

    fetched_count: int
    message: str
    total_count: int | None = None


ProgressCallback = Callable[[FetchProgress], None]
TracksCallback = Callable[[list[Track]], None]
FetchControlCallback = Callable[[], bool]


class LastFmLovedTracksApiClient:
    """HTTP client for Last.fm's ``user.getLovedTracks`` JSON API."""

    def __init__(
        self,
        api_key: str | None = None,
        session: HttpSession | None = None,
        api_url: str = LASTFM_API_URL,
        retry_attempts: int = LASTFM_RETRY_ATTEMPTS,
        retry_delay_seconds: float = LASTFM_RETRY_DELAY_SECONDS,
        page_limit: int = LASTFM_API_PAGE_LIMIT,
    ) -> None:
        self.api_key = (api_key or lastfm_api_credentials().api_key).strip()
        self.session = session or requests.Session()
        self.api_url = api_url
        self.retry_attempts = retry_attempts
        self.retry_delay_seconds = retry_delay_seconds
        self.page_limit = page_limit
        if isinstance(self.session, requests.Session):
            self.session.headers.update(LASTFM_HEADERS)

    def fetch_page(self, username: str, page: int) -> LovedTracksApiPage:
        """Fetch and parse one loved-track API page for ``username``."""

        if not self.api_key:
            raise LastFmError("Last.fm API key is not configured")
        if page < 1:
            raise ValueError("page must be positive")

        params: dict[str, object] = {
            "method": "user.getLovedTracks",
            "user": username,
            "api_key": self.api_key,
            "format": "json",
            "limit": self.page_limit,
            "page": page,
        }
        attempts = max(1, self.retry_attempts)
        last_error: LastFmError | None = None

        for attempt in range(1, attempts + 1):
            _log_info(
                "Fetching Last.fm loved tracks through API for user %s page %s (attempt %s/%s)",
                username,
                page,
                attempt,
                attempts,
            )
            try:
                response = self.session.get(
                    self.api_url,
                    params=params,
                    timeout=REQUEST_TIMEOUT_SECONDS,
                )
                self._raise_for_unsuccessful_response(response)
                payload = response.json()
            except (LastFmError, requests.RequestException, ValueError) as error:
                last_error = _to_lastfm_error(self.api_url, error)
                _log_warning(
                    "Last.fm API fetch attempt %s/%s failed for user %s page %s: %s",
                    attempt,
                    attempts,
                    username,
                    page,
                    last_error,
                )
                if attempt < attempts and _is_retryable_error(error):
                    time.sleep(self.retry_delay_seconds)
                    continue
                raise last_error from error

            api_page = _parse_loved_tracks_api_payload(payload, page)
            _log_info(
                "Fetched Last.fm API page %s for %s: tracks=%s total=%s pages=%s",
                page,
                username,
                len(api_page.tracks),
                api_page.total_tracks,
                api_page.total_pages,
            )
            return api_page

        raise last_error or LastFmError(f"Could not fetch Last.fm loved tracks from {self.api_url}")

    def _raise_for_unsuccessful_response(self, response: requests.Response) -> None:
        status_code = response.status_code
        if status_code >= 400:
            raise LastFmError(
                "Could not fetch Last.fm loved tracks from the Web API: "
                f"Last.fm returned HTTP status {status_code}"
            )
        response.raise_for_status()


class LastFmArtistInfoClient:
    """HTTP client for Last.fm's ``artist.getInfo`` JSON API."""

    def __init__(
        self,
        api_key: str | None = None,
        session: HttpSession | None = None,
        api_url: str = LASTFM_API_URL,
        retry_attempts: int = LASTFM_RETRY_ATTEMPTS,
        retry_delay_seconds: float = LASTFM_RETRY_DELAY_SECONDS,
    ) -> None:
        self.api_key = (api_key or lastfm_api_credentials().api_key).strip()
        self.session = session or requests.Session()
        self.api_url = api_url
        self.retry_attempts = retry_attempts
        self.retry_delay_seconds = retry_delay_seconds
        if isinstance(self.session, requests.Session):
            self.session.headers.update(LASTFM_HEADERS)

    def fetch_artist_image(self, artist: str) -> ArtistImage:
        """Fetch artist page metadata and a representative image for ``artist``."""

        artist_name = artist.strip()
        if not artist_name:
            raise ValueError("Last.fm artist must not be empty")
        if not self.api_key:
            raise LastFmError("Last.fm API key is not configured")

        payload = self._fetch_artist_info_payload(artist_name)
        artist_image = _parse_artist_image_payload(payload, artist_name)
        image_url = self._select_artist_photo_url(artist_image)
        if image_url is None:
            return ArtistImage(artist=artist_image.artist, page_url=artist_image.page_url)

        return ArtistImage(
            artist=artist_image.artist,
            page_url=artist_image.page_url,
            image_url=image_url,
            image_bytes=self._fetch_image_bytes(image_url),
        )

    def _select_artist_photo_url(self, artist_image: ArtistImage) -> str | None:
        page_image_url = self._fetch_artist_page_image_url(artist_image.page_url)
        if page_image_url is not None:
            return page_image_url
        if _is_lastfm_placeholder_image_url(artist_image.image_url):
            return None
        return artist_image.image_url

    def _fetch_artist_info_payload(self, artist: str) -> object:
        params: dict[str, object] = {
            "method": "artist.getInfo",
            "artist": artist,
            "api_key": self.api_key,
            "format": "json",
        }
        attempts = max(1, self.retry_attempts)
        last_error: LastFmError | None = None

        for attempt in range(1, attempts + 1):
            _log_info(
                "Fetching Last.fm artist info for %s (attempt %s/%s)",
                artist,
                attempt,
                attempts,
            )
            try:
                response = self.session.get(
                    self.api_url,
                    params=params,
                    timeout=REQUEST_TIMEOUT_SECONDS,
                )
                _raise_for_unsuccessful_artist_response(response, self.api_url)
                return response.json()
            except (LastFmError, requests.RequestException, ValueError) as error:
                last_error = _to_lastfm_error(self.api_url, error)
                _log_warning(
                    "Last.fm artist info attempt %s/%s failed for %s: %s",
                    attempt,
                    attempts,
                    artist,
                    last_error,
                )
                if attempt < attempts and _is_retryable_error(error):
                    time.sleep(self.retry_delay_seconds)
                    continue
                raise last_error from error

        raise last_error or LastFmError(f"Could not fetch Last.fm artist info from {self.api_url}")

    def _fetch_image_bytes(self, image_url: str) -> bytes | None:
        try:
            response = self.session.get(image_url, timeout=REQUEST_TIMEOUT_SECONDS)
            _raise_for_unsuccessful_artist_response(response, image_url)
        except (LastFmError, requests.RequestException) as error:
            _log_warning("Could not fetch Last.fm artist image from %s: %s", image_url, error)
            return None

        content = getattr(response, "content", b"")
        if isinstance(content, bytes) and content:
            return content
        text = getattr(response, "text", "")
        return text.encode("utf-8") if isinstance(text, str) and text else None

    def _fetch_artist_page_image_url(self, page_url: str) -> str | None:
        try:
            response = self.session.get(page_url, timeout=REQUEST_TIMEOUT_SECONDS)
            _raise_for_unsuccessful_artist_response(response, page_url)
        except (LastFmError, requests.RequestException) as error:
            _log_warning("Could not fetch Last.fm artist page image from %s: %s", page_url, error)
            return None

        text = getattr(response, "text", "")
        if not isinstance(text, str) or not text:
            return None
        return _select_artist_page_image_url(text, page_url)


class LastFmLovedTracksScraper:
    """High-level Last.fm fetcher that reports progress and stores loved tracks."""

    def __init__(
        self,
        session: HttpSession | None = None,
        base_url: str = LASTFM_BASE_URL,
        api_client: LastFmLovedTracksApiClient | None = None,
        api_key: str | None = None,
        page_delay_seconds: float = LASTFM_PAGE_DELAY_SECONDS,
    ) -> None:
        self.api_client = api_client or LastFmLovedTracksApiClient(
            api_key=api_key,
            session=session,
        )
        self.base_url = base_url.rstrip("/")
        self.page_delay_seconds = page_delay_seconds

    def fetch_loved_tracks(
        self,
        username: str,
        max_pages: int | None = None,
        progress_callback: ProgressCallback | None = None,
        tracks_callback: TracksCallback | None = None,
        control_callback: FetchControlCallback | None = None,
    ) -> list[Track]:
        """Fetch all loved-track pages for ``username`` and return cumulative tracks."""

        if not username:
            raise ValueError("Last.fm username must not be empty")
        if max_pages is not None and max_pages < 1:
            raise ValueError("max_pages must be positive when provided")

        tracks: list[Track] = []
        next_page: int | None = 1
        page_count = 0
        total_count: int | None = None
        _log_info(
            "Starting Last.fm API loved-track fetch for user %s; pagination limit=%s",
            username,
            max_pages or "none",
        )

        while next_page is not None:
            if not _continue_fetching(control_callback):
                _log_info("Stopping Last.fm loved-track fetch for user %s by request", username)
                break
            if max_pages is not None and page_count >= max_pages:
                _log_info(
                    "Stopping Last.fm loved-track fetch for user %s after %s page(s) due to limit",
                    username,
                    max_pages,
                )
                break
            page_count += 1

            _log_info(
                "Fetching Last.fm API loved-track page %s for user %s",
                next_page,
                username,
            )
            page = self.api_client.fetch_page(username, next_page)
            if page_count == 1:
                _emit_progress(
                    progress_callback,
                    FetchProgress(
                        0,
                        translate(
                            "LastFmLovedTracksScraper",
                            "Found Last.fm user {username}",
                            username=username,
                        ),
                    ),
                )
            if page.total_tracks is not None:
                total_count = page.total_tracks
            tracks.extend(page.tracks)
            next_page = page.next_page
            _log_info(
                "Fetched %s tracks from API page %s for user %s; cumulative=%s total=%s",
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
            _emit_tracks(tracks_callback, tracks)
            if next_page is not None and self.page_delay_seconds > 0:
                _log_info(
                    "Waiting %.1f seconds before next Last.fm API page for %s",
                    self.page_delay_seconds,
                    username,
                )
                if not _controlled_sleep(self.page_delay_seconds, control_callback):
                    _log_info(
                        "Stopping Last.fm loved-track fetch for user %s during page delay",
                        username,
                    )
                    break

        _log_info(
            "Finished Last.fm API loved-track fetch for user %s with %s tracks across %s page(s)",
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
        tracks_callback: TracksCallback | None = None,
        control_callback: FetchControlCallback | None = None,
    ) -> list[Track]:
        """Fetch loved tracks for ``username`` and save them in ``repository``."""

        tracks = self.fetch_loved_tracks(
            username,
            max_pages=max_pages,
            progress_callback=progress_callback,
            tracks_callback=tracks_callback,
            control_callback=control_callback,
        )
        tracks = repository.mark_cached_downloads(repository.mark_cached_lookups(tracks))
        merged_tracks = repository.merge_tracks(username, tracks)
        _log_info(
            "Merged %s fetched Last.fm loved tracks into %s stored tracks for user %s",
            len(tracks),
            len(merged_tracks),
            username,
        )
        return merged_tracks

    def fetch_loved_track_count(self, username: str) -> int | None:
        """Fetch the first loved-track API page and return Last.fm's total count."""

        if not username:
            raise ValueError("Last.fm username must not be empty")

        _log_info("Checking online Last.fm loved-track count for user %s", username)
        page = self.api_client.fetch_page(username, 1)
        if page.total_tracks is None:
            _log_info(
                "Last.fm loved-track count for user %s was not present in API response",
                username,
            )
            return None
        _log_info(
            "Last.fm online loved-track count for user %s is %s",
            username,
            page.total_tracks,
        )
        return page.total_tracks

    def loved_tracks_url(self, username: str) -> str:
        """Return the public loved-track URL for ``username``."""

        return f"{self.base_url}/user/{quote(username, safe='')}/loved"


def _parse_loved_tracks_api_payload(payload: object, page: int) -> LovedTracksApiPage:
    if not isinstance(payload, dict):
        raise LastFmError("Last.fm API returned an invalid response")
    if "error" in payload:
        message = payload.get("message") or "unknown Last.fm API error"
        raise LastFmError(f"Last.fm API error: {message}")

    loved_tracks = payload.get("lovedtracks")
    if not isinstance(loved_tracks, dict):
        raise LastFmError("Last.fm API response did not contain loved tracks")

    attrs = loved_tracks.get("@attr")
    if not isinstance(attrs, dict):
        attrs = {}

    tracks_value = loved_tracks.get("track", [])
    track_items = tracks_value if isinstance(tracks_value, list) else [tracks_value]
    tracks = [
        track
        for track in (_parse_loved_track_api_item(item) for item in track_items)
        if track is not None
    ]
    return LovedTracksApiPage(
        tracks=tracks,
        page=_parse_positive_int(attrs.get("page")) or page,
        total_pages=_parse_positive_int(attrs.get("totalPages")),
        total_tracks=_parse_count(str(attrs.get("total", ""))),
    )


def _parse_loved_track_api_item(item: object) -> Track | None:
    if not isinstance(item, dict):
        return None

    title = _clean_text(str(item.get("name", "")))
    artist = _parse_api_artist(item.get("artist"))
    if not title or not artist:
        return None

    url = item.get("url")
    lastfm_url = url if isinstance(url, str) and url else None
    return Track(
        artist=artist,
        title=title,
        lastfm_url=lastfm_url,
        loved_at=_parse_api_loved_at(item.get("date")),
    )


def _parse_artist_image_payload(payload: object, requested_artist: str) -> ArtistImage:
    if not isinstance(payload, dict):
        raise LastFmError("Last.fm API returned an invalid artist response")
    if "error" in payload:
        message = payload.get("message") or "unknown Last.fm API error"
        raise LastFmError(f"Last.fm API error: {message}")

    artist = payload.get("artist")
    if not isinstance(artist, dict):
        raise LastFmError("Last.fm API response did not contain artist information")

    artist_name = _clean_text(requested_artist)
    page_url = artist.get("url")
    page_url = (
        page_url
        if isinstance(page_url, str) and page_url
        else f"{LASTFM_BASE_URL}/music/{quote(artist_name, safe='')}"
    )
    return ArtistImage(
        artist=artist_name,
        page_url=page_url,
        image_url=_select_artist_image_url(artist.get("image")),
    )


def _select_artist_image_url(images: object) -> str | None:
    if not isinstance(images, list):
        return None

    ranked_sizes = ("mega", "extralarge", "large", "medium", "small")
    candidates: dict[str, str] = {}
    for item in images:
        if not isinstance(item, dict):
            continue
        image_url = item.get("#text")
        size = item.get("size")
        if isinstance(image_url, str) and image_url and isinstance(size, str):
            candidates[size.casefold()] = image_url

    for size in ranked_sizes:
        if size in candidates:
            return candidates[size]
    return next(iter(candidates.values()), None)


class _ArtistImageExtractor(_HTMLParser):
    """Minimal stdlib HTML parser for og:image, twitter:image, and header background URLs."""

    def __init__(self) -> None:
        super().__init__()
        self._og_image: str | None = None
        self._twitter_image: str | None = None
        self._header_bg_image: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        d = {k.casefold(): (v or "") for k, v in attrs}
        if tag == "meta":
            if d.get("property", "").casefold() == "og:image" and self._og_image is None:
                self._og_image = d.get("content", "")
            elif d.get("name", "").casefold() == "twitter:image" and self._twitter_image is None:
                self._twitter_image = d.get("content", "")
        elif "header-new-background-image" in d.get("class", "") and self._header_bg_image is None:
            url = _extract_css_background_image_url(d.get("style", ""))
            if url:
                self._header_bg_image = url

    def image_candidates(self) -> tuple[str | None, ...]:
        """Return candidate image URLs in priority order."""

        return (self._og_image, self._twitter_image, self._header_bg_image)


def _select_artist_page_image_url(html: str, page_url: str) -> str | None:
    extractor = _ArtistImageExtractor()
    extractor.feed(html)
    for image_url in extractor.image_candidates():
        if isinstance(image_url, str) and image_url and not _is_lastfm_placeholder_image_url(
            image_url
        ):
            return urljoin(page_url, image_url)
    return None


def _extract_css_background_image_url(style: str) -> str | None:
    match = re.search(
        r"background-image\s*:\s*url\((?P<quote>['\"]?)(?P<url>.+?)(?P=quote)\)",
        style,
    )
    return match.group("url") if match else None


def _is_lastfm_placeholder_image_url(image_url: str | None) -> bool:
    if not image_url:
        return False
    normalized_url = image_url.casefold()
    return any(marker.casefold() in normalized_url for marker in LASTFM_PLACEHOLDER_IMAGE_MARKERS)


def _raise_for_unsuccessful_artist_response(response: requests.Response, url: str) -> None:
    status_code = response.status_code
    if status_code >= 400:
        raise LastFmError(
            f"Could not fetch Last.fm artist information from {url}: "
            f"Last.fm returned HTTP status {status_code}"
        )
    response.raise_for_status()


def _parse_api_artist(value: object) -> str:
    if isinstance(value, dict):
        return _clean_text(str(value.get("name") or value.get("#text") or ""))
    if isinstance(value, str):
        return _clean_text(value)
    return ""


def _parse_api_loved_at(value: object) -> str | None:
    if not isinstance(value, dict):
        return None
    uts = value.get("uts")
    if not isinstance(uts, str) or not uts:
        return None
    try:
        timestamp = int(uts)
    except ValueError:
        return None
    return _Datetime.fromtimestamp(timestamp, tz=UTC).strftime("%Y%m%d-%H%M%S")


def _parse_positive_int(value: object) -> int | None:
    try:
        parsed = int(str(value))
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None


def _clean_text(value: str) -> str:
    return " ".join(value.split())


def _parse_count(value: str) -> int | None:
    try:
        return int(value.replace(",", ""))
    except ValueError:
        return None


def _progress_message(fetched_count: int, total_count: int | None) -> str:
    if total_count is None:
        return translate(
            "LastFmLovedTracksScraper",
            "Fetched {count} tracks",
            count=fetched_count,
        )
    return translate(
        "LastFmLovedTracksScraper",
        "Fetched {done}/{total} tracks",
        done=fetched_count,
        total=total_count,
    )


def _emit_progress(progress_callback: ProgressCallback | None, progress: FetchProgress) -> None:
    _log_info("Fetch progress: %s", progress.message)
    if progress_callback is not None:
        progress_callback(progress)


def _emit_tracks(tracks_callback: TracksCallback | None, tracks: list[Track]) -> None:
    if tracks_callback is not None:
        tracks_callback(list(tracks))


def _continue_fetching(control_callback: FetchControlCallback | None) -> bool:
    return True if control_callback is None else control_callback()


def _controlled_sleep(
    delay_seconds: float,
    control_callback: FetchControlCallback | None,
) -> bool:
    deadline = time.monotonic() + delay_seconds
    while time.monotonic() < deadline:
        if not _continue_fetching(control_callback):
            return False
        time.sleep(min(0.1, max(0.0, deadline - time.monotonic())))
    return _continue_fetching(control_callback)


def _log_info(message: str, *args: object) -> None:
    LOGGER.info(message, *args)


def _log_warning(message: str, *args: object) -> None:
    LOGGER.warning(message, *args)


def _to_lastfm_error(
    url: str,
    error: LastFmError | requests.RequestException | ValueError,
) -> LastFmError:
    if isinstance(error, LastFmError):
        return error
    return LastFmError(f"Could not fetch Last.fm loved tracks from {url}: {error}")


def _is_retryable_error(error: LastFmError | requests.RequestException | ValueError) -> bool:
    if isinstance(error, requests.RequestException):
        return True
    if isinstance(error, ValueError):
        return True
    return (
        "HTTP status 600" in str(error)
        or "HTTP status 502" in str(error)
        or "HTTP status 503" in str(error)
        or "HTTP status 504" in str(error)
        or "temporary unavailable page" in str(error)
    )
