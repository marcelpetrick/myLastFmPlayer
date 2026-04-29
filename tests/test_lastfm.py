from __future__ import annotations

from pathlib import Path

import pytest
import requests

from my_lastfm_player.lastfm import (
    LASTFM_BASE_URL,
    FetchedHtmlPage,
    FetchProgress,
    LastFmError,
    LastFmLovedTracksFetcher,
    LastFmLovedTracksParser,
    LastFmLovedTracksScraper,
    LovedTracksPage,
    parse_loved_tracks_page,
)
from my_lastfm_player.models import Track, TrackStatus
from my_lastfm_player.storage import JsonTrackRepository

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class FakeResponse:
    def __init__(self, text: str, url: str, status_code: int = 200) -> None:
        self.text = text
        self.url = url
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} error")


class FakeSession:
    def __init__(self, responses: dict[str, FakeResponse]) -> None:
        self.responses = responses
        self.requested_urls: list[str] = []

    def get(self, url: str, *, timeout: int) -> FakeResponse:
        self.requested_urls.append(url)
        response = self.responses.get(url)
        if response is None:
            raise requests.ConnectionError(f"No fake response for {url}")
        return response


class SequencedSession:
    def __init__(self, responses: list[FakeResponse]) -> None:
        self.responses = responses
        self.requested_urls: list[str] = []

    def get(self, url: str, *, timeout: int) -> FakeResponse:
        self.requested_urls.append(url)
        if not self.responses:
            raise requests.ConnectionError(f"No fake response for {url}")
        return self.responses.pop(0)


def read_fixture(name: str) -> str:
    return (FIXTURES_DIR / name).read_text(encoding="utf-8")


def test_parse_loved_tracks_page_extracts_tracks_and_next_url() -> None:
    page = parse_loved_tracks_page(
        read_fixture("lastfm_loved_page_1.html"),
        "https://www.last.fm/user/example/loved",
    )

    assert page == LovedTracksPage(
        tracks=[
            Track(
                artist="Guns N' Roses",
                title="Down on the Farm",
                lastfm_url="https://www.last.fm/music/Guns+N%27+Roses/_/Down+on+the+Farm",
            ),
            Track(
                artist="Nelly Furtado",
                title="Say It Right",
                lastfm_url="https://www.last.fm/music/Nelly+Furtado/_/Say+It+Right",
            ),
        ],
        next_url="https://www.last.fm/user/example/loved?page=2",
        total_tracks=3,
    )


def test_loved_tracks_parser_extracts_fixture_html_with_beautifulsoup() -> None:
    parser = LastFmLovedTracksParser()

    page = parser.parse(
        read_fixture("lastfm_loved_page_1.html"),
        "https://www.last.fm/user/example/loved",
    )

    assert [track.artist for track in page.tracks] == ["Guns N' Roses", "Nelly Furtado"]
    assert [track.title for track in page.tracks] == ["Down on the Farm", "Say It Right"]
    assert page.total_tracks == 3
    assert page.next_url == "https://www.last.fm/user/example/loved?page=2"


def test_parse_loved_tracks_page_handles_missing_next_page() -> None:
    page = parse_loved_tracks_page(
        read_fixture("lastfm_loved_page_2.html"),
        "https://www.last.fm/user/example/loved?page=2",
    )

    assert page.next_url is None
    assert page.tracks == [
        Track(
            artist="The Killers",
            title="Smile Like You Mean It",
            lastfm_url="https://www.last.fm/music/The+Killers/_/Smile+Like+You+Mean+It",
        )
    ]


def test_parse_loved_tracks_page_skips_incomplete_rows() -> None:
    page = parse_loved_tracks_page(
        """
        <table>
          <tr class="chartlist-row">
            <td class="chartlist-name"><a href="/music/A/_/B">B</a></td>
          </tr>
        </table>
        """,
        "https://www.last.fm/user/example/loved",
    )

    assert page.tracks == []


def test_scraper_fetches_paginated_loved_tracks() -> None:
    first_url = f"{LASTFM_BASE_URL}/user/example/loved"
    second_url = f"{LASTFM_BASE_URL}/user/example/loved?page=2"
    session = FakeSession(
        {
            first_url: FakeResponse(read_fixture("lastfm_loved_page_1.html"), first_url),
            second_url: FakeResponse(read_fixture("lastfm_loved_page_2.html"), second_url),
        }
    )

    tracks = LastFmLovedTracksScraper(session=session, page_delay_seconds=0).fetch_loved_tracks(
        "example"
    )

    assert [track.title for track in tracks] == [
        "Down on the Farm",
        "Say It Right",
        "Smile Like You Mean It",
    ]
    assert session.requested_urls == [first_url, second_url]


def test_fetcher_fetches_html_documents() -> None:
    first_url = f"{LASTFM_BASE_URL}/user/example/loved"
    html = read_fixture("lastfm_loved_page_1.html")
    session = FakeSession({first_url: FakeResponse(html, first_url)})

    fetched_page = LastFmLovedTracksFetcher(session=session).fetch_page(first_url)

    assert fetched_page == FetchedHtmlPage(url=first_url, html=html)
    assert session.requested_urls == [first_url]


def test_fetcher_retries_lastfm_temporary_unavailable_status() -> None:
    first_url = f"{LASTFM_BASE_URL}/user/example/loved"
    html = read_fixture("lastfm_loved_page_1.html")
    unavailable_html = "<html><title>Last.fm - Temporarily Unavailable</title></html>"
    session = SequencedSession(
        [
            FakeResponse(unavailable_html, first_url, status_code=600),
            FakeResponse(html, first_url),
        ]
    )
    fetcher = LastFmLovedTracksFetcher(
        session=session,
        retry_attempts=2,
        retry_delay_seconds=0,
    )

    fetched_page = fetcher.fetch_page(first_url)

    assert fetched_page == FetchedHtmlPage(url=first_url, html=html)
    assert session.requested_urls == [first_url, first_url]


def test_scraper_reports_fetch_progress() -> None:
    first_url = f"{LASTFM_BASE_URL}/user/example/loved"
    second_url = f"{LASTFM_BASE_URL}/user/example/loved?page=2"
    session = FakeSession(
        {
            first_url: FakeResponse(read_fixture("lastfm_loved_page_1.html"), first_url),
            second_url: FakeResponse(read_fixture("lastfm_loved_page_2.html"), second_url),
        }
    )
    progress_events: list[FetchProgress] = []

    LastFmLovedTracksScraper(session=session, page_delay_seconds=0).fetch_loved_tracks(
        "example",
        progress_callback=progress_events.append,
    )

    assert progress_events == [
        FetchProgress(0, "Found Last.fm user example"),
        FetchProgress(2, "Fetched 2/3 tracks", total_count=3),
        FetchProgress(3, "Fetched 3/3 tracks", total_count=3),
    ]


def test_scraper_respects_max_pages() -> None:
    first_url = f"{LASTFM_BASE_URL}/user/example/loved"
    session = FakeSession(
        {
            first_url: FakeResponse(read_fixture("lastfm_loved_page_1.html"), first_url),
        }
    )

    tracks = LastFmLovedTracksScraper(session=session, page_delay_seconds=0).fetch_loved_tracks(
        "example",
        max_pages=1,
    )

    assert [track.title for track in tracks] == ["Down on the Farm", "Say It Right"]
    assert session.requested_urls == [first_url]


def test_scraper_encodes_username_in_url() -> None:
    scraper = LastFmLovedTracksScraper()

    assert scraper.loved_tracks_url("user name/with slash") == (
        "https://www.last.fm/user/user%20name%2Fwith%20slash/loved"
    )


def test_scraper_rejects_invalid_inputs() -> None:
    scraper = LastFmLovedTracksScraper()

    with pytest.raises(ValueError, match="username"):
        scraper.fetch_loved_tracks("")

    with pytest.raises(ValueError, match="max_pages"):
        scraper.fetch_loved_tracks("example", max_pages=0)


def test_scraper_wraps_request_failures() -> None:
    first_url = f"{LASTFM_BASE_URL}/user/example/loved"
    session = FakeSession({first_url: FakeResponse("", first_url, status_code=500)})

    with pytest.raises(LastFmError, match="Could not fetch"):
        LastFmLovedTracksScraper(session=session, page_delay_seconds=0).fetch_loved_tracks(
            "example"
        )


def test_fetch_and_store_loved_tracks_persists_results(tmp_path: Path) -> None:
    first_url = f"{LASTFM_BASE_URL}/user/example/loved"
    session = FakeSession(
        {
            first_url: FakeResponse(read_fixture("lastfm_loved_page_2.html"), first_url),
        }
    )
    repository = JsonTrackRepository(data_dir=tmp_path)

    scraper = LastFmLovedTracksScraper(session=session, page_delay_seconds=0)

    tracks = scraper.fetch_and_store_loved_tracks("example", repository)

    assert tracks == repository.load_tracks("example")
    assert repository.load_tracks("example")[0].status == TrackStatus.FETCHED
