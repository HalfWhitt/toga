from __future__ import annotations

from typing import Any, Literal

from toga.constants import Direction

from .base import StyleT, Widget


class Divider(Widget):
    HORIZONTAL = Direction.HORIZONTAL
    VERTICAL = Direction.VERTICAL

    def __init__(
        self,
        id: str | None = None,
        style: StyleT | None = None,
        direction: Direction = HORIZONTAL,
        **kwargs,
    ):
        """Create a new divider line.

        :param id: The ID for the widget.
        :param style: A style object. If no style is provided, a default style will be
            applied to the widget.
        :param direction: The direction in which the divider will be drawn. Either
            :attr:`~toga.constants.Direction.HORIZONTAL` or
            :attr:`~toga.constants.Direction.VERTICAL`; defaults to
            :attr:`~toga.constants.Direction.HORIZONTAL`
        :param kwargs: Initial style properties.
        """
        super().__init__(id, style, **kwargs)

        self.direction = direction

    def _create(self) -> Any:
        return self.factory.Divider(interface=self)

    @property
    def enabled(self) -> Literal[True]:
        """Is the widget currently enabled? i.e., can the user interact with the widget?

        Divider widgets cannot be disabled; this property will always return True; any
        attempt to modify it will be ignored.
        """
        return True

    @enabled.setter
    def enabled(self, value: object) -> None:
        pass

    def focus(self) -> None:
        """No-op; Divider cannot accept input focus."""
        pass

    @property
    def direction(self) -> Direction:
        """The direction in which the visual separator will be drawn."""
        return self._impl.get_direction()

    @direction.setter
    def direction(self, value: object) -> None:
        self._impl.set_direction(value)
        self.refresh()
