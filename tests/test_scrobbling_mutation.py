"""Scrobbles and now-playing updates without a known duration send no duration."""

from __future__ import annotations

from my_lastfm_player.scrobbling import ScrobblingService


class RecordingNetwork:
    def __init__(self, **kwargs) -> None:
        self.calls: list[tuple[str, dict]] = []

    def get_authenticated_user(self):
        class User:
            def get_name(self, **kwargs):
                return "Alice"

        return User()

    def scrobble(self, **kwargs) -> None:
        self.calls.append(("scrobble", kwargs))

    def update_now_playing(self, **kwargs) -> None:
        self.calls.append(("now_playing", kwargs))


def _connected_service() -> tuple[ScrobblingService, list[RecordingNetwork]]:
    networks: list[RecordingNetwork] = []

    def network_factory(**kwargs):
        network = RecordingNetwork(**kwargs)
        networks.append(network)
        return network

    service = ScrobblingService(
        "key", "secret", session_key="session", username="alice", network_factory=network_factory
    )
    assert service.try_connect()
    return service, networks


def test_default_duration_is_sent_as_none() -> None:
    service, networks = _connected_service()

    service.scrobble("Artist", "Title", 1_700_000_000)
    service.update_now_playing("Artist", "Title")

    assert networks[0].calls == [
        (
            "scrobble",
            {"artist": "Artist", "title": "Title", "timestamp": 1_700_000_000, "duration": None},
        ),
        ("now_playing", {"artist": "Artist", "title": "Title", "duration": None}),
    ]
