"""Edge cases of the Last.fm clients, parsers, page-image extraction and pagination."""

from __future__ import annotations

import itertools
from types import SimpleNamespace

import pytest
import requests

from my_lastfm_player import lastfm
from my_lastfm_player.lastfm import (
    LastFmArtistInfoClient,
    LastFmError,
    LastFmLovedTracksApiClient,
    LastFmLovedTracksScraper,
    LovedTracksApiPage,
    _controlled_sleep,
    _parse_loved_tracks_api_payload,
    _raise_for_unsuccessful_artist_response,
    _select_artist_image_url,
    _select_artist_page_image_url,
)
from my_lastfm_player.models import Track

PAGE_URL = "https://www.last.fm/music/Artist"


class FakeResponse:
    def __init__(self, status_code=200, payload=None, **attributes) -> None:
        self.status_code = status_code
        self._payload = payload
        for name, value in attributes.items():
            setattr(self, name, value)

    def json(self):
        return self._payload

    def raise_for_status(self) -> None:
        return None


class FakeSession:
    def __init__(self, responses) -> None:
        self.responses = list(responses)
        self.calls = 0

    def get(self, url, *, params=None, timeout):
        self.calls += 1
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


class FakeApiClient:
    def __init__(self, pages: list[LovedTracksApiPage]) -> None:
        self.pages = pages

    def fetch_page(self, username: str, page: int) -> LovedTracksApiPage:
        return self.pages[page - 1]


class CountingControl:
    def __init__(self) -> None:
        self.calls = 0

    def __call__(self) -> bool:
        self.calls += 1
        return True


@pytest.fixture
def sleeps(monkeypatch) -> list[float]:
    calls: list[float] = []
    monkeypatch.setattr(
        lastfm, "time", SimpleNamespace(sleep=calls.append, monotonic=lastfm.time.monotonic)
    )
    return calls


def _fake_clock(monkeypatch, readings) -> None:
    clock = iter(readings)
    monkeypatch.setattr(
        lastfm, "time", SimpleNamespace(monotonic=lambda: next(clock), sleep=lambda _s: None)
    )


# --- pacing ---------------------------------------------------------------------------


def test_controlled_sleep_ends_when_the_deadline_is_reached_exactly(monkeypatch) -> None:
    _fake_clock(monkeypatch, itertools.chain([100.0, 100.0], itertools.count(200.0)))
    control = CountingControl()

    assert _controlled_sleep(0.0, control) is True
    assert control.calls == 1


def _two_pages(total: int | None = None) -> FakeApiClient:
    return FakeApiClient(
        [
            LovedTracksApiPage([Track("A", "One")], page=1, total_pages=2, total_tracks=total),
            LovedTracksApiPage([Track("A", "Two")], page=2, total_pages=2, total_tracks=total),
        ]
    )


def test_zero_page_delay_never_enters_the_pacing_sleep() -> None:
    scraper = LastFmLovedTracksScraper(api_client=_two_pages(), page_delay_seconds=0)  # type: ignore[arg-type]
    control = CountingControl()

    tracks = scraper.fetch_loved_tracks("alice", control_callback=control)

    assert [track.title for track in tracks] == ["One", "Two"]
    assert control.calls == 2


def test_page_delay_consults_the_control_callback(monkeypatch) -> None:
    _fake_clock(monkeypatch, itertools.count(0.0, 0.25))
    scraper = LastFmLovedTracksScraper(api_client=_two_pages(), page_delay_seconds=1.0)  # type: ignore[arg-type]
    control = CountingControl()

    scraper.fetch_loved_tracks("alice", control_callback=control)

    assert control.calls > 2


@pytest.mark.parametrize("total", [None, 2])
def test_progress_messages_use_the_scraper_catalog_context(qapp, total) -> None:
    scraper = LastFmLovedTracksScraper(
        api_client=_two_pages(total),  # type: ignore[arg-type]
        page_delay_seconds=0,
    )
    messages: list[str] = []

    scraper.fetch_loved_tracks(
        "alice", progress_callback=lambda progress: messages.append(progress.message)
    )

    suffix = "" if total is None else "/2"
    assert messages == [
        "Found Last.fm user alice",
        f"Fetched 1{suffix} tracks",
        f"Fetched 2{suffix} tracks",
    ]


# --- scraper construction ------------------------------------------------------------


def test_scraper_strips_only_trailing_slashes() -> None:
    scraper = LastFmLovedTracksScraper(
        api_client=_two_pages(),  # type: ignore[arg-type]
        base_url="https://example.org/X/",
    )

    assert scraper.loved_tracks_url("bob") == "https://example.org/X/user/bob/loved"


def test_scraper_hands_its_api_key_to_the_default_client() -> None:
    scraper = LastFmLovedTracksScraper(session=FakeSession([]), api_key="custom-key")

    assert scraper.api_client.api_key == "custom-key"


# --- payload parsing -----------------------------------------------------------------


def test_payload_page_attribute_overrides_the_requested_page() -> None:
    payload = {
        "lovedtracks": {
            "@attr": {"page": "3", "totalPages": "4"},
            "track": [{"artist": {"name": "Artist"}, "url": "https://www.last.fm/x"}],
        }
    }

    page = _parse_loved_tracks_api_payload(payload, 1)

    assert page.page == 3
    assert page.tracks == []  # an item without a name is skipped


@pytest.mark.parametrize(
    ("images", "expected"),
    [
        ([{"size": "small", "#text": "s"}, {"size": "mega", "#text": "m"}], "m"),
        ([{"size": "small", "#text": "s"}, {"size": "large", "#text": "l"}], "l"),
        ([{"size": "small", "#text": "s"}, {"size": "medium", "#text": "md"}], "md"),
        ([{"size": "", "#text": "x"}, {"size": "small", "#text": "s"}], "s"),
    ],
)
def test_ranked_image_sizes_beat_the_listing_order(images, expected) -> None:
    assert _select_artist_image_url(images) == expected


# --- HTTP status handling --------------------------------------------------------------


def test_status_400_is_already_an_error() -> None:
    with pytest.raises(LastFmError, match="HTTP status 400"):
        _raise_for_unsuccessful_artist_response(FakeResponse(400), PAGE_URL)  # type: ignore[arg-type]

    client = LastFmLovedTracksApiClient(api_key="key", session=FakeSession([]))
    with pytest.raises(LastFmError, match="HTTP status 400"):
        client._raise_for_unsuccessful_response(FakeResponse(400))  # type: ignore[arg-type]


# --- retries ---------------------------------------------------------------------------


def _ok_artist_payload() -> FakeResponse:
    return FakeResponse(payload={"artist": {"url": PAGE_URL}})


def test_a_single_attempt_is_not_retried(sleeps) -> None:
    artist_session = FakeSession([requests.ConnectionError("down"), _ok_artist_payload()])
    artist_client = LastFmArtistInfoClient(
        api_key="key", session=artist_session, retry_attempts=1, retry_delay_seconds=0.5
    )
    with pytest.raises(LastFmError):
        artist_client._fetch_artist_info_payload("Artist")

    api_session = FakeSession([requests.ConnectionError("down"), FakeResponse(payload={})])
    api_client = LastFmLovedTracksApiClient(
        api_key="key", session=api_session, retry_attempts=1, retry_delay_seconds=0.5
    )
    with pytest.raises(LastFmError):
        api_client.fetch_page("alice", 1)

    assert artist_session.calls == 1
    assert api_session.calls == 1
    assert sleeps == []


def test_the_last_artist_attempt_raises_without_sleeping(sleeps) -> None:
    final_error = requests.ConnectionError("still down")
    session = FakeSession([requests.ConnectionError("down"), final_error])
    client = LastFmArtistInfoClient(
        api_key="key", session=session, retry_attempts=2, retry_delay_seconds=0.5
    )

    with pytest.raises(LastFmError) as raised:
        client._fetch_artist_info_payload("Artist")

    assert raised.value.__cause__ is final_error
    assert sleeps == [0.5]


# --- artist page and image downloads ---------------------------------------------------


def test_non_text_page_bodies_have_no_image() -> None:
    client = LastFmArtistInfoClient(
        api_key="key",
        session=FakeSession([FakeResponse(text=b'<meta property="og:image" content="/a.jpg">')]),
    )

    assert client._fetch_artist_page_image_url(PAGE_URL) is None


def test_page_responses_without_a_text_attribute_have_no_image() -> None:
    client = LastFmArtistInfoClient(api_key="key", session=FakeSession([FakeResponse()]))

    assert client._fetch_artist_page_image_url(PAGE_URL) is None


def test_image_bytes_fall_back_to_text_and_tolerate_missing_attributes() -> None:
    client = LastFmArtistInfoClient(
        api_key="key", session=FakeSession([FakeResponse(text="raw"), FakeResponse()])
    )

    assert client._fetch_image_bytes("https://img/1.jpg") == b"raw"
    assert client._fetch_image_bytes("https://img/2.jpg") is None


# --- page image extraction -------------------------------------------------------------


@pytest.mark.parametrize(
    ("html", "expected"),
    [
        (
            '<meta property="og:image" content><meta name="twitter:image" content="/tw.jpg">',
            "https://www.last.fm/tw.jpg",
        ),
        ('<meta property="og:image"><meta property="og:image" content="/second.jpg">', None),
        ('<meta name="twitter:image"><meta name="twitter:image" content="/second.jpg">', None),
        ('<div style="background-image: url(/bg.jpg)"></div>', None),
    ],
)
def test_page_image_extraction_edge_cases(html, expected) -> None:
    assert _select_artist_page_image_url(html, PAGE_URL) == expected
