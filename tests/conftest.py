from __future__ import annotations

import os
import sys
import xml.etree.ElementTree as ET
from collections.abc import Iterator
from pathlib import Path

import pytest
from PyQt6.QtCore import QTranslator
from PyQt6.QtWidgets import QApplication

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

CATALOG_PATH = (
    Path(__file__).resolve().parents[1]
    / "my_lastfm_player"
    / "translations"
    / "my_lastfm_player_de.ts"
)


def load_translation_catalog(path: Path = CATALOG_PATH) -> dict[str, set[str]]:
    """Return the source strings of the Qt catalog, grouped by context."""

    catalog: dict[str, set[str]] = {}
    for context in ET.parse(path).getroot().iter("context"):
        name = context.findtext("name", default="")
        catalog.setdefault(name, set()).update(
            message.findtext("source", default="") for message in context.iter("message")
        )
    return catalog


class CatalogCheckingTranslator(QTranslator):
    """Record every application string lookup that is missing from the catalog.

    Installed for the whole test session, it sees each ``tr()`` and
    ``QCoreApplication.translate()`` call. A context or source string that the
    catalog does not know would stay untranslated for every user, so the test that
    triggered it fails. Qt's own strings (contexts starting with ``Q``) are ignored.
    It never translates anything itself, so the English text is unchanged.
    """

    def __init__(self, catalog: dict[str, set[str]]) -> None:
        super().__init__()
        self.catalog = catalog
        self.violations: list[tuple[str, str]] = []

    def translate(  # pylint: disable=unused-argument
        self,
        context: str | None,
        source_text: str | None,
        disambiguation: str | None = None,
        n: int = -1,
    ) -> str | None:
        context = context or ""
        source_text = source_text or ""
        if context.startswith("Q") and context not in self.catalog:
            return None
        if source_text not in self.catalog.get(context, set()):
            self.violations.append((context, source_text))
        # None is a null QString: "no translation here", so Qt falls back.
        return None

    def isEmpty(self) -> bool:  # noqa: N802 - Qt override
        return False


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    app = QApplication.instance() or QApplication([])
    if not hasattr(app, "catalog_translator"):
        app.catalog_translator = CatalogCheckingTranslator(load_translation_catalog())
        app.installTranslator(app.catalog_translator)
    return app


@pytest.fixture(autouse=True)
def fail_on_string_missing_from_translation_catalog() -> Iterator[None]:
    """Fail the test when it looked up a UI string the translation catalog lacks.

    Translators only run while a QApplication exists, which the ``qapp`` fixture
    creates on first use; tests before that are not checked.
    """

    yield
    translator: CatalogCheckingTranslator | None = getattr(
        QApplication.instance(), "catalog_translator", None
    )
    if translator is None or not translator.violations:
        return
    context, source_text = translator.violations[0]
    translator.violations.clear()
    pytest.fail(
        "UI string missing from the translation catalog: "
        f"context={context!r}, source={source_text!r}"
    )


@pytest.fixture(autouse=True)
def fail_on_unhandled_qt_slot_exception() -> Iterator[None]:
    """Turn an exception raised inside a Qt slot into a test failure.

    Without a custom ``sys.excepthook`` PyQt aborts the whole process on such an
    exception, which kills the pytest run (and every mutmut worker) instead of
    failing the one test that triggered it.
    """

    errors: list[BaseException] = []
    previous_hook = sys.excepthook
    sys.excepthook = lambda _type, value, _traceback: errors.append(value)
    try:
        yield
    finally:
        sys.excepthook = previous_hook
    if errors:
        pytest.fail(f"Unhandled exception in a Qt slot: {errors[0]!r}")
