from __future__ import annotations

from pathlib import Path

import pytest
import requests

from my_lastfm_player import lastfm as lastfm_module
from my_lastfm_player.lastfm import (
    LASTFM_API_URL,
    ArtistImage,
    FetchProgress,
    LastFmArtistInfoClient,
    LastFmError,
    LastFmLovedTracksApiClient,
    LastFmLovedTracksScraper,
    LovedTracksApiPage,
    _controlled_sleep,
    _is_lastfm_placeholder_image_url,
    _is_retryable_error,
    _parse_artist_image_payload,
    _parse_loved_tracks_api_payload,
    _progress_message,
    _raise_for_unsuccessful_artist_response,
    _select_artist_image_url,
    _select_artist_page_image_url,
)
from my_lastfm_player.models import Track, TrackStatus
from my_lastfm_player.storage import JsonTrackRepository


class FakeResponse:
    def __init__(
        self,
        text: str,
        url: str,
        status_code: int = 200,
        json_payload: object | None = None,
        content: bytes | None = None,
    ) -> None:
        self.text = text
        self.url = url
        self.status_code = status_code
        self.json_payload = json_payload
        self.content = content if content is not None else text.encode("utf-8")

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} error")

    def json(self) -> object:
        if self.json_payload is None:
            raise ValueError("No JSON payload configured")
        return self.json_payload


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


class ArtistInfoSession:
    def __init__(self, responses: dict[str, FakeResponse]) -> None:
        self.responses = responses
        self.requests: list[tuple[str, dict[str, object] | None]] = []

    def get(
        self,
        url: str,
        *,
        params: dict[str, object] | None = None,
        timeout: int,
    ) -> FakeResponse:
        del timeout
        self.requests.append((url, params))
        response = self.responses.get(url)
        if response is None:
            raise requests.ConnectionError(f"No fake response for {url}")
        return response


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


def test_artist_info_client_fetches_artist_page_and_page_metadata_image() -> None:
    api_image_url = "https://last.fm/api-image.jpg"
    page_image_url = "https://last.fm/page-image.jpg"
    page_url = "https://www.last.fm/music/API+Artist"
    session = ArtistInfoSession(
        {
            LASTFM_API_URL: FakeResponse(
                "",
                LASTFM_API_URL,
                json_payload={
                    "artist": {
                        "name": "API Artist",
                        "url": page_url,
                        "image": [
                            {"#text": "https://last.fm/small.jpg", "size": "small"},
                            {"#text": api_image_url, "size": "extralarge"},
                        ],
                    }
                },
            ),
            page_url: FakeResponse(
                f'<meta property="og:image" content="{page_image_url}">',
                page_url,
            ),
            page_image_url: FakeResponse("", page_image_url, content=b"image-bytes"),
        }
    )

    artist_image = LastFmArtistInfoClient(
        api_key="test-key",
        session=session,
        retry_delay_seconds=0,
    ).fetch_artist_image("Requested Artist")

    assert artist_image == ArtistImage(
        artist="Requested Artist",
        page_url=page_url,
        image_url=page_image_url,
        image_bytes=b"image-bytes",
    )
    assert session.requests[0][1]["method"] == "artist.getInfo"
    assert session.requests[0][1]["artist"] == "Requested Artist"
    assert session.requests[1] == (page_url, None)
    assert session.requests[2] == (page_image_url, None)


def test_artist_info_client_handles_missing_image_and_fallback_url() -> None:
    page_url = "https://www.last.fm/music/Artist%20Name"
    session = ArtistInfoSession(
        {
            LASTFM_API_URL: FakeResponse(
                "",
                LASTFM_API_URL,
                json_payload={"artist": {"name": "Artist", "image": []}},
            ),
            page_url: FakeResponse("", page_url),
        }
    )

    artist_image = LastFmArtistInfoClient(api_key="test-key", session=session).fetch_artist_image(
        "Artist Name"
    )

    assert artist_image == ArtistImage(
        artist="Artist Name",
        page_url=page_url,
    )


def test_artist_info_client_rejects_errors_and_missing_api_key(monkeypatch) -> None:
    monkeypatch.setattr(
        lastfm_module,
        "lastfm_api_credentials",
        lambda: type("Credentials", (), {"api_key": ""})(),
    )

    with pytest.raises(LastFmError, match="API key"):
        LastFmArtistInfoClient(api_key="").fetch_artist_image("Artist")

    session = ArtistInfoSession(
        {
            LASTFM_API_URL: FakeResponse(
                "",
                LASTFM_API_URL,
                json_payload={"error": 6, "message": "Artist not found"},
            )
        }
    )
    with pytest.raises(LastFmError, match="Artist not found"):
        LastFmArtistInfoClient(api_key="test-key", session=session).fetch_artist_image("Missing")


def test_artist_info_client_rejects_empty_artist() -> None:
    with pytest.raises(ValueError, match="artist"):
        LastFmArtistInfoClient(api_key="test-key").fetch_artist_image(" ")


def test_artist_info_client_retries_artist_info_and_handles_image_errors() -> None:
    image_url = "https://last.fm/image.jpg"
    page_url = "https://www.last.fm/music/Artist"

    class FlakyArtistSession:
        def __init__(self) -> None:
            self.calls = 0

        def get(
            self,
            url: str,
            *,
            params: dict[str, object] | None = None,
            timeout: int,
        ) -> FakeResponse:
            del timeout
            if params is not None:
                self.calls += 1
                if self.calls == 1:
                    raise requests.ConnectionError("temporary network failure")
                return FakeResponse(
                    "",
                    url,
                    json_payload={
                        "artist": {
                            "url": page_url,
                            "image": [{"#text": image_url, "size": "large"}],
                        }
                    },
                )
            if url == page_url:
                raise requests.ConnectionError("temporary page failure")
            return FakeResponse("", url, status_code=404)

    artist_image = LastFmArtistInfoClient(
        api_key="test-key",
        session=FlakyArtistSession(),
        retry_attempts=2,
        retry_delay_seconds=0,
    ).fetch_artist_image("Artist")

    assert artist_image == ArtistImage(
        artist="Artist",
        page_url=page_url,
        image_url=image_url,
    )


def test_artist_info_client_uses_text_body_when_image_content_is_empty() -> None:
    image_url = "https://last.fm/image.svg"
    page_url = "https://www.last.fm/music/Artist"
    session = ArtistInfoSession(
        {
            LASTFM_API_URL: FakeResponse(
                "",
                LASTFM_API_URL,
                json_payload={
                    "artist": {
                        "url": page_url,
                        "image": [{"#text": image_url, "size": "large"}],
                    }
                },
            ),
            page_url: FakeResponse("", page_url),
            image_url: FakeResponse("<svg />", image_url, content=b""),
        }
    )

    artist_image = LastFmArtistInfoClient(api_key="test-key", session=session).fetch_artist_image(
        "Artist"
    )

    assert artist_image.image_bytes == b"<svg />"


def test_artist_image_payload_parser_handles_invalid_shapes_and_sizes() -> None:
    with pytest.raises(LastFmError, match="invalid artist response"):
        _parse_artist_image_payload([], "Artist")

    with pytest.raises(LastFmError, match="artist information"):
        _parse_artist_image_payload({"artist": []}, "Artist")

    assert _select_artist_image_url("bad") is None
    assert (
        _select_artist_image_url(
            [
                "bad item",
                {"#text": "", "size": "large"},
                {"#text": "https://last.fm/custom.jpg", "size": "custom"},
            ]
        )
        == "https://last.fm/custom.jpg"
    )


def test_artist_info_client_ignores_lastfm_placeholder_star_image() -> None:
    page_url = "https://www.last.fm/music/Artist"
    placeholder_url = "https://lastfm.freetls.fastly.net/i/u/300x300/2a96cbd8b46e442fc41c2b86b821562f.png"
    session = ArtistInfoSession(
        {
            LASTFM_API_URL: FakeResponse(
                "",
                LASTFM_API_URL,
                json_payload={
                    "artist": {
                        "url": page_url,
                        "image": [{"#text": placeholder_url, "size": "mega"}],
                    }
                },
            ),
            page_url: FakeResponse("", page_url),
        }
    )

    artist_image = LastFmArtistInfoClient(api_key="test-key", session=session).fetch_artist_image(
        "Artist"
    )

    assert artist_image == ArtistImage(artist="Artist", page_url=page_url, image_url=None)
    assert session.requests == [
        (
            LASTFM_API_URL,
            {
                "method": "artist.getInfo",
                "artist": "Artist",
                "api_key": "test-key",
                "format": "json",
            },
        ),
        (page_url, None),
    ]


def test_artist_page_image_parser_prefers_social_metadata_and_ignores_placeholder() -> None:
    page_url = "https://www.last.fm/music/Artist"
    real_image_url = "https://lastfm.freetls.fastly.net/i/u/ar0/real.jpg"
    html = f"""
    <meta property="og:image" content="https://lastfm.freetls.fastly.net/i/u/ar0/2a96cbd8b46e442fc41c2b86b821562f.png">
    <meta name="twitter:image" content="{real_image_url}">
    """

    assert _select_artist_page_image_url(html, page_url) == real_image_url
    assert _is_lastfm_placeholder_image_url("https://last.fm/2a96cbd8b46e442fc41c2b86b821562f.png")


def test_artist_page_image_parser_uses_header_background_image() -> None:
    page_url = "https://www.last.fm/music/Artist"
    html = """
    <div
        class="header-new-background-image"
        style="background-image: url(/i/u/ar0/artist.jpg);"
    ></div>
    """

    assert _select_artist_page_image_url(html, page_url) == "https://www.last.fm/i/u/ar0/artist.jpg"


def test_raise_for_unsuccessful_artist_response_reports_http_status() -> None:
    response = FakeResponse("", "https://last.fm/api", status_code=500)

    with pytest.raises(LastFmError, match="HTTP status 500"):
        _raise_for_unsuccessful_artist_response(response, "https://last.fm/api")


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


def test_controlled_sleep_stops_before_first_sleep_when_control_is_false(monkeypatch) -> None:
    sleep_calls: list[float] = []
    monkeypatch.setattr("my_lastfm_player.lastfm.time.monotonic", lambda: 0.0)
    monkeypatch.setattr(
        "my_lastfm_player.lastfm.time.sleep",
        lambda seconds: sleep_calls.append(seconds),
    )

    assert not _controlled_sleep(0.1, lambda: False)
    assert sleep_calls == []


def test_retryable_error_detection() -> None:
    assert _is_retryable_error(requests.ConnectionError("network"))
    assert _is_retryable_error(ValueError("bad json"))
    assert _is_retryable_error(LastFmError("Last.fm returned HTTP status 503"))
    assert not _is_retryable_error(LastFmError("Last.fm returned HTTP status 404"))


def test_scraper_rejects_empty_username_for_track_count_fetch() -> None:
    with pytest.raises(ValueError, match="username"):
        LastFmLovedTracksScraper().fetch_loved_track_count("")


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
