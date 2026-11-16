"""Exact contract of ScrobblingService towards pylast and its auth-generation guards.

The fakes record every keyword argument, so a dropped or swapped argument fails.
"""

from __future__ import annotations

import pytest

from my_lastfm_player import scrobbling
from my_lastfm_player.scrobbling import LastFmWriteError, ScrobblingService


class Recorder:
    def __init__(self) -> None:
        self.networks: list[RecordingNetwork] = []
        self.generators: list[RecordingGenerator] = []
        self.tracks: list[tuple] = []
        self.on_network = None
        self.fail_network = False
        self.fail_generator_url = False
        self.fail_session = False

    def network_factory(self, **kwargs):
        if self.on_network is not None:
            self.on_network()
        if self.fail_network:
            raise RuntimeError("network down")
        network = RecordingNetwork(kwargs)
        self.networks.append(network)
        return network

    def sg_factory(self, network):
        generator = RecordingGenerator(network, self)
        self.generators.append(generator)
        return generator

    def track_factory(self, artist, title, network, **kwargs):
        self.tracks.append((artist, title, network, kwargs))
        return RecordingTrack(self)


class RecordingNetwork:
    def __init__(self, kwargs: dict) -> None:
        self.kwargs = kwargs
        self.calls: list[tuple] = []

    def get_authenticated_user(self):
        network = self

        class User:
            def get_name(self, **kwargs):
                network.calls.append(("get_name", kwargs))
                return "ProperName" if kwargs.get("properly_capitalized") else "propername"

        return User()

    def scrobble(self, **kwargs) -> None:
        self.calls.append(("scrobble", kwargs))

    def update_now_playing(self, **kwargs) -> None:
        self.calls.append(("now_playing", kwargs))


class RecordingGenerator:
    def __init__(self, network, recorder: Recorder) -> None:
        self.network = network
        self.recorder = recorder
        self.session_urls: list[str] = []

    def get_web_auth_url(self) -> str:
        if self.recorder.fail_generator_url:
            raise RuntimeError("no token")
        return "https://www.last.fm/api/auth/?token=t"

    def get_web_auth_session_key_username(self, url: str):
        self.session_urls.append(url)
        if self.recorder.fail_session:
            raise RuntimeError("not authorized yet")
        return "session-key", "WebUser"


class RecordingTrack:
    def __init__(self, recorder: Recorder) -> None:
        self.recorder = recorder

    def get_userloved(self):
        return 1

    def love(self) -> None:
        self.recorder.tracks.append("love")

    def unlove(self) -> None:
        self.recorder.tracks.append("unlove")


def make_service(recorder: Recorder, **kwargs) -> ScrobblingService:
    values = {"api_key": "key", "api_secret": "secret", **kwargs}
    return ScrobblingService(
        network_factory=recorder.network_factory,
        sg_factory=recorder.sg_factory,
        track_factory=recorder.track_factory,
        **values,
    )


def connected_service(recorder: Recorder) -> ScrobblingService:
    service = make_service(recorder, session_key="sk", username="user")
    assert service.try_connect()
    return service


def test_default_factories_are_the_pylast_ones() -> None:
    service = ScrobblingService("key", "secret")

    assert service._network_factory is scrobbling._pylast_network_factory
    assert service._sg_factory is scrobbling._pylast_sg_factory
    assert service._track_factory is scrobbling._pylast_track_factory
    assert service.username == ""
    assert service.session_key == ""
    assert service.scrobbling_enabled is True
    assert not service.is_authenticated
    assert not service.auth_in_progress


def test_try_connect_passes_stored_credentials_and_keeps_the_verified_name() -> None:
    recorder = Recorder()
    service = make_service(recorder, session_key="sk", username="user")

    assert service.try_connect()

    (network,) = recorder.networks
    assert network.kwargs == {
        "api_key": "key",
        "api_secret": "secret",
        "session_key": "sk",
        "username": "user",
    }
    assert network.calls == [("get_name", {"properly_capitalized": True})]
    assert service.username == "ProperName"
    assert service.is_authenticated
    assert service.can_write_loves


@pytest.mark.parametrize(
    "kwargs",
    [
        {"session_key": "", "username": "user"},
        {"session_key": "sk", "username": "user", "api_key": ""},
        {"session_key": "sk", "username": "user", "api_secret": ""},
        {"session_key": "sk", "username": ""},
    ],
)
def test_try_connect_refuses_incomplete_credentials_without_a_request(kwargs) -> None:
    recorder = Recorder()
    service = make_service(recorder, **kwargs)

    assert service.try_connect() is False
    assert recorder.networks == []
    assert not service.is_authenticated


def test_failed_reconnect_drops_an_established_session() -> None:
    recorder = Recorder()
    service = connected_service(recorder)
    recorder.fail_network = True

    assert service.try_connect() is False
    assert not service.is_authenticated


def test_try_connect_result_is_discarded_after_a_concurrent_disconnect() -> None:
    recorder = Recorder()
    service = make_service(recorder, session_key="sk", username="user")
    recorder.on_network = service.disconnect

    assert service.try_connect() is False
    assert not service.is_authenticated
    assert service.username == "user"


def test_failed_connect_after_a_concurrent_disconnect_leaves_state_alone() -> None:
    recorder = Recorder()
    service = connected_service(recorder)

    def disconnect_then_fail() -> None:
        service.disconnect()
        service._authenticated = True  # a newer flow already re-established the session
        recorder.fail_network = True

    recorder.on_network = disconnect_then_fail

    assert service.try_connect() is False
    assert service.is_authenticated


def test_start_web_auth_uses_only_application_credentials() -> None:
    recorder = Recorder()
    service = make_service(recorder)

    url = service.start_web_auth()

    assert url == "https://www.last.fm/api/auth/?token=t"
    (network,) = recorder.networks
    assert network.kwargs == {"api_key": "key", "api_secret": "secret"}
    assert recorder.generators[0].network is network
    assert service.auth_in_progress


def test_start_web_auth_without_credentials_does_nothing() -> None:
    recorder = Recorder()
    service = make_service(recorder, api_secret="")

    assert service.start_web_auth() is None
    assert recorder.networks == []
    assert service._auth_generation == 0


def test_start_web_auth_is_discarded_when_cancelled_meanwhile() -> None:
    recorder = Recorder()
    service = make_service(recorder)
    recorder.on_network = service.cancel_pending_authentication

    assert service.start_web_auth() is None
    assert not service.auth_in_progress
    assert service._sg is None


def test_failed_start_web_auth_clears_a_previous_pending_flow() -> None:
    recorder = Recorder()
    service = make_service(recorder)
    assert service.start_web_auth()
    recorder.fail_generator_url = True

    assert service.start_web_auth() is None
    assert not service.auth_in_progress
    assert service._sg is None


def test_failed_start_after_a_newer_flow_keeps_that_flow() -> None:
    recorder = Recorder()
    service = make_service(recorder)

    def newer_flow_then_fail() -> None:
        recorder.on_network = None
        assert service.start_web_auth()
        recorder.fail_network = True

    recorder.on_network = newer_flow_then_fail

    assert service.start_web_auth() is None
    assert service.auth_in_progress
    assert service._sg is recorder.generators[0]


def test_each_auth_change_advances_the_generation() -> None:
    recorder = Recorder()
    service = make_service(recorder)

    service.start_web_auth()
    service.start_web_auth()
    assert service._auth_generation == 2
    service.cancel_pending_authentication()
    assert service._auth_generation == 3
    service.disconnect()
    assert service._auth_generation == 4


def test_complete_web_auth_stores_the_returned_session() -> None:
    recorder = Recorder()
    service = make_service(recorder)
    url = service.start_web_auth()

    assert service.complete_web_auth()

    assert recorder.generators[0].session_urls == [url]
    session_network = recorder.networks[-1]
    assert session_network.kwargs == {
        "api_key": "key",
        "api_secret": "secret",
        "session_key": "session-key",
        "username": "WebUser",
    }
    assert service.username == "WebUser"
    assert service.session_key == "session-key"
    assert service.is_authenticated
    assert service._network is session_network
    assert not service.auth_in_progress
    assert service._sg is None


def test_complete_web_auth_requires_a_started_flow() -> None:
    recorder = Recorder()
    service = make_service(recorder)

    assert service.complete_web_auth() is False
    service._sg = object()
    assert service.complete_web_auth() is False
    assert recorder.networks == []


def test_complete_web_auth_failure_keeps_the_flow_pending() -> None:
    recorder = Recorder()
    service = make_service(recorder)
    service.start_web_auth()
    recorder.fail_session = True

    assert service.complete_web_auth() is False
    assert service.auth_in_progress
    assert not service.is_authenticated


def test_complete_web_auth_is_discarded_after_a_concurrent_cancel() -> None:
    recorder = Recorder()
    service = make_service(recorder)
    service.start_web_auth()
    recorder.on_network = service.cancel_pending_authentication

    assert service.complete_web_auth() is False
    assert not service.is_authenticated
    assert service.session_key == ""


def test_disconnect_clears_session_and_pending_flow() -> None:
    recorder = Recorder()
    service = connected_service(recorder)
    service.start_web_auth()

    service.disconnect()

    assert service.session_key == ""
    assert service._network is None
    assert not service.is_authenticated
    assert service._sg is None
    assert not service.auth_in_progress


def test_cancel_pending_authentication_keeps_an_established_session() -> None:
    recorder = Recorder()
    service = connected_service(recorder)
    service.start_web_auth()

    service.cancel_pending_authentication()

    assert service.is_authenticated
    assert service.session_key == "sk"
    assert service._sg is None
    assert not service.auth_in_progress


@pytest.mark.parametrize(("duration", "expected"), [(0, None), (215, 215)])
def test_scrobble_and_now_playing_send_exact_arguments(duration, expected) -> None:
    recorder = Recorder()
    service = connected_service(recorder)
    network = recorder.networks[0]

    service.update_now_playing("Artist", "Title", duration_seconds=duration)
    service.scrobble("Artist", "Title", 1700000000, duration_seconds=duration)

    assert network.calls[1:] == [
        ("now_playing", {"artist": "Artist", "title": "Title", "duration": expected}),
        (
            "scrobble",
            {"artist": "Artist", "title": "Title", "timestamp": 1700000000, "duration": expected},
        ),
    ]


def test_now_playing_is_skipped_when_scrobbling_is_disabled() -> None:
    recorder = Recorder()
    service = connected_service(recorder)
    service.scrobbling_enabled = False

    service.update_now_playing("Artist", "Title")

    assert recorder.networks[0].calls == [("get_name", {"properly_capitalized": True})]


def test_love_reads_and_writes_use_the_authenticated_username() -> None:
    recorder = Recorder()
    service = connected_service(recorder)
    network = recorder.networks[0]

    assert service.is_track_loved("Artist", "Title") is True
    service.love_track("Artist", "Title")
    service.unlove_track("Artist", "Title")

    assert recorder.tracks == [
        ("Artist", "Title", network, {"username": "ProperName"}),
        ("Artist", "Title", network, {"username": "ProperName"}),
        "love",
        ("Artist", "Title", network, {"username": "ProperName"}),
        "unlove",
    ]


def test_love_writes_need_both_a_session_and_a_network() -> None:
    recorder = Recorder()
    service = connected_service(recorder)
    service._network = None

    with pytest.raises(LastFmWriteError, match="^Not connected to Last.fm$"):
        service.love_track("Artist", "Title")
    with pytest.raises(LastFmWriteError, match="^Not connected to Last.fm$"):
        service.is_track_loved("Artist", "Title")


def test_love_write_errors_name_the_action_and_track() -> None:
    recorder = Recorder()
    service = connected_service(recorder)

    def broken_track(*_args, **_kwargs):
        raise RuntimeError("HTTP 500")

    service._track_factory = broken_track

    with pytest.raises(LastFmWriteError, match="^Last.fm unlove failed for A - T: HTTP 500$"):
        service.unlove_track("A", "T")
    with pytest.raises(LastFmWriteError, match="^Last.fm love failed for A - T: HTTP 500$"):
        service.love_track("A", "T")
    with pytest.raises(
        LastFmWriteError, match="^Could not read the loved state of A - T: HTTP 500$"
    ):
        service.is_track_loved("A", "T")
