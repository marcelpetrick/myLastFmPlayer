from __future__ import annotations

import sys
import types

from my_lastfm_player.scrobbling import (
    SCROBBLE_THRESHOLD,
    ScrobblingService,
    _pylast_network_factory,
    _pylast_sg_factory,
)


class FakeUser:
    def get_name(self) -> str:
        return "testuser"


class FakeNetwork:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.scrobbles: list[dict] = []
        self.now_playing: list[dict] = []

    def get_authenticated_user(self) -> FakeUser:
        return FakeUser()

    def scrobble(self, **kwargs) -> None:
        self.scrobbles.append(kwargs)

    def update_now_playing(self, **kwargs) -> None:
        self.now_playing.append(kwargs)


class FakeSG:
    def __init__(self, network) -> None:
        self._network = network

    def get_web_auth_url(self) -> str:
        return "https://last.fm/api/auth/?token=testtoken"

    def get_web_auth_session_key(self, url: str) -> str:
        return "test_session_key_123"


def _make_service(**kwargs) -> tuple[ScrobblingService, list[FakeNetwork]]:
    created: list[FakeNetwork] = []

    def fake_network(**kw):
        net = FakeNetwork(**kw)
        created.append(net)
        return net

    svc = ScrobblingService(
        api_key="key",
        api_secret="secret",
        network_factory=fake_network,
        sg_factory=FakeSG,
        **kwargs,
    )
    return svc, created


# ── Construction / properties ─────────────────────────────────────────────────

def test_initial_state_is_not_authenticated() -> None:
    svc, _ = _make_service()
    assert not svc.is_authenticated
    assert not svc.auth_in_progress
    assert svc.username == ""
    assert svc.session_key == ""


def test_has_api_credentials_true_when_key_and_secret_set() -> None:
    svc, _ = _make_service()
    assert svc.has_api_credentials


def test_has_api_credentials_false_when_empty() -> None:
    svc = ScrobblingService(api_key="", api_secret="")
    assert not svc.has_api_credentials


def test_scrobble_threshold_constant() -> None:
    assert SCROBBLE_THRESHOLD == 0.33


# ── try_connect ───────────────────────────────────────────────────────────────

def test_try_connect_with_valid_session_key() -> None:
    svc, networks = _make_service(session_key="stored_key")

    result = svc.try_connect()

    assert result
    assert svc.is_authenticated
    assert svc.username == "testuser"
    assert networks[0].kwargs["session_key"] == "stored_key"


def test_try_connect_without_session_key_returns_false() -> None:
    svc, _ = _make_service()
    assert not svc.try_connect()
    assert not svc.is_authenticated


def test_try_connect_handles_network_error() -> None:
    def failing_network(**kw):
        raise RuntimeError("network error")

    svc = ScrobblingService(
        api_key="k", api_secret="s", session_key="key", network_factory=failing_network
    )
    assert not svc.try_connect()
    assert not svc.is_authenticated


# ── Web auth flow ─────────────────────────────────────────────────────────────

def test_start_web_auth_returns_url() -> None:
    svc, _ = _make_service()
    url = svc.start_web_auth()
    assert url == "https://last.fm/api/auth/?token=testtoken"
    assert svc.auth_in_progress


def test_start_web_auth_without_credentials_returns_none() -> None:
    svc = ScrobblingService(api_key="", api_secret="")
    assert svc.start_web_auth() is None
    assert not svc.auth_in_progress


def test_start_web_auth_handles_error() -> None:
    def failing_network(**kw):
        raise RuntimeError("network error")

    svc = ScrobblingService(api_key="k", api_secret="s", network_factory=failing_network)

    assert svc.start_web_auth() is None
    assert not svc.auth_in_progress


def test_complete_web_auth_sets_authenticated() -> None:
    svc, networks = _make_service()
    svc.start_web_auth()

    result = svc.complete_web_auth()

    assert result
    assert svc.is_authenticated
    assert svc.username == "testuser"
    assert svc.session_key == "test_session_key_123"
    assert not svc.auth_in_progress


def test_complete_web_auth_without_start_returns_false() -> None:
    svc, _ = _make_service()
    assert not svc.complete_web_auth()


def test_complete_web_auth_handles_error() -> None:
    class FailingSG:
        def __init__(self, network) -> None:
            pass

        def get_web_auth_url(self) -> str:
            return "https://last.fm/api/auth/?token=x"

        def get_web_auth_session_key(self, url: str) -> str:
            raise RuntimeError("not yet authorized")

    svc = ScrobblingService(
        api_key="k", api_secret="s",
        network_factory=lambda **kw: FakeNetwork(**kw),
        sg_factory=FailingSG,
    )
    svc.start_web_auth()
    assert not svc.complete_web_auth()
    assert not svc.is_authenticated


# ── disconnect ────────────────────────────────────────────────────────────────

def test_disconnect_clears_session() -> None:
    svc, _ = _make_service(session_key="k")
    svc.try_connect()
    assert svc.is_authenticated

    svc.disconnect()

    assert not svc.is_authenticated
    assert svc.session_key == ""
    assert not svc.auth_in_progress


# ── scrobble ──────────────────────────────────────────────────────────────────

def test_scrobble_submits_when_authenticated() -> None:
    svc, networks = _make_service(session_key="k")
    svc.try_connect()

    svc.scrobble("Artist", "Title", timestamp=1_700_000_000, duration_seconds=240)

    assert len(networks[-1].scrobbles) == 1
    s = networks[-1].scrobbles[0]
    assert s["artist"] == "Artist"
    assert s["title"] == "Title"
    assert s["timestamp"] == 1_700_000_000
    assert s["duration"] == 240


def test_scrobble_skipped_when_not_authenticated() -> None:
    svc, networks = _make_service()
    svc.scrobble("Artist", "Title", timestamp=1_700_000_000)
    assert not networks  # no network created → can't scrobble


def test_scrobble_skipped_when_disabled() -> None:
    svc, networks = _make_service(session_key="k", scrobbling_enabled=False)
    svc.try_connect()
    svc.scrobble("Artist", "Title", timestamp=1_700_000_000)
    assert networks[-1].scrobbles == []


def test_scrobble_duration_none_when_zero() -> None:
    svc, networks = _make_service(session_key="k")
    svc.try_connect()
    svc.scrobble("A", "T", timestamp=123, duration_seconds=0)
    assert networks[-1].scrobbles[0]["duration"] is None


def test_scrobble_handles_network_error_gracefully() -> None:
    def erroring_network(**kw):
        net = FakeNetwork(**kw)

        def bad_scrobble(**_):
            raise RuntimeError("api error")

        net.scrobble = bad_scrobble
        return net

    svc = ScrobblingService(
        api_key="k", api_secret="s", session_key="key", network_factory=erroring_network
    )
    svc.try_connect()
    svc.scrobble("A", "T", timestamp=123)  # must not raise


# ── update_now_playing ────────────────────────────────────────────────────────

def test_update_now_playing_submits_when_authenticated() -> None:
    svc, networks = _make_service(session_key="k")
    svc.try_connect()
    svc.update_now_playing("Artist", "Title", duration_seconds=180)
    assert networks[-1].now_playing[0]["artist"] == "Artist"


def test_update_now_playing_skipped_when_not_authenticated() -> None:
    svc, networks = _make_service()
    svc.update_now_playing("A", "T")
    assert not networks


def test_update_now_playing_handles_network_error_gracefully() -> None:
    def erroring_network(**kw):
        net = FakeNetwork(**kw)

        def bad_now_playing(**_):
            raise RuntimeError("api error")

        net.update_now_playing = bad_now_playing
        return net

    svc = ScrobblingService(
        api_key="k", api_secret="s", session_key="key", network_factory=erroring_network
    )
    svc.try_connect()
    svc.update_now_playing("A", "T")  # must not raise


# ── credentials_dict ──────────────────────────────────────────────────────────

def test_credentials_dict_contains_required_keys() -> None:
    svc, _ = _make_service(session_key="k", username="user")
    d = svc.credentials_dict()
    assert d["username"] == "user"
    assert "session_key" in d
    assert "scrobbling_enabled" in d


def test_pylast_factories_delegate_to_pylast(monkeypatch) -> None:
    class FakeLastFMNetwork:
        def __init__(self, **kwargs) -> None:
            self.kwargs = kwargs

    class FakeSessionKeyGenerator:
        def __init__(self, network) -> None:
            self.network = network

    fake_pylast = types.SimpleNamespace(
        LastFMNetwork=FakeLastFMNetwork,
        SessionKeyGenerator=FakeSessionKeyGenerator,
    )
    monkeypatch.setitem(sys.modules, "pylast", fake_pylast)

    network = _pylast_network_factory(api_key="key")
    generator = _pylast_sg_factory(network)

    assert network.kwargs == {"api_key": "key"}
    assert generator.network is network
