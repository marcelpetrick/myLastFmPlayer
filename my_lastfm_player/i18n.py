from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PyQt6.QtCore import QCoreApplication, QTranslator


@dataclass(frozen=True, slots=True)
class Language:
    """Language offered by the UI language menu."""

    code: str
    native_name: str
    qm_name: str


SUPPORTED_LANGUAGES = (
    Language("en", "English", ""),
    Language("hr", "Hrvatski", "my_lastfm_player_hr.qm"),
    Language("de", "Deutsch", "my_lastfm_player_de.qm"),
    Language("zh", "中文", "my_lastfm_player_zh.qm"),
    Language("uk", "Українська", "my_lastfm_player_uk.qm"),
)
DEFAULT_LANGUAGE_CODE = "en"
TRANSLATIONS_DIR = Path(__file__).resolve().parent / "translations"


class TranslationManager:
    """Install and remove Qt translators for live language switching."""

    def __init__(self, app: QCoreApplication) -> None:
        self.app = app
        self.current_language = DEFAULT_LANGUAGE_CODE
        self._translator: QTranslator | None = None

    def set_language(self, code: str) -> bool:
        """Install the translator for ``code`` and return whether it was loaded."""

        language = language_by_code(code)
        self._remove_translator()
        self.current_language = language.code
        if language.code == DEFAULT_LANGUAGE_CODE:
            return True

        translator = QTranslator(self.app)
        qm_path = TRANSLATIONS_DIR / language.qm_name
        if not translator.load(str(qm_path)):
            return False
        self.app.installTranslator(translator)
        self._translator = translator
        return True

    def _remove_translator(self) -> None:
        if self._translator is not None:
            self.app.removeTranslator(self._translator)
            self._translator = None


def language_by_code(code: str) -> Language:
    """Return configured language metadata for ``code``."""

    for language in SUPPORTED_LANGUAGES:
        if language.code == code:
            return language
    raise ValueError(f"Unsupported language code: {code}")


def translate(context: str, text: str, **values: object) -> str:
    """Translate ``text`` in ``context`` and format named placeholders."""

    translated = QCoreApplication.translate(context, text)
    if values:
        return translated.format(**values)
    return translated
