"""``pyqtSignal`` with a correct static signature.

The PyQt6 stubs declare the keyword-only ``arguments`` parameter of
``pyqtSignal.__init__`` without a default, so mypy reports every ``pyqtSignal(...)``
declaration as a missing-argument error although the runtime accepts it. At runtime
this module re-exports PyQt's own ``pyqtSignal`` unchanged; only the type checker
sees the corrected signature.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from PyQt6.QtCore import pyqtSignal as _PyQtSignal

if TYPE_CHECKING:

    def pyqtSignal(  # noqa: N802  # pylint: disable=unused-argument
        *types: Any, name: str = ..., revision: int = ...
    ) -> _PyQtSignal:
        """Declare a Qt signal (typing view of ``PyQt6.QtCore.pyqtSignal``)."""
        ...

else:
    pyqtSignal = _PyQtSignal

__all__ = ["pyqtSignal"]
