from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Literal, Protocol, TypeVar

import toga
from toga.handlers import wrapped_handler
from toga.sources import ListSource, Row, Source

from .base import StyleT, Widget

SourceT = TypeVar("SourceT", bound=Source)


class OnPrimaryActionHandler(Protocol):
    def __call__(self, widget: DetailedList, row: Any, **kwargs: Any) -> None:
        """A handler to invoke for the primary action.

        :param widget: The DetailedList that was invoked.
        :param row: The current row for the detailed list.
        :param kwargs: Ensures compatibility with arguments added in future versions.
        """


class OnSecondaryActionHandler(Protocol):
    def __call__(self, widget: DetailedList, row: Any, **kwargs: Any) -> None:
        """A handler to invoke for the secondary action.

        :param widget: The DetailedList that was invoked.
        :param row: The current row for the detailed list.
        :param kwargs: Ensures compatibility with arguments added in future versions.
        """


class OnRefreshHandler(Protocol):
    def __call__(self, widget: DetailedList, **kwargs: Any) -> None:
        """A handler to invoke when the detailed list is refreshed.

        :param widget: The DetailedList that was refreshed.
        :param kwargs: Ensures compatibility with arguments added in future versions.
        """


class OnSelectHandler(Protocol):
    def __call__(self, widget: DetailedList, **kwargs: Any) -> None:
        """A handler to invoke when the detailed list is selected.

        :param widget: The DetailedList that was selected.
        :param kwargs: Ensures compatibility with arguments added in future versions.
        """


class DetailedList(Widget):
    def __init__(
        self,
        id: str | None = None,
        style: StyleT | None = None,
        data: SourceT | Iterable | None = None,
        accessors: tuple[str, str, str] = ("title", "subtitle", "icon"),
        missing_value: str = "",
        primary_action: str | None = "Delete",
        on_primary_action: OnPrimaryActionHandler | None = None,
        secondary_action: str | None = "Action",
        on_secondary_action: OnSecondaryActionHandler | None = None,
        on_refresh: OnRefreshHandler | None = None,
        on_select: toga.widgets.detailedlist.OnSelectHandler | None = None,
        **kwargs,
    ):
        """Create a new DetailedList widget.

        :param id: The ID for the widget.
        :param style: A style object. If no style is provided, a default style will be
            applied to the widget.
        :param data: Initial :any:`data` to be displayed in the list.
        :param accessors: The accessors to use to retrieve the data for each item, in
            the form (title, subtitle, icon).
        :param missing_value: The text that will be shown when a row doesn't provide a
            value for its title or subtitle.
        :param on_select: Initial :any:`on_select` handler.
        :param primary_action: The name for the primary action.
        :param on_primary_action: Initial :any:`on_primary_action` handler.
        :param secondary_action: The name for the secondary action.
        :param on_secondary_action: Initial :any:`on_secondary_action` handler.
        :param on_refresh: Initial :any:`on_refresh` handler.
        :param kwargs: Initial style properties.
        """
        # Prime the attributes and handlers that need to exist when the widget is
        # created.
        self._accessors = accessors
        self._missing_value = missing_value
        self._primary_action = primary_action
        self._secondary_action = secondary_action
        self.on_select = None

        self._data: SourceT | ListSource = None

        super().__init__(id, style, **kwargs)

        self.data = data
        self.on_primary_action = on_primary_action
        self.on_secondary_action = on_secondary_action
        self.on_refresh = on_refresh
        self.on_select = on_select

    def _create(self) -> Any:
        return self.factory.DetailedList(interface=self)

    @property
    def enabled(self) -> Literal[True]:
        """Is the widget currently enabled? i.e., can the user interact with the widget?
        DetailedList widgets cannot be disabled; this property will always return True;
        any attempt to modify it will be ignored.
        """
        return True

    @enabled.setter
    def enabled(self, value: object) -> None:
        pass

    def focus(self) -> None:
        """No-op; DetailedList cannot accept input focus."""
        pass

    @property
    def data(self) -> SourceT | ListSource:
        """The data to display in the table.

        When setting this property:

        * A :any:`Source` will be used as-is. It must either be a :any:`ListSource`, or
          a custom class that provides the same methods.

        * A value of None is turned into an empty ListSource.

        * Otherwise, the value must be an iterable, which is copied into a new
          ListSource. Items are converted as shown :ref:`here <listsource-item>`.
        """
        return self._data

    @data.setter
    def data(self, data: SourceT | Iterable | None) -> None:
        if data is None:
            self._data = ListSource(data=[], accessors=self.accessors)
        elif isinstance(data, Source):
            self._data = data
        else:
            self._data = ListSource(data=data, accessors=self.accessors)

        self._data.add_listener(self._impl)
        self._impl.change_source(source=self._data)

    def scroll_to_top(self) -> None:
        """Scroll the view so that the top of the list (first row) is visible."""
        self.scroll_to_row(0)

    def scroll_to_row(self, row: int) -> None:
        """Scroll the view so that the specified row index is visible.

        :param row: The index of the row to make visible. Negative values refer to the
            nth last row (-1 is the last row, -2 second last, and so on).
        """
        if len(self.data) > 1:
            if row >= 0:
                self._impl.scroll_to_row(min(row, len(self.data)))
            else:
                self._impl.scroll_to_row(max(len(self.data) + row, 0))

    def scroll_to_bottom(self) -> None:
        """Scroll the view so that the bottom of the list (last row) is visible."""
        self.scroll_to_row(-1)

    @property
    def accessors(self) -> tuple[str, str, str]:
        """The accessors used to populate the list (read-only)"""
        return self._accessors

    @property
    def missing_value(self) -> str:
        """The text that will be shown when a row doesn't provide a value for its
        title or subtitle.
        """
        return self._missing_value

    @property
    def selection(self) -> Row | None:
        """The current selection of the table.

        Returns the selected Row object, or :any:`None` if no row is currently selected.
        """
        try:
            return self.data[self._impl.get_selection()]
        except TypeError:
            return None

    @property
    def on_primary_action(self) -> OnPrimaryActionHandler:
        """The handler to invoke when the user performs the primary action on a row of
        the DetailedList.

        The primary action is "swipe left" on platforms that use swipe interactions;
        other platforms may manifest this action in other ways (e.g, a context menu).

        If no ``on_primary_action`` handler is provided, the primary action will be
        disabled in the UI.
        """
        return self._on_primary_action

    @on_primary_action.setter
    def on_primary_action(self, handler: OnPrimaryActionHandler) -> None:
        self._on_primary_action = wrapped_handler(self, handler)
        self._impl.set_primary_action_enabled(handler is not None)

    @property
    def on_secondary_action(self) -> OnSecondaryActionHandler:
        """The handler to invoke when the user performs the secondary action on a row of
        the DetailedList.

        The secondary action is "swipe right" on platforms that use swipe interactions;
        other platforms may manifest this action in other ways (e.g, a context menu).

        If no ``on_secondary_action`` handler is provided, the secondary action will be
        disabled in the UI.
        """
        return self._on_secondary_action

    @on_secondary_action.setter
    def on_secondary_action(self, handler: OnSecondaryActionHandler) -> None:
        self._on_secondary_action = wrapped_handler(self, handler)
        self._impl.set_secondary_action_enabled(handler is not None)

    @property
    def on_refresh(self) -> OnRefreshHandler:
        """The callback function to invoke when the user performs a refresh action
        (usually "pull down") on the DetailedList.

        If no ``on_refresh`` handler is provided, the refresh UI action will be
        disabled.
        """
        return self._on_refresh

    @on_refresh.setter
    def on_refresh(self, handler: OnRefreshHandler) -> None:
        self._on_refresh = wrapped_handler(
            self, handler, cleanup=self._impl.after_on_refresh
        )
        self._impl.set_refresh_enabled(handler is not None)

    @property
    def on_select(self) -> OnSelectHandler:
        """The callback function that is invoked
        when a row of the DetailedList is selected."""
        return self._on_select

    @on_select.setter
    def on_select(self, handler: toga.widgets.detailedlist.OnSelectHandler) -> None:
        self._on_select = wrapped_handler(self, handler)
