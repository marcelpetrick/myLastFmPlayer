from __future__ import annotations

import builtins
from pathlib import Path

import pytest
import requests
from bs4 import BeautifulSoup

from my_lastfm_player import lastfm as lastfm_module
from my_lastfm_player.lastfm import (
    LASTFM_API_URL,
    LASTFM_BASE_URL,
    FetchedHtmlPage,
    FetchProgress,
    LastFmError,
    LastFmLovedTracksApiClient,
    LastFmLovedTracksFetcher,
    LastFmLovedTracksParser,
    LastFmLovedTracksScraper,
    LovedTracksApiPage,
    LovedTracksPage,
    _controlled_sleep,
    _find_next_page_url,
    _find_total_tracks,
    _is_retryable_error,
    _parse_html_document,
    _parse_loved_at,
    _parse_loved_tracks_api_payload,
    _progress_message,
    parse_loved_tracks_page,
)
from my_lastfm_player.models import Track, TrackStatus
from my_lastfm_player.storage import JsonTrackRepository

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class FakeResponse:
    def __init__(
        self,
        text: str,
        url: str,
        status_code: int = 200,
        json_payload: object | None = None,
    ) -> None:
        self.text = text
        self.url = url
        self.status_code = status_code
        self.json_payload = json_payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} error")

    def json(self) -> object:
        if self.json_payload is None:
            raise ValueError("No JSON payload configured")
        return self.json_payload


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


class ApiFakeSession:
    def __init__(self, responses: dict[int, FakeResponse]) -> None:
        self.responses = responses
        self.requests: list[tuple[str, dict[str, object]]] = []

    def get(
        self,
        url: str,
        *,
        params: dict[str, object] | None = None,
        timeout: int,
    ) -> FakeResponse:
        del timeout
        request_params = params or {}
        self.requests.append((url, request_params))
        page = int(str(request_params.get("page", "1")))
        response = self.responses.get(page)
        if response is None:
            raise requests.ConnectionError(f"No fake response for page {page}")
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


def api_loved_payload(page: int, total_pages: int = 2, total: int = 3) -> dict[str, object]:
    tracks = {
        1: [
            {
                "name": "Down on the Farm",
                "artist": {"name": "Guns N' Roses"},
                "url": "https://www.last.fm/music/Guns+N%27+Roses/_/Down+on+the+Farm",
                "date": {"uts": "1682090040"},
            },
            {
                "name": "Say It Right",
                "artist": {"#text": "Nelly Furtado"},
                "url": "https://www.last.fm/music/Nelly+Furtado/_/Say+It+Right",
                "date": {"uts": "1667637000"},
            },
        ],
        2: [
            {
                "name": "Smile Like You Mean It",
                "artist": {"#text": "The Killers"},
                "url": "https://www.last.fm/music/The+Killers/_/Smile+Like+You+Mean+It",
                "date": {"uts": "1625957100"},
            }
        ],
    }
    return {
        "lovedtracks": {
            "@attr": {
                "page": str(page),
                "totalPages": str(total_pages),
                "total": str(total),
            },
            "track": tracks.get(page, []),
        }
    }


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
                loved_at="20230421-151400",
            ),
            Track(
                artist="Nelly Furtado",
                title="Say It Right",
                lastfm_url="https://www.last.fm/music/Nelly+Furtado/_/Say+It+Right",
                loved_at="20221105-083000",
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


def test_legacy_html_parser_reports_missing_beautifulsoup(monkeypatch) -> None:
    real_import = builtins.__import__

    def fake_import(name, globals_=None, locals_=None, fromlist=(), level=0):
        if name == "bs4":
            raise ImportError("blocked")
        return real_import(name, globals_, locals_, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    with pytest.raises(LastFmError, match="legacy Last.fm HTML parsing"):
        _parse_html_document("<html></html>")


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
            loved_at="20210710-224500",
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


def test_parse_loved_tracks_page_uses_fallback_table_rows_and_skips_blank_text() -> None:
    page = parse_loved_tracks_page(
        """
        <table>
          <tr>
            <td class="chartlist-name"><a href="/music/A/_/T">  Track   Name  </a></td>
            <td class="chartlist-artist"><a> Artist   Name </a></td>
          </tr>
          <tr>
            <td class="chartlist-name"><a href="/music/A/_/Blank">   </a></td>
            <td class="chartlist-artist"><a>Artist</a></td>
          </tr>
        </table>
        """,
        "https://www.last.fm/user/example/loved",
    )

    assert page.tracks == [
        Track(
            artist="Artist Name",
            title="Track Name",
            lastfm_url="https://www.last.fm/music/A/_/T",
        )
    ]


def test_parse_loved_tracks_page_handles_next_link_variants() -> None:
    page = parse_loved_tracks_page(
        """
        <html>
          <a class="pagination-next" href="/user/example/loved?page=2">Next</a>
          <span>loved tracks (1,234)</span>
        </html>
        """,
        "https://www.last.fm/user/example/loved",
    )

    assert page.next_url == "https://www.last.fm/user/example/loved?page=2"
    assert page.total_tracks == 1234


def test_find_next_page_url_ignores_disabled_or_invalid_links() -> None:
    page_url = "https://www.last.fm/user/example/loved"

    for html in (
        '<a rel="next" class="disabled" href="/next">Next</a>',
        '<a rel="next" aria-disabled="true" href="/next">Next</a>',
        '<a rel="next">Next</a>',
        '<span class="pagination-next"><a href="">Next</a></span>',
    ):
        assert _find_next_page_url(BeautifulSoup(html, "html.parser"), page_url) is None


def test_find_total_tracks_handles_data_attribute_and_invalid_count() -> None:
    assert (
        _find_total_tracks(
            BeautifulSoup('<div data-total-tracks="2,345"></div>', "html.parser")
        )
        == 2345
    )
    assert _find_total_tracks(BeautifulSoup("<div>no loved count</div>", "html.parser")) is None
    assert (
        _find_total_tracks(
            BeautifulSoup('<div data-total-tracks="many"></div>', "html.parser")
        )
        is None
    )


def test_api_client_fetches_loved_tracks_with_loved_at_metadata() -> None:
    session = ApiFakeSession(
        {1: FakeResponse("", LASTFM_API_URL, json_payload=api_loved_payload(1))}
    )

    page = LastFmLovedTracksApiClient(
        api_key="test-key",
        session=session,
        retry_delay_seconds=0,
    ).fetch_page("example", 1)

    assert page == LovedTracksApiPage(
        tracks=[
            Track(
                artist="Guns N' Roses",
                title="Down on the Farm",
                lastfm_url="https://www.last.fm/music/Guns+N%27+Roses/_/Down+on+the+Farm",
                loved_at="20230421-151400",
            ),
            Track(
                artist="Nelly Furtado",
                title="Say It Right",
                lastfm_url="https://www.last.fm/music/Nelly+Furtado/_/Say+It+Right",
                loved_at="20221105-083000",
            ),
        ],
        page=1,
        total_pages=2,
        total_tracks=3,
    )
    assert session.requests == [
        (
            LASTFM_API_URL,
            {
                "method": "user.getLovedTracks",
                "user": "example",
                "api_key": "test-key",
                "format": "json",
                "limit": 200,
                "page": 1,
            },
        )
    ]


def test_api_client_handles_single_track_and_missing_optional_metadata() -> None:
    session = ApiFakeSession(
        {
            1: FakeResponse(
                "",
                LASTFM_API_URL,
                json_payload={
                    "lovedtracks": {
                        "@attr": {"page": "1", "totalPages": "1", "total": "1"},
                        "track": {"name": "Single", "artist": "Artist"},
                    }
                },
            )
        }
    )

    page = LastFmLovedTracksApiClient(api_key="test-key", session=session).fetch_page("example", 1)

    assert page.tracks == [Track(artist="Artist", title="Single")]
    assert page.next_page is None


def test_api_client_raises_lastfm_error_for_api_error_payload() -> None:
    session = ApiFakeSession(
        {
            1: FakeResponse(
                "",
                LASTFM_API_URL,
                json_payload={"error": 6, "message": "User not found"},
            )
        }
    )

    with pytest.raises(LastFmError, match="User not found"):
        LastFmLovedTracksApiClient(api_key="test-key", session=session).fetch_page("missing", 1)


def test_api_client_rejects_missing_api_key_and_invalid_page(monkeypatch) -> None:
    monkeypatch.setattr(
        lastfm_module,
        "lastfm_api_credentials",
        lambda: type("Credentials", (), {"api_key": ""})(),
    )

    with pytest.raises(LastFmError, match="API key"):
        LastFmLovedTracksApiClient(api_key="").fetch_page("example", 1)

    with pytest.raises(ValueError, match="page"):
        LastFmLovedTracksApiClient(api_key="test-key").fetch_page("example", 0)


def test_parse_loved_tracks_api_payload_rejects_invalid_top_level_shapes() -> None:
    with pytest.raises(LastFmError, match="invalid response"):
        _parse_loved_tracks_api_payload([], 1)

    with pytest.raises(LastFmError, match="did not contain loved tracks"):
        _parse_loved_tracks_api_payload({"lovedtracks": []}, 1)


def test_parse_loved_tracks_api_payload_tolerates_bad_attrs_and_track_items() -> None:
    page = _parse_loved_tracks_api_payload(
        {
            "lovedtracks": {
                "@attr": "not a dict",
                "track": [
                    "bad item",
                    {"name": "", "artist": "Artist"},
                    {"name": "Title", "artist": 123},
                    {"name": "Valid", "artist": "Artist", "date": {"uts": "bad"}},
                    {"name": "No Date", "artist": "Artist", "date": {}},
                    {"name": "Missing Date", "artist": "Artist"},
                ],
            }
        },
        4,
    )

    assert page.page == 4
    assert page.total_pages is None
    assert page.total_tracks is None
    assert page.tracks == [
        Track(artist="Artist", title="Valid"),
        Track(artist="Artist", title="No Date"),
        Track(artist="Artist", title="Missing Date"),
    ]


def test_api_client_retries_request_exception_then_succeeds() -> None:
    class FlakyApiSession:
        def __init__(self) -> None:
            self.calls = 0

        def get(
            self,
            url: str,
            *,
            params: dict[str, object] | None = None,
            timeout: int,
        ) -> FakeResponse:
            del url, params, timeout
            self.calls += 1
            if self.calls == 1:
                raise requests.ConnectionError("temporary network failure")
            return FakeResponse("", LASTFM_API_URL, json_payload=api_loved_payload(1))

    session = FlakyApiSession()

    page = LastFmLovedTracksApiClient(
        api_key="test-key",
        session=session,
        retry_attempts=2,
        retry_delay_seconds=0,
    ).fetch_page("example", 1)

    assert page.total_tracks == 3
    assert session.calls == 2


def test_scraper_fetches_paginated_loved_tracks_through_api() -> None:
    session = ApiFakeSession(
        {
            1: FakeResponse("", LASTFM_API_URL, json_payload=api_loved_payload(1)),
            2: FakeResponse("", LASTFM_API_URL, json_payload=api_loved_payload(2)),
        }
    )

    tracks = LastFmLovedTracksScraper(
        api_key="test-key",
        session=session,
        page_delay_seconds=0,
    ).fetch_loved_tracks("example")

    assert [track.title for track in tracks] == [
        "Down on the Farm",
        "Say It Right",
        "Smile Like You Mean It",
    ]
    assert [request[1]["page"] for request in session.requests] == [1, 2]


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


def test_fetcher_retries_request_exception_then_succeeds() -> None:
    first_url = f"{LASTFM_BASE_URL}/user/example/loved"

    class FlakySession:
        def __init__(self) -> None:
            self.calls = 0

        def get(self, url: str, *, timeout: int) -> FakeResponse:
            self.calls += 1
            if self.calls == 1:
                raise requests.ConnectionError("temporary network failure")
            return FakeResponse(read_fixture("lastfm_loved_page_2.html"), url)

    session = FlakySession()
    fetcher = LastFmLovedTracksFetcher(
        session=session,
        retry_attempts=2,
        retry_delay_seconds=0,
    )

    fetched_page = fetcher.fetch_page(first_url)

    assert fetched_page.url == first_url
    assert session.calls == 2


def test_fetcher_treats_unavailable_title_as_retryable() -> None:
    first_url = f"{LASTFM_BASE_URL}/user/example/loved"
    html = read_fixture("lastfm_loved_page_2.html")
    unavailable_html = "<html><title>Last.fm - Temporarily Unavailable</title></html>"
    session = SequencedSession(
        [
            FakeResponse(unavailable_html, first_url),
            FakeResponse(html, first_url),
        ]
    )

    fetched_page = LastFmLovedTracksFetcher(
        session=session,
        retry_attempts=2,
        retry_delay_seconds=0,
    ).fetch_page(first_url)

    assert fetched_page.html == html
    assert session.requested_urls == [first_url, first_url]


def test_scraper_reports_fetch_progress() -> None:
    session = ApiFakeSession(
        {
            1: FakeResponse("", LASTFM_API_URL, json_payload=api_loved_payload(1)),
            2: FakeResponse("", LASTFM_API_URL, json_payload=api_loved_payload(2)),
        }
    )
    progress_events: list[FetchProgress] = []

    LastFmLovedTracksScraper(
        api_key="test-key",
        session=session,
        page_delay_seconds=0,
    ).fetch_loved_tracks(
        "example",
        progress_callback=progress_events.append,
    )

    assert progress_events == [
        FetchProgress(0, "Found Last.fm user example"),
        FetchProgress(2, "Fetched 2/3 tracks", total_count=3),
        FetchProgress(3, "Fetched 3/3 tracks", total_count=3),
    ]


def test_scraper_fetches_loved_track_count_from_first_page() -> None:
    session = ApiFakeSession(
        {1: FakeResponse("", LASTFM_API_URL, json_payload=api_loved_payload(1))}
    )

    count = LastFmLovedTracksScraper(
        api_key="test-key",
        session=session,
        page_delay_seconds=0,
    ).fetch_loved_track_count("example")

    assert count == 3
    assert [request[1]["page"] for request in session.requests] == [1]


def test_scraper_returns_none_when_loved_track_count_is_missing() -> None:
    session = ApiFakeSession(
        {
            1: FakeResponse(
                "",
                LASTFM_API_URL,
                json_payload={"lovedtracks": {"@attr": {"page": "1"}, "track": []}},
            ),
        }
    )

    count = LastFmLovedTracksScraper(
        api_key="test-key",
        session=session,
        page_delay_seconds=0,
    ).fetch_loved_track_count("example")

    assert count is None


def test_scraper_reports_progress_without_total_count() -> None:
    session = ApiFakeSession(
        {
            1: FakeResponse(
                "",
                LASTFM_API_URL,
                json_payload={
                    "lovedtracks": {
                        "@attr": {"page": "1", "totalPages": "1"},
                        "track": {"name": "Title", "artist": "Artist"},
                    }
                },
            ),
        }
    )
    progress_events: list[FetchProgress] = []

    tracks = LastFmLovedTracksScraper(
        api_key="test-key",
        session=session,
        page_delay_seconds=0,
    ).fetch_loved_tracks("example", progress_callback=progress_events.append)

    assert tracks == [Track(artist="Artist", title="Title")]
    assert progress_events[-1] == FetchProgress(1, "Fetched 1 tracks")
    assert _progress_message(3, None) == "Fetched 3 tracks"


def test_scraper_reports_cumulative_tracks_after_each_page() -> None:
    session = ApiFakeSession(
        {
            1: FakeResponse("", LASTFM_API_URL, json_payload=api_loved_payload(1)),
            2: FakeResponse("", LASTFM_API_URL, json_payload=api_loved_payload(2)),
        }
    )
    track_events: list[list[Track]] = []

    LastFmLovedTracksScraper(
        api_key="test-key",
        session=session,
        page_delay_seconds=0,
    ).fetch_loved_tracks(
        "example",
        tracks_callback=track_events.append,
    )

    assert [[track.title for track in tracks] for tracks in track_events] == [
        ["Down on the Farm", "Say It Right"],
        ["Down on the Farm", "Say It Right", "Smile Like You Mean It"],
    ]


def test_scraper_stops_paginated_fetch_when_control_callback_returns_false() -> None:
    session = ApiFakeSession(
        {
            1: FakeResponse("", LASTFM_API_URL, json_payload=api_loved_payload(1)),
            2: FakeResponse("", LASTFM_API_URL, json_payload=api_loved_payload(2)),
        }
    )
    control_calls = 0

    def control_callback() -> bool:
        nonlocal control_calls
        control_calls += 1
        return control_calls == 1

    tracks = LastFmLovedTracksScraper(
        api_key="test-key",
        session=session,
        page_delay_seconds=0,
    ).fetch_loved_tracks(
        "example",
        control_callback=control_callback,
    )

    assert [track.title for track in tracks] == ["Down on the Farm", "Say It Right"]
    assert [request[1]["page"] for request in session.requests] == [1]


def test_scraper_respects_max_pages() -> None:
    session = ApiFakeSession(
        {1: FakeResponse("", LASTFM_API_URL, json_payload=api_loved_payload(1))}
    )

    tracks = LastFmLovedTracksScraper(
        api_key="test-key",
        session=session,
        page_delay_seconds=0,
    ).fetch_loved_tracks(
        "example",
        max_pages=1,
    )

    assert [track.title for track in tracks] == ["Down on the Farm", "Say It Right"]
    assert [request[1]["page"] for request in session.requests] == [1]


def test_scraper_encodes_username_in_url() -> None:
    scraper = LastFmLovedTracksScraper()

    assert scraper.loved_tracks_url("user name/with slash") == (
        "https://www.last.fm/user/user%20name%2Fwith%20slash/loved"
    )


def test_fetcher_encodes_username_in_url() -> None:
    fetcher = LastFmLovedTracksFetcher(base_url="https://www.last.fm/")

    assert fetcher.loved_tracks_url("user name/with slash") == (
        "https://www.last.fm/user/user%20name%2Fwith%20slash/loved"
    )


def test_scraper_rejects_invalid_inputs() -> None:
    scraper = LastFmLovedTracksScraper()

    with pytest.raises(ValueError, match="username"):
        scraper.fetch_loved_tracks("")

    with pytest.raises(ValueError, match="max_pages"):
        scraper.fetch_loved_tracks("example", max_pages=0)


def test_scraper_wraps_request_failures() -> None:
    session = ApiFakeSession(
        {1: FakeResponse("", LASTFM_API_URL, status_code=500, json_payload={})}
    )

    with pytest.raises(LastFmError, match="Could not fetch"):
        LastFmLovedTracksScraper(
            api_key="test-key",
            session=session,
            page_delay_seconds=0,
        ).fetch_loved_tracks("example")


def test_fetch_and_store_loved_tracks_persists_results(tmp_path: Path) -> None:
    session = ApiFakeSession(
        {1: FakeResponse("", LASTFM_API_URL, json_payload=api_loved_payload(2, total_pages=1))}
    )
    repository = JsonTrackRepository(data_dir=tmp_path)

    scraper = LastFmLovedTracksScraper(
        api_key="test-key",
        session=session,
        page_delay_seconds=0,
    )

    tracks = scraper.fetch_and_store_loved_tracks("example", repository)

    assert tracks == repository.load_tracks("example")
    assert repository.load_tracks("example")[0].status == TrackStatus.FETCHED


def test_fetch_and_store_loved_tracks_merges_api_data_without_replacing_cache(
    tmp_path: Path,
) -> None:
    session = ApiFakeSession(
        {
            1: FakeResponse(
                "",
                LASTFM_API_URL,
                json_payload={
                    "lovedtracks": {
                        "@attr": {"page": "1", "totalPages": "1", "total": "0"},
                        "track": [],
                    }
                },
            )
        }
    )
    repository = JsonTrackRepository(data_dir=tmp_path)
    cached = Track(
        artist="Cached",
        title="Track",
        youtube_url="https://youtube.example/watch?v=cached",
        status=TrackStatus.QUEUED,
    )
    repository.save_tracks("example", [cached])

    tracks = LastFmLovedTracksScraper(
        api_key="test-key",
        session=session,
        page_delay_seconds=0,
    ).fetch_and_store_loved_tracks("example", repository)

    assert tracks == [cached]
    assert repository.load_tracks("example") == [cached]


def test_fetch_and_store_loved_tracks_preserves_cached_lookup_state(
    tmp_path: Path,
) -> None:
    session = ApiFakeSession(
        {1: FakeResponse("", LASTFM_API_URL, json_payload=api_loved_payload(2, total_pages=1))}
    )
    repository = JsonTrackRepository(data_dir=tmp_path)
    cached = Track(
        artist="The Killers",
        title="Smile Like You Mean It",
        youtube_url="https://youtube.example/watch?v=resolved",
        status=TrackStatus.QUEUED,
    )
    repository.save_tracks("example", [cached])

    tracks = LastFmLovedTracksScraper(
        api_key="test-key",
        session=session,
        page_delay_seconds=0,
    ).fetch_and_store_loved_tracks("example", repository)

    assert tracks[0].youtube_url == cached.youtube_url
    assert tracks[0].status is TrackStatus.QUEUED
    assert tracks[0].loved_at == "20210710-224500"


def test_controlled_sleep_stops_when_control_callback_returns_false(monkeypatch) -> None:
    monotonic_values = iter([0.0, 0.05, 0.05, 0.2])
    monkeypatch.setattr(
        "my_lastfm_player.lastfm.time.monotonic",
        lambda: next(monotonic_values, 0.2),
    )
    monkeypatch.setattr("my_lastfm_player.lastfm.time.sleep", lambda _seconds: None)
    calls = 0

    def control_callback() -> bool:
        nonlocal calls
        calls += 1
        return calls == 1

    assert not _controlled_sleep(0.1, control_callback)


def test_retryable_error_detection() -> None:
    assert _is_retryable_error(requests.ConnectionError("network"))
    assert _is_retryable_error(ValueError("bad json"))
    assert _is_retryable_error(LastFmError("Last.fm returned HTTP status 503"))
    assert not _is_retryable_error(LastFmError("Last.fm returned HTTP status 404"))


def test_scraper_rejects_empty_username_for_track_count_fetch() -> None:
    with pytest.raises(ValueError, match="username"):
        LastFmLovedTracksScraper().fetch_loved_track_count("")


def test_parse_loved_tracks_page_sets_lastfm_url_none_when_title_link_has_no_href() -> None:
    page = parse_loved_tracks_page(
        """
        <table>
          <tr class="chartlist-row">
            <td class="chartlist-name"><a>Title Without Href</a></td>
            <td class="chartlist-artist"><a href="/music/Artist">Artist</a></td>
          </tr>
        </table>
        """,
        "https://www.last.fm/user/example/loved",
    )

    assert page.tracks == [Track(artist="Artist", title="Title Without Href")]


def test_parse_loved_at_returns_none_when_title_attribute_is_empty() -> None:
    html = '<tr><td class="chartlist-timestamp"><span title="">text</span></td></tr>'
    row = BeautifulSoup(html, "html.parser").find("tr")
    assert _parse_loved_at(row) is None


def test_parse_loved_at_returns_none_when_title_has_no_space() -> None:
    html = '<tr><td class="chartlist-timestamp"><span title="NoSpaceHere">text</span></td></tr>'
    row = BeautifulSoup(html, "html.parser").find("tr")
    assert _parse_loved_at(row) is None


def test_parse_loved_at_returns_none_for_invalid_date_format() -> None:
    html = (
        '<tr><td class="chartlist-timestamp">'
        '<span title="Weekday bad date format">text</span></td></tr>'
    )
    row = BeautifulSoup(html, "html.parser").find("tr")
    assert _parse_loved_at(row) is None


def test_find_total_tracks_reads_explicit_data_attribute() -> None:
    soup = BeautifulSoup('<main data-total-tracks="1,234"></main>', "html.parser")

    assert _find_total_tracks(soup) == 1234


def test_controlled_sleep_returns_true_after_deadline_has_elapsed(monkeypatch) -> None:
    monotonic_values = [0.0, 2.0]
    monkeypatch.setattr(
        "my_lastfm_player.lastfm.time.monotonic",
        lambda: monotonic_values.pop(0) if monotonic_values else 2.0,
    )
    monkeypatch.setattr("my_lastfm_player.lastfm.time.sleep", lambda _: None)

    assert _controlled_sleep(1.0, lambda: True)


def test_scraper_sleeps_between_pages_when_page_delay_is_positive(monkeypatch) -> None:
    sleep_calls: list[float] = []
    monkeypatch.setattr(
        "my_lastfm_player.lastfm._controlled_sleep",
        lambda delay, _cb: (sleep_calls.append(delay), True)[1],
    )
    session = ApiFakeSession(
        {
            1: FakeResponse("", LASTFM_API_URL, json_payload=api_loved_payload(1)),
            2: FakeResponse("", LASTFM_API_URL, json_payload=api_loved_payload(2)),
        }
    )

    tracks = LastFmLovedTracksScraper(
        api_key="test-key",
        session=session,
        page_delay_seconds=1.5,
    ).fetch_loved_tracks("example")

    assert len(tracks) == 3
    assert sleep_calls == [1.5]


def test_scraper_stops_during_page_delay_when_controlled_sleep_returns_false(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "my_lastfm_player.lastfm._controlled_sleep",
        lambda _delay, _cb: False,
    )
    session = ApiFakeSession(
        {
            1: FakeResponse("", LASTFM_API_URL, json_payload=api_loved_payload(1)),
            2: FakeResponse("", LASTFM_API_URL, json_payload=api_loved_payload(2)),
        }
    )

    tracks = LastFmLovedTracksScraper(
        api_key="test-key",
        session=session,
        page_delay_seconds=1.5,
    ).fetch_loved_tracks("example")

    assert [track.title for track in tracks] == ["Down on the Farm", "Say It Right"]
    assert [request[1]["page"] for request in session.requests] == [1]
