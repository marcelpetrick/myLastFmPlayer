from __future__ import annotations

import pytest

from my_lastfm_player.ui.flags import _H, _W, flag_icon


@pytest.mark.usefixtures("qapp")
class TestFlagIcon:
    @pytest.mark.parametrize("code", ["en", "de", "hr", "uk", "zh"])
    def test_known_codes_return_non_empty_icon(self, code: str) -> None:
        icon = flag_icon(code)
        assert not icon.isNull()

    def test_unknown_code_returns_null_icon(self) -> None:
        icon = flag_icon("xx")
        assert icon.isNull()

    @pytest.mark.parametrize("code", ["en", "de", "hr", "uk", "zh"])
    def test_pixmap_dimensions(self, code: str) -> None:
        icon = flag_icon(code)
        pm = icon.pixmap(_W, _H)
        assert pm.width() == _W
        assert pm.height() == _H
