from __future__ import annotations

import pytest

from my_lastfm_player import i18n as i18n_module
from my_lastfm_player.i18n import (
    DEFAULT_LANGUAGE_CODE,
    TranslationManager,
    language_by_code,
    translate,
)


class FakeApp:
    def __init__(self) -> None:
        self.installed: list[object] = []
        self.removed: list[object] = []

    def installTranslator(self, translator: object) -> None:
        self.installed.append(translator)

    def removeTranslator(self, translator: object) -> None:
        self.removed.append(translator)


class FakeTranslator:
    loaded_paths: list[str] = []
    should_load = True

    def __init__(self, _app: FakeApp) -> None:
        self.path = ""

    def load(self, path: str) -> bool:
        self.path = path
        self.loaded_paths.append(path)
        return self.should_load


def test_language_lookup_accepts_configured_codes_and_rejects_unknown() -> None:
    assert language_by_code(DEFAULT_LANGUAGE_CODE).native_name == "English"
    assert language_by_code("de").native_name == "Deutsch"

    with pytest.raises(ValueError, match="Unsupported language code"):
        language_by_code("xx")


def test_translation_manager_installs_removes_and_handles_load_failure(monkeypatch) -> None:
    app = FakeApp()
    manager = TranslationManager(app)  # type: ignore[arg-type]
    monkeypatch.setattr(i18n_module, "QTranslator", FakeTranslator)

    FakeTranslator.should_load = True
    assert manager.set_language("de")
    assert manager.current_language == "de"
    assert len(app.installed) == 1
    assert FakeTranslator.loaded_paths[-1].endswith("my_lastfm_player_de.qm")

    assert manager.set_language("en")
    assert manager.current_language == "en"
    assert app.removed == app.installed

    FakeTranslator.should_load = False
    assert not manager.set_language("hr")
    assert manager.current_language == "hr"
    assert len(app.installed) == 1


def test_translate_formats_named_values(qapp) -> None:
    assert translate("Tests", "Hello {name}", name="World") == "Hello World"
    assert translate("Tests", "Plain text") == "Plain text"
