from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import InitVar, dataclass
from math import pi
from typing import TYPE_CHECKING, Any
from warnings import filterwarnings, warn

from toga.colors import BLACK, Color
from toga.constants import Baseline, FillRule
from toga.fonts import (
    SYSTEM,
    SYSTEM_DEFAULT_FONT_SIZE,
    Font,
)
from toga.images import Image

if TYPE_CHECKING:
    from toga.colors import ColorT

# Make sure deprecation warnings are shown by default
filterwarnings("default", category=DeprecationWarning)

######################################################################
# 03-2025: Backwards compatibility for Toga <= 0.5.1
######################################################################


def _determine_counterclockwise(anticlockwise, counterclockwise):
    num_supplied = sum(value is not None for value in [anticlockwise, counterclockwise])
    if num_supplied == 0:
        return False
    if num_supplied == 1:
        if anticlockwise is not None:
            warn(
                "Parameter 'anticlockwise' is deprecated. Use 'counterclockwise' "
                "instead.",
                DeprecationWarning,
                stacklevel=3,
            )
            return anticlockwise

        return counterclockwise

    raise TypeError("Received both 'anticlockwise' and 'counterclockwise' arguments")


######################################################################
# End backwards compatibility
######################################################################


class DrawingObject(ABC):
    """A drawing operation in a [`Context`][toga.widgets.canvas.Context].

    Every context drawing method creates a `DrawingObject`, adds it to the context,
    and returns it. Each argument passed to the method becomes a property of the
    `DrawingObject`, which can be modified as shown in the [Usage][] section.

    `DrawingObjects` can also be created manually, then added to a context using the
    [`append()`][toga.widgets.canvas.Context.append] or
    [`insert()`][toga.widgets.canvas.Context.append] methods. Their constructors take
    the same arguments as the corresponding [`Context`][toga.widgets.canvas.Context]
    method, and their classes have the same names, but capitalized:

    * [`toga.widgets.canvas.Arc`][toga.widgets.canvas.Context.arc]
    * [`toga.widgets.canvas.BeginPath`][toga.widgets.canvas.Context.begin_path]
    * [`toga.widgets.canvas.BezierCurveTo`][toga.widgets.canvas.Context.bezier_curve_to]
    * [`toga.widgets.canvas.ClosePath`][toga.widgets.canvas.Context.close_path]
    * [`toga.widgets.canvas.Ellipse`][toga.widgets.canvas.Context.ellipse]
    * [`toga.widgets.canvas.Fill`][toga.widgets.canvas.Context.fill]
    * [`toga.widgets.canvas.LineTo`][toga.widgets.canvas.Context.line_to]
    * [`toga.widgets.canvas.MoveTo`][toga.widgets.canvas.Context.move_to]
    * [`toga.widgets.canvas.QuadraticCurveTo`][toga.widgets.canvas.Context.quadratic_curve_to]
    * [`toga.widgets.canvas.Rect`][toga.widgets.canvas.Context.rect]
    * [`toga.widgets.canvas.ResetTransform`][toga.widgets.canvas.Context.reset_transform]
    * [`toga.widgets.canvas.Rotate`][toga.widgets.canvas.Context.rotate]
    * [`toga.widgets.canvas.Scale`][toga.widgets.canvas.Context.scale]
    * [`toga.widgets.canvas.Stroke`][toga.widgets.canvas.Context.stroke]
    * [`toga.widgets.canvas.Translate`][toga.widgets.canvas.Context.translate]
    * [`toga.widgets.canvas.WriteText`][toga.widgets.canvas.Context.write_text]
    """  # noqa: E501

    # Disable the line-too-long check as there is no way to properly render the list
    # above with any given list item on multiple lines; an undesired space is added if
    # the link content is split on two lines.

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    @abstractmethod
    def _draw(self, impl: Any, **kwargs: Any) -> None: ...


class validated_property:
    def __init__(self, default, validate=lambda x: x):
        self.default = default
        self.validate = validate

    def __set_name__(self, action_class, name):
        self.name = name

    def __get__(self, action, action_class=None):
        if action is None:
            return self

        return getattr(action, f"_{self.name}")

    def __set__(self, action, value):
        if value is self or value is None:
            value = self.default
        else:
            value = self.validate(value)

        setattr(action, f"_{self.name}", value)


class BeginPath(DrawingObject):
    def _draw(self, impl: Any, **kwargs: Any) -> None:
        impl.begin_path(**kwargs)


class ClosePath(DrawingObject):
    def _draw(self, impl: Any, **kwargs: Any) -> None:
        impl.close_path(**kwargs)


@dataclass
class Fill(DrawingObject):
    color: ColorT = validated_property(
        default=Color.parse(BLACK),
        validate=lambda x: Color.parse(x),
    )
    fill_rule: FillRule = FillRule.NONZERO

    def _draw(self, impl: Any, **kwargs: Any) -> None:
        impl.fill(self.color, self.fill_rule, **kwargs)


@dataclass
class Stroke(DrawingObject):
    color: ColorT = validated_property(
        default=Color.parse(BLACK),
        validate=lambda x: Color.parse(x),
    )
    line_width: float = 2.0
    line_dash: list[float] | None = None

    def _draw(self, impl: Any, **kwargs: Any) -> None:
        impl.stroke(self.color, self.line_width, self.line_dash, **kwargs)


@dataclass
class MoveTo(DrawingObject):
    x: float
    y: float

    def _draw(self, impl: Any, **kwargs: Any) -> None:
        impl.move_to(self.x, self.y, **kwargs)


@dataclass
class LineTo(DrawingObject):
    x: float
    y: float

    def _draw(self, impl: Any, **kwargs: Any) -> None:
        impl.line_to(self.x, self.y, **kwargs)


@dataclass
class BezierCurveTo(DrawingObject):
    cp1x: float
    cp1y: float
    cp2x: float
    cp2y: float
    x: float
    y: float

    def _draw(self, impl: Any, **kwargs: Any) -> None:
        impl.bezier_curve_to(
            self.cp1x, self.cp1y, self.cp2x, self.cp2y, self.x, self.y, **kwargs
        )


@dataclass
class QuadraticCurveTo(DrawingObject):
    cpx: float
    cpy: float
    x: float
    y: float

    def _draw(self, impl: Any, **kwargs: Any) -> None:
        impl.quadratic_curve_to(self.cpx, self.cpy, self.x, self.y, **kwargs)


@dataclass
class Arc(DrawingObject):
    x: float
    y: float
    radius: float
    startangle: float = 0.0
    endangle: float = 2 * pi
    counterclockwise: bool | None = None
    anticlockwise: InitVar[bool | None] = None  # DEPRECATED

    ######################################################################
    # 03-2025: Backwards compatibility for Toga <= 0.5.1
    ######################################################################

    def __post_init__(self, anticlockwise):
        print(f"{self.counterclockwise = }")
        print(f"{anticlockwise = }")
        self.counterclockwise = _determine_counterclockwise(
            anticlockwise, self.counterclockwise
        )

    ######################################################################
    # End backwards compatibility
    ######################################################################

    def _draw(self, impl: Any, **kwargs: Any) -> None:
        impl.arc(
            self.x,
            self.y,
            self.radius,
            self.startangle,
            self.endangle,
            self.counterclockwise,
            **kwargs,
        )


@dataclass
class Ellipse(DrawingObject):
    x: float
    y: float
    radiusx: float
    radiusy: float
    rotation: float = 0.0
    startangle: float = 0.0
    endangle: float = 2 * pi
    counterclockwise: bool | None = None
    anticlockwise: InitVar[bool | None] = None  # DEPRECATED

    ######################################################################
    # 03-2025: Backwards compatibility for Toga <= 0.5.1
    ######################################################################

    def __post_init__(self, anticlockwise):
        print(f"{self.counterclockwise = }")
        print(f"{anticlockwise = }")
        self.counterclockwise = _determine_counterclockwise(
            anticlockwise, self.counterclockwise
        )

    ######################################################################
    # End backwards compatibility
    ######################################################################

    def _draw(self, impl: Any, **kwargs: Any) -> None:
        impl.ellipse(
            self.x,
            self.y,
            self.radiusx,
            self.radiusy,
            self.rotation,
            self.startangle,
            self.endangle,
            self.counterclockwise,
            **kwargs,
        )


@dataclass
class Rect(DrawingObject):
    x: float
    y: float
    width: float
    height: float

    def _draw(self, impl: Any, **kwargs: Any) -> None:
        impl.rect(self.x, self.y, self.width, self.height, **kwargs)


@dataclass
class WriteText(DrawingObject):
    text: str
    x: float = 0.0
    y: float = 0.0
    font: Font | None = validated_property(
        default=Font(family=SYSTEM, size=SYSTEM_DEFAULT_FONT_SIZE)
    )
    baseline: Baseline = Baseline.ALPHABETIC
    line_height: float | None = None

    def _draw(self, impl: Any, **kwargs: Any) -> None:
        impl.write_text(
            str(self.text),
            self.x,
            self.y,
            self.font._impl,
            self.baseline,
            self.line_height,
            **kwargs,
        )


@dataclass
class DrawImage(DrawingObject):
    image: Image
    x: float = 0.0
    y: float = 0.0
    width: float | None = None
    height: float | None = None

    def _draw(self, impl: Any, **kwargs: Any) -> None:
        impl.draw_image(
            self.image,
            self.x,
            self.y,
            self.width if self.width is not None else self.image.width,
            self.height if self.height is not None else self.image.height,
            **kwargs,
        )


@dataclass
class Rotate(DrawingObject):
    radians: float

    def _draw(self, impl: Any, **kwargs: Any) -> None:
        impl.rotate(self.radians, **kwargs)


@dataclass
class Scale(DrawingObject):
    sx: float
    sy: float

    def _draw(self, impl: Any, **kwargs: Any) -> None:
        impl.scale(self.sx, self.sy, **kwargs)


@dataclass
class Translate(DrawingObject):
    tx: float
    ty: float

    def _draw(self, impl: Any, **kwargs: Any) -> None:
        impl.translate(self.tx, self.ty, **kwargs)


class ResetTransform(DrawingObject):
    def _draw(self, impl: Any, **kwargs: Any) -> None:
        impl.reset_transform(**kwargs)
