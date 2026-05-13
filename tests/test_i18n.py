from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

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


def test_translate_falls_back_to_source_on_bad_placeholder(monkeypatch, qapp) -> None:
    from PyQt6.QtCore import QCoreApplication

    monkeypatch.setattr(
        QCoreApplication,
        "translate",
        staticmethod(lambda _ctx, _txt: "播放{艺术家}"),
    )
    result = translate("ApplicationController", "Playing {artist}", artist="Kraftwerk")
    assert result == "Playing Kraftwerk"


def test_translation_catalogs_are_complete_and_keep_placeholders() -> None:
    placeholder_pattern = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")
    catalogs = sorted(
        (Path(__file__).parents[1] / "my_lastfm_player" / "translations").glob("*.ts")
    )

    assert catalogs
    for catalog in catalogs:
        root = ET.parse(catalog).getroot()
        for message in root.findall(".//message"):
            translation = message.find("translation")
            if translation is not None and translation.get("type") == "vanished":
                continue
            source_text = message.findtext("source") or ""
            translation_text = (
                "" if translation is None or translation.text is None else translation.text
            )
            assert translation is not None
            assert translation.get("type") != "unfinished", (
                f"{catalog.name} has unfinished translation: {source_text}"
            )
            assert set(placeholder_pattern.findall(translation_text)) == set(
                placeholder_pattern.findall(source_text)
            ), f"{catalog.name} changes placeholders for: {source_text}"
