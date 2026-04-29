from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from urllib.parse import quote, urljoin

import requests
from bs4 import BeautifulSoup, Tag

from my_lastfm_player.models import Track
from my_lastfm_player.storage import JsonTrackRepository

LASTFM_BASE_URL = "https://www.last.fm"
REQUEST_TIMEOUT_SECONDS = 20


class LastFmError(RuntimeError):
    """Raised when Last.fm loved tracks cannot be fetched or parsed."""


class HttpSession(Protocol):
    def get(self, url: str, *, timeout: int) -> requests.Response: ...


@dataclass(frozen=True, slots=True)
class LovedTracksPage:
    tracks: list[Track]
    next_url: str | None


class LastFmLovedTracksScraper:
    def __init__(
        self,
        session: HttpSession | None = None,
        base_url: str = LASTFM_BASE_URL,
    ) -> None:
        self.session = session or requests.Session()
        self.base_url = base_url.rstrip("/")

    def fetch_loved_tracks(self, username: str, max_pages: int | None = None) -> list[Track]:
        if not username:
            raise ValueError("Last.fm username must not be empty")
        if max_pages is not None and max_pages < 1:
            raise ValueError("max_pages must be positive when provided")

        tracks: list[Track] = []
        next_url: str | None = self.loved_tracks_url(username)
        page_count = 0

        while next_url is not None:
            if max_pages is not None and page_count >= max_pages:
                break
            page_count += 1

            response = self._get(next_url)
            page = parse_loved_tracks_page(response.text, response.url)
            tracks.extend(page.tracks)
            next_url = page.next_url

        return tracks

    def fetch_and_store_loved_tracks(
        self,
        username: str,
        repository: JsonTrackRepository,
        max_pages: int | None = None,
    ) -> list[Track]:
        tracks = self.fetch_loved_tracks(username, max_pages=max_pages)
        repository.save_tracks(username, tracks)
        return tracks

    def loved_tracks_url(self, username: str) -> str:
        return f"{self.base_url}/user/{quote(username, safe='')}/loved"

    def _get(self, url: str) -> requests.Response:
        try:
            response = self.session.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
            response.raise_for_status()
            return response
        except requests.RequestException as error:
            message = f"Could not fetch Last.fm loved tracks from {url}: {error}"
            raise LastFmError(message) from error


def parse_loved_tracks_page(html: str, page_url: str) -> LovedTracksPage:
    soup = BeautifulSoup(html, "html.parser")
    tracks = [_parse_track_row(row, page_url) for row in _find_track_rows(soup)]
    parsed_tracks = [track for track in tracks if track is not None]
    return LovedTracksPage(tracks=parsed_tracks, next_url=_find_next_page_url(soup, page_url))


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
