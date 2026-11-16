"""Exact contract of the Last.fm clients, parsers and the paginating scraper."""

from __future__ import annotations

import pytest
import requests

from my_lastfm_player import lastfm
from my_lastfm_player.lastfm import (
    LASTFM_API_URL,
    LASTFM_HEADERS,
    REQUEST_TIMEOUT_SECONDS,
    ArtistImage,
    FetchProgress,
    LastFmArtistInfoClient,
    LastFmError,
    LastFmLovedTracksApiClient,
    LastFmLovedTracksScraper,
    LovedTracksApiPage,
    _ArtistImageExtractor,
    _controlled_sleep,
    _extract_css_background_image_url,
    _is_lastfm_placeholder_image_url,
    _is_retryable_error,
    _parse_api_loved_at,
    _parse_artist_image_payload,
    _parse_loved_tracks_api_payload,
    _parse_positive_int,
    _select_artist_image_url,
    _select_artist_page_image_url,
    _to_lastfm_error,
)
from my_lastfm_player.models import Track, TrackStatus
from my_lastfm_player.storage import JsonTrackRepository

PLACEHOLDER = "https://lastfm.freetls.fastly.net/i/u/300x300/2a96cbd8b46e442fc41c2b86b821562f.png"


class FakeResponse:
    def __init__(self, status_code=200, payload=None, text="", content=b"") -> None:
        self.status_code = status_code
        self._payload = payload
        self.text = text
        self.content = content

    def json(self):
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload

    def raise_for_status(self) -> None:
        return None


class FakeSession:
    def __init__(self, responses) -> None:
        self.responses = list(responses)
        self.calls: list[tuple] = []

    def get(self, url, *, params=None, timeout):
        self.calls.append((url, params, timeout))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


@pytest.fixture
def sleeps(monkeypatch) -> list[float]:
    calls: list[float] = []
    monkeypatch.setattr(lastfm.time, "sleep", calls.append)
    return calls


def _api_payload(tracks, page=1, total_pages=1, total="2"):
    return {
        "lovedtracks": {
            "track": tracks,
            "@attr": {"page": str(page), "totalPages": str(total_pages), "total": total},
        }
    }


def _api_track(name="Song", artist="Artist", uts="1700000000", url="https://www.last.fm/x"):
    return {"name": name, "artist": {"name": artist}, "date": {"uts": uts}, "url": url}


# --- API client ------------------------------------------------------------------------


def test_real_sessions_get_the_lastfm_headers() -> None:
    client = LastFmLovedTracksApiClient(api_key=" key ")
    artist_client = LastFmArtistInfoClient(api_key="key")

    assert client.api_key == "key"
    for header, value in LASTFM_HEADERS.items():
        assert client.session.headers[header] == value
        assert artist_client.session.headers[header] == value


def test_fetch_page_sends_exact_parameters() -> None:
    session = FakeSession([FakeResponse(payload=_api_payload([_api_track()]))])
    client = LastFmLovedTracksApiClient(api_key="key", session=session, page_limit=50)

    page = client.fetch_page("alice", 3)

    assert session.calls == [
        (
            LASTFM_API_URL,
            {
                "method": "user.getLovedTracks",
                "user": "alice",
                "api_key": "key",
                "format": "json",
                "limit": 50,
                "page": 3,
            },
            REQUEST_TIMEOUT_SECONDS,
        )
    ]
    assert page.tracks[0].title == "Song"


def test_fetch_page_rejects_missing_key_and_bad_page(monkeypatch) -> None:
    monkeypatch.setattr(
        lastfm, "lastfm_api_credentials", lambda: type("C", (), {"api_key": "  "})()
    )
    with pytest.raises(LastFmError, match="^Last.fm API key is not configured$"):
        LastFmLovedTracksApiClient(session=FakeSession([])).fetch_page("alice", 1)
    with pytest.raises(ValueError, match="^page must be positive$"):
        LastFmLovedTracksApiClient(api_key="k", session=FakeSession([])).fetch_page("alice", 0)


def test_fetch_page_retries_transient_errors_with_the_configured_delay(sleeps) -> None:
    session = FakeSession(
        [
            FakeResponse(503),
            requests.ConnectionError("reset"),
            FakeResponse(payload=_api_payload([])),
        ]
    )
    client = LastFmLovedTracksApiClient(
        api_key="k", session=session, retry_attempts=3, retry_delay_seconds=1.5
    )

    client.fetch_page("alice", 1)

    assert sleeps == [1.5, 1.5]
    assert len(session.calls) == 3


def test_fetch_page_does_not_retry_a_client_error(sleeps) -> None:
    session = FakeSession([FakeResponse(404)])
    client = LastFmLovedTracksApiClient(api_key="k", session=session, retry_attempts=5)

    with pytest.raises(
        LastFmError,
        match="^Could not fetch Last.fm loved tracks from the Web API: "
        "Last.fm returned HTTP status 404$",
    ):
        client.fetch_page("alice", 1)
    assert sleeps == []


def test_fetch_page_gives_up_after_the_last_attempt(sleeps) -> None:
    session = FakeSession([FakeResponse(503), FakeResponse(502)])
    client = LastFmLovedTracksApiClient(
        api_key="k", session=session, retry_attempts=2, retry_delay_seconds=0.5
    )

    with pytest.raises(LastFmError, match="HTTP status 502$"):
        client.fetch_page("alice", 1)
    assert sleeps == [0.5]


def test_zero_retry_attempts_still_tries_once(sleeps) -> None:
    session = FakeSession([FakeResponse(payload=_api_payload([]))])

    LastFmLovedTracksApiClient(api_key="k", session=session, retry_attempts=0).fetch_page("a", 1)

    assert len(session.calls) == 1


@pytest.mark.parametrize(
    ("error", "retryable"),
    [
        (requests.ConnectionError("x"), True),
        (ValueError("bad json"), True),
        (LastFmError("Last.fm returned HTTP status 600"), True),
        (LastFmError("Last.fm returned HTTP status 502"), True),
        (LastFmError("Last.fm returned HTTP status 503"), True),
        (LastFmError("Last.fm returned HTTP status 504"), True),
        (LastFmError("temporary unavailable page"), True),
        (LastFmError("Last.fm returned HTTP status 500"), False),
        (LastFmError("Last.fm returned HTTP status 404"), False),
    ],
)
def test_retryable_errors(error, retryable) -> None:
    assert _is_retryable_error(error) is retryable


def test_errors_are_wrapped_with_the_url() -> None:
    original = LastFmError("kept")

    assert _to_lastfm_error("https://u", original) is original
    assert str(_to_lastfm_error("https://u", ValueError("bad"))) == (
        "Could not fetch Last.fm loved tracks from https://u: bad"
    )


def test_next_page_stops_at_the_last_page() -> None:
    assert LovedTracksApiPage([], page=1, total_pages=3).next_page == 2
    assert LovedTracksApiPage([], page=3, total_pages=3).next_page is None
    assert LovedTracksApiPage([], page=1).next_page is None


# --- payload parsing ------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ([], "Last.fm API returned an invalid response"),
        ({"error": 6, "message": "User not found"}, "Last.fm API error: User not found"),
        ({"error": 8}, "Last.fm API error: unknown Last.fm API error"),
        ({"other": {}}, "Last.fm API response did not contain loved tracks"),
    ],
)
def test_invalid_loved_track_payloads(payload, message) -> None:
    with pytest.raises(LastFmError, match=f"^{message}$"):
        _parse_loved_tracks_api_payload(payload, 1)


def test_payload_parsing_reads_attributes_single_items_and_skips_invalid() -> None:
    page = _parse_loved_tracks_api_payload(
        {"lovedtracks": {"track": _api_track(), "@attr": {"total": "1,234", "totalPages": "7"}}},
        4,
    )

    assert [track.title for track in page.tracks] == ["Song"]
    assert (page.page, page.total_pages, page.total_tracks) == (4, 7, 1234)

    page = _parse_loved_tracks_api_payload(
        {
            "lovedtracks": {
                "track": [
                    _api_track(name="  Two   Words "),
                    _api_track(artist=""),
                    "junk",
                    {"name": "T", "artist": "Plain Artist", "url": 5},
                ],
                "@attr": "not a dict",
            }
        },
        2,
    )

    assert [(t.artist, t.title, t.lastfm_url) for t in page.tracks] == [
        ("Artist", "Two Words", "https://www.last.fm/x"),
        ("Plain Artist", "T", None),
    ]
    assert (page.page, page.total_pages, page.total_tracks) == (2, None, None)


def test_artist_text_falls_back_to_the_text_field() -> None:
    page = _parse_loved_tracks_api_payload(
        {"lovedtracks": {"track": [{"name": "S", "artist": {"#text": "Txt"}}]}}, 1
    )

    assert page.tracks[0].artist == "Txt"


def test_loved_at_parsing() -> None:
    assert _parse_api_loved_at({"uts": "0"}) == "19700101-000000"
    assert _parse_api_loved_at({"uts": "1700000000"}) == "20231114-221320"
    assert _parse_api_loved_at({"uts": ""}) is None
    assert _parse_api_loved_at({"uts": "x"}) is None
    assert _parse_api_loved_at({"uts": 5}) is None
    assert _parse_api_loved_at("1700000000") is None


def test_positive_int_parsing() -> None:
    assert _parse_positive_int("5") == 5
    assert _parse_positive_int("1") == 1
    assert _parse_positive_int("0") is None
    assert _parse_positive_int(None) is None
    assert _parse_positive_int("x") is None


# --- artist info -----------------------------------------------------------------------------


def _artist_payload(images=None, url="https://www.last.fm/music/Artist"):
    artist = {"url": url, "image": images or []}
    return {"artist": artist}


def test_artist_info_request_and_page_image_preference() -> None:
    page_html = '<meta property="og:image" content="/img/og.jpg">'
    session = FakeSession(
        [
            FakeResponse(
                payload=_artist_payload([{"#text": "https://api/img.png", "size": "large"}])
            ),
            FakeResponse(text=page_html),
            FakeResponse(content=b"bytes"),
        ]
    )
    client = LastFmArtistInfoClient(api_key="key", session=session)

    image = client.fetch_artist_image("  Artist  ")

    assert image == ArtistImage(
        artist="Artist",
        page_url="https://www.last.fm/music/Artist",
        image_url="https://www.last.fm/img/og.jpg",
        image_bytes=b"bytes",
    )
    assert session.calls == [
        (
            LASTFM_API_URL,
            {"method": "artist.getInfo", "artist": "Artist", "api_key": "key", "format": "json"},
            REQUEST_TIMEOUT_SECONDS,
        ),
        ("https://www.last.fm/music/Artist", None, REQUEST_TIMEOUT_SECONDS),
        ("https://www.last.fm/img/og.jpg", None, REQUEST_TIMEOUT_SECONDS),
    ]


def test_artist_image_falls_back_to_api_image_and_text_bytes() -> None:
    session = FakeSession(
        [
            FakeResponse(
                payload=_artist_payload([{"#text": "https://api/img.png", "size": "mega"}])
            ),
            FakeResponse(404),
            FakeResponse(text="ab"),
        ]
    )

    image = LastFmArtistInfoClient(api_key="k", session=session).fetch_artist_image("Artist")

    assert (image.image_url, image.image_bytes) == ("https://api/img.png", b"ab")


def test_placeholder_api_image_means_no_image() -> None:
    session = FakeSession(
        [
            FakeResponse(payload=_artist_payload([{"#text": PLACEHOLDER, "size": "large"}])),
            FakeResponse(text=""),
        ]
    )

    image = LastFmArtistInfoClient(api_key="k", session=session).fetch_artist_image("Artist")

    assert image == ArtistImage(artist="Artist", page_url="https://www.last.fm/music/Artist")
    assert len(session.calls) == 2


def test_failed_image_download_keeps_the_url_without_bytes() -> None:
    session = FakeSession(
        [
            FakeResponse(
                payload=_artist_payload([{"#text": "https://api/i.png", "size": "small"}])
            ),
            requests.ConnectionError("page down"),
            requests.ConnectionError("image down"),
        ]
    )

    image = LastFmArtistInfoClient(api_key="k", session=session).fetch_artist_image("Artist")

    assert (image.image_url, image.image_bytes) == ("https://api/i.png", None)


def test_empty_image_response_has_no_bytes() -> None:
    session = FakeSession([FakeResponse(content=b"", text="")])

    assert LastFmArtistInfoClient(api_key="k", session=session)._fetch_image_bytes("u") is None


def test_artist_info_input_validation(monkeypatch) -> None:
    with pytest.raises(ValueError, match="^Last.fm artist must not be empty$"):
        LastFmArtistInfoClient(api_key="k", session=FakeSession([])).fetch_artist_image("  ")
    monkeypatch.setattr(lastfm, "lastfm_api_credentials", lambda: type("C", (), {"api_key": ""})())
    with pytest.raises(LastFmError, match="^Last.fm API key is not configured$"):
        LastFmArtistInfoClient(session=FakeSession([])).fetch_artist_image("A")


def test_artist_info_retries_then_reports_the_status(sleeps) -> None:
    session = FakeSession([FakeResponse(503), FakeResponse(500)])
    client = LastFmArtistInfoClient(
        api_key="k", session=session, retry_attempts=4, retry_delay_seconds=0.25
    )

    with pytest.raises(
        LastFmError,
        match=f"^Could not fetch Last.fm artist information from {LASTFM_API_URL}: "
        "Last.fm returned HTTP status 500$",
    ):
        client.fetch_artist_image("A")
    assert sleeps == [0.25]


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ([], "Last.fm API returned an invalid artist response"),
        ({"error": 6, "message": "nope"}, "Last.fm API error: nope"),
        ({"error": 6}, "Last.fm API error: unknown Last.fm API error"),
        ({"artist": "x"}, "Last.fm API response did not contain artist information"),
    ],
)
def test_invalid_artist_payloads(payload, message) -> None:
    with pytest.raises(LastFmError, match=f"^{message}$"):
        _parse_artist_image_payload(payload, "A")


def test_artist_page_url_falls_back_to_a_quoted_music_url() -> None:
    image = _parse_artist_image_payload({"artist": {"url": ""}}, " AC/DC ")

    assert image.page_url == "https://www.last.fm/music/AC%2FDC"
    assert image.artist == "AC/DC"


def test_artist_image_size_ranking() -> None:
    images = [
        {"#text": "s", "size": "small"},
        {"#text": "xl", "size": "ExtraLarge"},
        {"#text": "", "size": "mega"},
        {"#text": "m", "size": "medium"},
        "junk",
    ]

    assert _select_artist_image_url(images) == "xl"
    assert _select_artist_image_url([{"#text": "odd", "size": "huge"}]) == "odd"
    assert _select_artist_image_url([{"#text": "n", "size": None}]) is None
    assert _select_artist_image_url("x") is None


def test_page_image_extractor_priority_and_first_value_wins() -> None:
    html = (
        '<div class="header-new-background-image" style="background-image: url(\'/bg.jpg\')">'
        '<meta name="Twitter:Image" content="/tw.jpg">'
        '<meta property="OG:image" content="/og1.jpg">'
        '<meta property="og:image" content="/og2.jpg">'
        '<meta name="twitter:image" content="/tw2.jpg">'
    )
    extractor = _ArtistImageExtractor()
    extractor.feed(html)

    assert extractor.image_candidates() == ("/og1.jpg", "/tw.jpg", "/bg.jpg")


def test_page_image_selection_skips_placeholders_and_resolves_relative_urls() -> None:
    html = (
        f'<meta property="og:image" content="{PLACEHOLDER}">'
        '<meta name="twitter:image" content="t.jpg">'
    )

    assert _select_artist_page_image_url(html, "https://www.last.fm/music/A") == (
        "https://www.last.fm/music/t.jpg"
    )
    assert _select_artist_page_image_url("<p>none</p>", "https://x") is None


def test_css_background_url_extraction() -> None:
    assert _extract_css_background_image_url('background-image: url("/a.jpg")') == "/a.jpg"
    assert _extract_css_background_image_url("background-image:url(/b.jpg)") == "/b.jpg"
    assert _extract_css_background_image_url("color: red") is None


def test_placeholder_detection_is_case_insensitive() -> None:
    assert _is_lastfm_placeholder_image_url(PLACEHOLDER.upper())
    assert not _is_lastfm_placeholder_image_url("https://x/y.png")
    assert not _is_lastfm_placeholder_image_url(None)


# --- scraper ----------------------------------------------------------------------------------


class PagedApi:
    def __init__(self, pages) -> None:
        self.pages = pages
        self.requests: list[tuple[str, int]] = []

    def fetch_page(self, username, page):
        self.requests.append((username, page))
        return self.pages[page - 1]


def _page(n, titles, total_pages, total=None):
    return LovedTracksApiPage(
        [Track("A", title) for title in titles], page=n, total_pages=total_pages, total_tracks=total
    )


def test_scraper_reports_exact_progress_and_cumulative_tracks() -> None:
    api = PagedApi([_page(1, ["1", "2"], 2, total=3), _page(2, ["3"], 2)])
    progress: list[FetchProgress] = []
    snapshots: list[list[str]] = []

    tracks = LastFmLovedTracksScraper(api_client=api, page_delay_seconds=0).fetch_loved_tracks(
        "alice",
        progress_callback=progress.append,
        tracks_callback=lambda ts: snapshots.append([t.title for t in ts]),
    )

    assert [t.title for t in tracks] == ["1", "2", "3"]
    assert api.requests == [("alice", 1), ("alice", 2)]
    assert progress == [
        FetchProgress(0, "Found Last.fm user alice"),
        FetchProgress(2, "Fetched 2/3 tracks", 3),
        FetchProgress(3, "Fetched 3/3 tracks", 3),
    ]
    assert snapshots == [["1", "2"], ["1", "2", "3"]]


def test_scraper_without_total_reports_plain_counts_and_respects_max_pages() -> None:
    api = PagedApi([_page(1, ["1"], 3), _page(2, ["2"], 3), _page(3, ["3"], 3)])
    progress: list[FetchProgress] = []

    tracks = LastFmLovedTracksScraper(api_client=api, page_delay_seconds=0).fetch_loved_tracks(
        "alice", max_pages=2, progress_callback=progress.append
    )

    assert [t.title for t in tracks] == ["1", "2"]
    assert [p.message for p in progress] == [
        "Found Last.fm user alice",
        "Fetched 1 tracks",
        "Fetched 2 tracks",
    ]


def test_scraper_stops_when_the_control_callback_says_so() -> None:
    api = PagedApi([_page(1, ["1"], 2), _page(2, ["2"], 2)])
    answers = iter([True, False])

    tracks = LastFmLovedTracksScraper(api_client=api, page_delay_seconds=0).fetch_loved_tracks(
        "alice", control_callback=lambda: next(answers)
    )

    assert [t.title for t in tracks] == ["1"]


def test_scraper_waits_between_pages_and_can_stop_during_the_wait(monkeypatch) -> None:
    delays: list[float] = []
    monkeypatch.setattr(
        lastfm, "_controlled_sleep", lambda delay, _control: delays.append(delay) or False
    )
    api = PagedApi([_page(1, ["1"], 2), _page(2, ["2"], 2)])

    tracks = LastFmLovedTracksScraper(api_client=api, page_delay_seconds=0.7).fetch_loved_tracks(
        "alice"
    )

    assert delays == [0.7]
    assert [t.title for t in tracks] == ["1"]


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"username": ""}, "Last.fm username must not be empty"),
        ({"username": "a", "max_pages": 0}, "max_pages must be positive when provided"),
    ],
)
def test_scraper_argument_validation(kwargs, message) -> None:
    with pytest.raises(ValueError, match=f"^{message}$"):
        LastFmLovedTracksScraper(api_client=PagedApi([])).fetch_loved_tracks(**kwargs)


def test_fetch_and_store_forwards_options_and_restores_cached_state(tmp_path) -> None:
    repository = JsonTrackRepository(data_dir=tmp_path)
    repository.save_lookup_cache([Track("A", "1", youtube_url="https://y")])
    scraper = LastFmLovedTracksScraper(api_client=PagedApi([]), page_delay_seconds=0)
    received: dict = {}

    def fake_fetch(username, **kwargs):
        received.update(kwargs, username=username)
        return [Track("A", "1")]

    scraper.fetch_loved_tracks = fake_fetch  # type: ignore[method-assign]

    def progress(_p):
        return None

    def tracks_cb(_t):
        return None

    def control():
        return True

    merged = scraper.fetch_and_store_loved_tracks(
        "alice",
        repository,
        max_pages=4,
        progress_callback=progress,
        tracks_callback=tracks_cb,
        control_callback=control,
    )

    assert received == {
        "username": "alice",
        "max_pages": 4,
        "progress_callback": progress,
        "tracks_callback": tracks_cb,
        "control_callback": control,
    }
    assert (merged[0].youtube_url, merged[0].status) == ("https://y", TrackStatus.QUEUED)


def test_loved_track_count_and_url() -> None:
    api = PagedApi([_page(1, [], 1, total=42)])
    scraper = LastFmLovedTracksScraper(api_client=api, base_url="https://www.last.fm/")

    assert scraper.fetch_loved_track_count("bob") == 42
    assert api.requests == [("bob", 1)]
    assert scraper.loved_tracks_url("a b/c") == "https://www.last.fm/user/a%20b%2Fc/loved"
    assert (
        LastFmLovedTracksScraper(api_client=PagedApi([_page(1, [], 1)])).fetch_loved_track_count(
            "bob"
        )
        is None
    )
    with pytest.raises(ValueError, match="^Last.fm username must not be empty$"):
        scraper.fetch_loved_track_count("")


def test_controlled_sleep_checks_the_callback_until_the_deadline(monkeypatch) -> None:
    # deadline, loop check, sleep length, loop check, sleep length, final loop check
    clock = iter([0.0, 0.0, 0.0, 0.1, 0.15, 0.25])
    monkeypatch.setattr(lastfm.time, "monotonic", lambda: next(clock))
    slept: list[float] = []
    monkeypatch.setattr(lastfm.time, "sleep", slept.append)

    assert _controlled_sleep(0.2, lambda: True) is True
    assert slept == [pytest.approx(0.1), pytest.approx(0.05)]


def test_controlled_sleep_stops_early_and_honours_a_final_veto(monkeypatch) -> None:
    monkeypatch.setattr(lastfm.time, "sleep", lambda _s: None)

    assert _controlled_sleep(5.0, lambda: False) is False
    assert _controlled_sleep(0.0, lambda: False) is False
    assert _controlled_sleep(0.0, None) is True
