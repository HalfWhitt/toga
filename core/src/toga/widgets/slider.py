from contextlib import contextmanager
from typing import Optional, Tuple

from toga.handlers import wrapped_handler

from .base import Widget


class Slider(Widget):
    def __init__(
        self,
        id=None,
        style=None,
        value=None,
        range=(0, 1),
        tick_count=None,
        on_change=None,
        on_press=None,
        on_release=None,
        enabled=True,
    ):
        """Create a new slider widget.

        Inherits from :class:`~toga.widgets.base.Widget`.

        :param id: The ID for the widget.
        :param style: A style object. If no style is provided, a default style
            will be applied to the widget.
        :param value: Initial :any:`value`: defaults to the mid-point of the range.
        :param range: Initial :any:`range`: defaults to (0, 1).
        :param tick_count: Initial :any:`tick_count`.
        :param on_change: Initial :any:`on_change` handler.
        :param on_press: Initial :any:`on_press` handler.
        :param on_release: Initial :any:`on_release` handler.
        :param enabled: Whether the user can interact with the widget.
        """
        super().__init__(id=id, style=style)

        # Needed for _impl initialization
        self._on_change = None

        self._impl = self.factory.Slider(interface=self)
        self.range = range
        self.tick_count = tick_count
        if value is None:
            value = (self.min + self.max) / 2
        self.value = value

        self.on_change = on_change
        self.enabled = enabled
        self.on_press = on_press
        self.on_release = on_release

    _MIN_WIDTH = 100

    # Backends are inconsistent about when they produce events for programmatic changes,
    # so we deal with those in the interface layer.
    @contextmanager
    def _suppress_change(self):
        on_change = self._on_change
        self._on_change = None
        yield
        self._on_change = on_change

    @property
    def value(self) -> float:
        """Current value.

        If the slider is discrete, setting the value will round it to the nearest tick.

        :raises ValueError: If set to a value which is outside of the :any:`range`.
        """
        return self._impl.get_value()

    @value.setter
    def value(self, value):
        if not (self.min <= value <= self.max):
            raise ValueError(f"value {value} is not in range {self.min} - {self.max}")
        old_value = self.value

        step = self.tick_step
        if step is not None:
            value = self.min + round((value - self.min) / step) * step

        with self._suppress_change():
            self._impl.set_value(float(value))
        if self.on_change and (value != old_value):
            self.on_change(self)

    @property
    def range(self) -> Tuple[float]:
        """Range of allowed values, in the form (min, max).

        If a range is set which doesn't include the current value, the value will be
        changed to the min or the max, whichever is closest.

        :raises ValueError: If the min is not strictly less than the max.
        """
        return self._impl.get_range()

    @range.setter
    def range(self, range):
        _min, _max = range
        if _min >= _max:
            raise ValueError(f"min value {_min} is not smaller than max value {_max}")

        with self._suppress_change():
            self._impl.set_range((float(_min), float(_max)))

            # Clip the value within the new range.
            old_value = self.value
            self.value = max(_min, min(_max, old_value))

        if self.on_change and (self.value != old_value):
            self.on_change(self)

    @property
    def min(self) -> float:
        """Minimum allowed value.

        This property is read-only, and depends on the value of :any:`range`.
        """
        return self.range[0]

    @property
    def max(self) -> float:
        """Maximum allowed value.

        This property is read-only, and depends on the value of :any:`range`.
        """
        return self.range[1]

    @property
    def tick_count(self) -> Optional[int]:
        """Number of tick marks to display on the slider.

        * If this is ``None``, the slider will be continuous.
        * If this is an ``int``, the slider will be discrete, and will have the given
          number of possible values, equally spaced within the :any:`range`.

        Setting this property to an ``int`` will round the current value to the nearest
        tick.

        :raises ValueError: If set to a count which is not at least 2 (for the min and
            max).
        """
        return self._impl.get_tick_count()

    @tick_count.setter
    def tick_count(self, tick_count):
        if (tick_count is not None) and (tick_count < 2):
            raise ValueError("tick count must be at least 2")
        old_value = self.value
        with self._suppress_change():
            self._impl.set_tick_count(tick_count)
        self.value = old_value  # Round if necessary.

    @property
    def tick_step(self) -> float:
        """Step between adjacent ticks.

        * If the slider is continous, this property returns ``None``
        * If the slider is discrete, it returns the difference in value between adjacent
          ticks.

        This property is read-only, and depends on the values of :any:`tick_count` and
        :any:`range`.
        """
        if self.tick_count is None:
            return None
        return (self.max - self.min) / (self.tick_count - 1)

    @property
    def tick_value(self) -> Optional[int]:
        """Value of the slider, measured in ticks.

        * If the slider is continuous, this property returns ``None``.
        * If the slider is discrete, it returns an integer between 1 (representing
          :any:`min`) and :any:`tick_count` (representing :any:`max`).

        :raises ValueError: If set to anything inconsistent with the rules above.
        """
        if self.tick_count is not None:
            return round((self.value - self.min) / self.tick_step) + 1
        else:
            return None

    @tick_value.setter
    def tick_value(self, tick_value):
        if self.tick_count is None:
            if tick_value is not None:
                raise ValueError("cannot set tick value when tick count is None")
        else:
            if tick_value is None:
                raise ValueError(
                    "cannot set tick value to None when tick count is not None"
                )
            self.value = self.min + (tick_value - 1) * self.tick_step

    @property
    def on_change(self) -> callable:
        """Handler to invoke when the value of the slider is changed, either by the user
        or programmatically.

        Setting the widget to its existing value will not call the handler.
        """
        return self._on_change

    @on_change.setter
    def on_change(self, handler):
        self._on_change = wrapped_handler(self, handler)
        self._impl.set_on_change(self._on_change)

    @property
    def on_press(self) -> callable:
        """Handler to invoke when when the user presses the slider before changing it."""
        return self._on_press

    @on_press.setter
    def on_press(self, handler):
        self._on_press = wrapped_handler(self, handler)
        self._impl.set_on_press(self._on_press)

    @property
    def on_release(self) -> callable:
        """Handler to invoke when the user releases the slider after changing it."""
        return self._on_release

    @on_release.setter
    def on_release(self, handler):
        self._on_release = wrapped_handler(self, handler)
        self._impl.set_on_release(self._on_release)
