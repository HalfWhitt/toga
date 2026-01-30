from __future__ import annotations

import warnings
from contextlib import AbstractContextManager as ContextManager
from dataclasses import dataclass, field
from math import pi
from typing import TYPE_CHECKING, Any

from toga.constants import Baseline, FillRule
from toga.fonts import Font
from toga.images import Image

from .drawingaction import (
    Arc,
    BeginPath,
    BezierCurveTo,
    DrawImage,
    DrawingAction,
    Ellipse,
    LineTo,
    MoveTo,
    QuadraticCurveTo,
    Rect,
    ResetTransform,
    Rotate,
    Scale,
    Translate,
    WriteText,
    color_property,
)

if TYPE_CHECKING:
    from toga.colors import ColorT

    from .canvas import Canvas


# Make sure deprecation warnings are shown by default
warnings.filterwarnings("default", category=DeprecationWarning)


class DrawingActionDispatch:
    @property
    def _action_target(self):
        """The State that should receive the drawing actions."""
        raise NotImplementedError()

    ###########################################################################
    # Path manipulation
    ###########################################################################

    def begin_path(self) -> BeginPath:
        """Start a new path in the canvas state.

        :returns: The `BeginPath`
            [`DrawingAction`][toga.widgets.canvas.DrawingAction] for the operation.
        """
        begin_path = BeginPath()
        self._action_target.append(begin_path)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            self.redraw()
        return begin_path

    def close_path(self, x: float | None = None, y: float | None = None) -> ClosePath:
        """Close the current path in the canvas state.

        This closes the current path as a simple drawing operation. It should be paired
        with a [`begin_path()`][toga.widgets.canvas.State.begin_path] operation; or,
        to complete a complete closed path, use the
        [`ClosedPath()`][toga.widgets.canvas.State.ClosedPath] context manager.

        :returns: The `ClosePath`
            [`DrawingAction`][toga.widgets.canvas.DrawingAction] for the operation.
        """
        close_path = ClosePath(x=x, y=y)
        self._action_target.append(close_path)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            self.redraw()
        return close_path

    def move_to(self, x: float, y: float) -> MoveTo:
        """Moves the current point of the canvas state without drawing.

        :param x: The x coordinate of the new current point.
        :param y: The y coordinate of the new current point.
        :returns: The `MoveTo` [`DrawingAction`][toga.widgets.canvas.DrawingAction]
            for the operation.
        """
        move_to = MoveTo(x, y)
        self._action_target.append(move_to)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            self.redraw()
        return move_to

    def line_to(self, x: float, y: float) -> LineTo:
        """Draw a line segment ending at a point in the canvas state.

        :param x: The x coordinate for the end point of the line segment.
        :param y: The y coordinate for the end point of the line segment.
        :returns: The `LineTo` [`DrawingAction`][toga.widgets.canvas.DrawingAction]
            for the operation.
        """
        line_to = LineTo(x, y)
        self._action_target.append(line_to)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            self.redraw()
        return line_to

    def bezier_curve_to(
        self,
        cp1x: float,
        cp1y: float,
        cp2x: float,
        cp2y: float,
        x: float,
        y: float,
    ) -> BezierCurveTo:
        """Draw a Bézier curve in the canvas state.

        A Bézier curve requires three points. The first two are control points; the
        third is the end point for the curve. The starting point is the last point in
        the current path, which can be changed using `move_to()` before creating the
        Bézier curve.

        :param cp1y: The y coordinate for the first control point of the Bézier curve.
        :param cp1x: The x coordinate for the first control point of the Bézier curve.
        :param cp2x: The x coordinate for the second control point of the Bézier curve.
        :param cp2y: The y coordinate for the second control point of the Bézier curve.
        :param x: The x coordinate for the end point.
        :param y: The y coordinate for the end point.
        :returns: The `BezierCurveTo`
            [`DrawingAction`][toga.widgets.canvas.DrawingAction] for the operation.
        """
        bezier_curve_to = BezierCurveTo(cp1x, cp1y, cp2x, cp2y, x, y)
        self._action_target.append(bezier_curve_to)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            self.redraw()
        return bezier_curve_to

    def quadratic_curve_to(
        self,
        cpx: float,
        cpy: float,
        x: float,
        y: float,
    ) -> QuadraticCurveTo:
        """Draw a quadratic curve in the canvas state.

        A quadratic curve requires two points. The first point is a control point; the
        second is the end point. The starting point of the curve is the last point in
        the current path, which can be changed using `moveTo()` before creating the
        quadratic curve.

        :param cpx: The x axis of the coordinate for the control point of the quadratic
            curve.
        :param cpy: The y axis of the coordinate for the control point of the quadratic
            curve.
        :param x: The x axis of the coordinate for the end point.
        :param y: The y axis of the coordinate for the end point.
        :returns: The `QuadraticCurveTo`
            [`DrawingAction`][toga.widgets.canvas.DrawingAction] for the operation.
        """
        quadratic_curve_to = QuadraticCurveTo(cpx, cpy, x, y)
        self._action_target.append(quadratic_curve_to)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            self.redraw()
        return quadratic_curve_to

    def arc(
        self,
        x: float,
        y: float,
        radius: float,
        startangle: float = 0.0,
        endangle: float = 2 * pi,
        counterclockwise: bool | None = None,
        anticlockwise: bool | None = None,  # DEPRECATED
    ) -> Arc:
        """Draw a circular arc in the canvas state.

        A full circle will be drawn by default; an arc can be drawn by specifying a
        start and end angle.

        :param x: The X coordinate of the circle's center.
        :param y: The Y coordinate of the circle's center.
        :param startangle: The start angle in radians, measured clockwise from the
            positive X axis.
        :param endangle: The end angle in radians, measured clockwise from the positive
            X axis.
        :param counterclockwise: If true, the arc is swept counterclockwise. The default
            is clockwise.
        :param anticlockwise: **DEPRECATED** - Use `counterclockwise`.
        :returns: The `Arc` [`DrawingAction`][toga.widgets.canvas.DrawingAction]
            for the operation.
        """
        arc = Arc(x, y, radius, startangle, endangle, counterclockwise, anticlockwise)
        self._action_target.append(arc)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            self.redraw()
        return arc

    def ellipse(
        self,
        x: float,
        y: float,
        radiusx: float,
        radiusy: float,
        rotation: float = 0.0,
        startangle: float = 0.0,
        endangle: float = 2 * pi,
        counterclockwise: bool | None = None,
        anticlockwise: bool | None = None,  # DEPRECATED
    ) -> Ellipse:
        """Draw an elliptical arc in the canvas state.

        A full ellipse will be drawn by default; an arc can be drawn by specifying a
        start and end angle.

        :param x: The X coordinate of the ellipse's center.
        :param y: The Y coordinate of the ellipse's center.
        :param radiusx: The ellipse's horizontal axis radius.
        :param radiusy: The ellipse's vertical axis radius.
        :param rotation: The ellipse's rotation in radians, measured clockwise around
            its center.
        :param startangle: The start angle in radians, measured clockwise from the
            positive X axis.
        :param endangle: The end angle in radians, measured clockwise from the positive
            X axis.
        :param counterclockwise: If true, the arc is swept counterclockwise. The default
            is clockwise.
        :param anticlockwise: **DEPRECATED** - Use `counterclockwise`.
        :returns: The `Ellipse` [`DrawingAction`][toga.widgets.canvas.DrawingAction]
            for the operation.
        """
        ellipse = Ellipse(
            x,
            y,
            radiusx,
            radiusy,
            rotation,
            startangle,
            endangle,
            counterclockwise,
            anticlockwise,
        )
        self._action_target.append(ellipse)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            self.redraw()
        return ellipse

    def rect(self, x: float, y: float, width: float, height: float) -> Rect:
        """Draw a rectangle in the canvas state.

        :param x: The horizontal coordinate of the left of the rectangle.
        :param y: The vertical coordinate of the top of the rectangle.
        :param width: The width of the rectangle.
        :param height: The height of the rectangle.
        :returns: The `Rect` [`DrawingAction`][toga.widgets.canvas.DrawingAction]
            for the operation.
        """
        rect = Rect(x, y, width, height)
        self._action_target.append(rect)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            self.redraw()
        return rect

    def fill(
        self,
        color: ColorT | None = None,
        fill_rule: FillRule = FillRule.NONZERO,
        x: float | None = None,
        y: float | None = None,
    ) -> Fill:
        """Fill the current path.

        The fill can use either the
        [Non-Zero](https://en.wikipedia.org/wiki/Nonzero-rule) or
        [Even-Odd](https://en.wikipedia.org/wiki/Even-odd_rule) winding
        rule for filling paths.

        :param fill_rule: `nonzero` is the non-zero winding rule; `evenodd` is the
            even-odd winding rule.
        :param color: The fill color.
        :returns: The `Fill` [`DrawingAction`][toga.widgets.canvas.DrawingAction]
            for the operation.
        """
        fill = Fill(color, fill_rule, x, y)
        self._action_target.append(fill)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            self.redraw()
        return fill

    def stroke(
        self,
        color: ColorT | None = None,
        line_width: float | None = None,
        line_dash: list[float] | None = None,
        x: float | None = None,
        y: float | None = None,
    ) -> Stroke:
        """Draw the current path as a stroke.

        :param color: The color for the stroke.
        :param line_width: The width of the stroke.
        :param line_dash: The dash pattern to follow when drawing the line, expressed as
            alternating lengths of dashes and spaces. The default is a solid line.
        :returns: The `Stroke` [`DrawingAction`][toga.widgets.canvas.DrawingAction]
            for the operation.
        """
        stroke = Stroke(color, line_width, line_dash, x, y)
        self._action_target.append(stroke)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            self.redraw()
        return stroke

    ###########################################################################
    # Text drawing
    ###########################################################################

    def write_text(
        self,
        text: str,
        x: float = 0.0,
        y: float = 0.0,
        font: Font | None = None,
        baseline: Baseline = Baseline.ALPHABETIC,
        line_height: float | None = None,
    ) -> WriteText:
        """Write text at a given position in the canvas state.

        Drawing text is effectively a series of path operations, so the text will have
        the color and fill properties of the canvas state.

        :param text: The text to draw. Newlines will cause line breaks, but long lines
            will not be wrapped.
        :param x: The X coordinate of the text's left edge.
        :param y: The Y coordinate: its meaning depends on `baseline`.
        :param font: The font in which to draw the text. The default is the system font.
        :param baseline: Alignment of text relative to the Y coordinate.
        :param line_height: Height of the line box as a multiple of the font size
            when multiple lines are present.
        :returns: The `WriteText` [`DrawingAction`][toga.widgets.canvas.DrawingAction]
            for the operation.
        """
        write_text = WriteText(text, x, y, font, baseline, line_height)
        self._action_target.append(write_text)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            self.redraw()
        return write_text

    ###########################################################################
    # Bitmap drawing
    ###########################################################################

    def draw_image(
        self,
        image: Image,
        x: float = 0.0,
        y: float = 0.0,
        width: float | None = None,
        height: float | None = None,
    ):
        """Draw a Toga Image in the canvas state.

        The x, y coordinates specify the location of the bottom-left corner
        of the image. If supplied, the width and height specify the size
        of the image when it is rendered in the state, the image will be
        scaled to fit.

        Drawing of images is performed with the current transformation matrix
        applied, so the destination rectangle of the image will be rotated,
        scaled and translated by any transformations which are currently applied.

        :param image: a Toga Image
        :param x: The x-coordinate of the bottom-left corner of the image when
            it is drawn.
        :param y: The y-coordinate of the bottom-left corner of the image when
            it is drawn.
        :param width: The width of the destination rectangle where the image
            will be drawn. The image will be scaled to fit the width. If the
            width is omitted, the natural width of the image will be used and
            no scaling will be done.
        :param height: The height of the destination rectangle where the image
            will be drawn. The image will be scaled to fit the height. If the
            height is omitted, the natural height of the image will be used and
            no scaling will be done.
        """
        draw_image = DrawImage(image, x, y, width, height)
        self._action_target.append(draw_image)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            self.redraw()
        return draw_image

    ###########################################################################
    # Transformations
    ###########################################################################
    def rotate(self, radians: float) -> Rotate:
        """Add a rotation to the canvas state.

        :param radians: The angle to rotate clockwise in radians.
        :returns: The `Rotate` [`DrawingAction`][toga.widgets.canvas.DrawingAction]
            for the transformation.
        """
        rotate = Rotate(radians)
        self._action_target.append(rotate)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            self.redraw()
        return rotate

    def scale(self, sx: float, sy: float) -> Scale:
        """Add a scaling transformation to the canvas state.

        :param sx: Scale factor for the X dimension. A negative value flips the
            image horizontally.
        :param sy: Scale factor for the Y dimension. A negative value flips the
            image vertically.
        :returns: The `Scale` [`DrawingAction`][toga.widgets.canvas.DrawingAction]
            for the transformation.
        """
        scale = Scale(sx, sy)
        self._action_target.append(scale)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            self.redraw()
        return scale

    def translate(self, tx: float, ty: float) -> Translate:
        """Add a translation to the canvas state.

        :param tx: Translation for the X dimension.
        :param ty: Translation for the Y dimension.
        :returns: The `Translate` [`DrawingAction`][toga.widgets.canvas.DrawingAction]
            for the transformation.
        """
        translate = Translate(tx, ty)
        self._action_target.append(translate)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            self.redraw()
        return translate

    def reset_transform(self) -> ResetTransform:
        """Reset all transformations in the canvas state.

        :returns: A `ResetTransform`
            [`DrawingAction`][toga.widgets.canvas.DrawingAction].
        """
        reset_transform = ResetTransform()
        self._action_target.append(reset_transform)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            self.redraw()
        return reset_transform

    ###########################################################################
    # Sub-states of this state
    ###########################################################################

    def state(self) -> ContextManager[State]:
        """Construct and yield a new sub-[`State`][toga.widgets.canvas.State] within
        this state.

        :return: Yields the new [`State`][toga.widgets.canvas.State] object.
        """
        state = State()
        self._action_target.append(state)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            self.redraw()
        return state

    ######################################################################
    # 2026-01: Backwards compatibility for <= 0.5.3
    ######################################################################

    # Each of these CamelCase methods, when called on a State, added to that State.
    # However, when called on a Canvas, they added to that Canvas's root_state.

    def Context(self) -> ContextManager[State]:
        warnings.warn(
            "The Context() drawing emthod has been renamed to state()",
            DeprecationWarning,
            stacklevel=2,
        )
        target = self if isinstance(self, State) else self.root_state

        return target.state()

    def ClosedPath(
        self,
        x: float | None = None,
        y: float | None = None,
    ) -> ContextManager(ClosePath):
        warnings.warn(
            (
                "The ClosedPath() drawing method has been renamed to close_path(). Its "
                "parameters (x and y) are also now keyword-only."
            ),
            DeprecationWarning,
            stacklevel=2,
        )
        target = self if isinstance(self, State) else self.root_state

        return target.close_path(x=x, y=y)

    def Fill(
        self,
        x: float | None = None,
        y: float | None = None,
        color: ColorT | None = None,
        fill_rule: FillRule = FillRule.NONZERO,
    ) -> ContextManager[Fill]:
        warnings.warn(
            (
                "The Fill() drawing method has been renamed to close_fill(). It now "
                "accepts fill_rule as its only positional parameter; color, x, and y "
                "are now keyword-only."
            ),
            DeprecationWarning,
            stacklevel=2,
        )
        target = self if isinstance(self, State) else self.root_state

        return target.close_path(fill_rule=fill_rule, color=color, x=x, y=y)

    def Stroke(
        self,
        x: float | None = None,
        y: float | None = None,
        color: ColorT | None = None,
        line_width: float | None = None,
        line_dash: list[float] | None = None,
    ) -> ContextManager[Stroke]:
        warnings.warn(
            (
                "The Stroke() drawing method has been renamed to stroke(). Its "
                "parameters (color, line_width, line_dash, x, and y) are also now "
                "keyword-only."
            ),
            DeprecationWarning,
            stacklevel=2,
        )
        target = self if isinstance(self, State) else self.root_state

        return target.close_path(
            color=color,
            line_width=line_width,
            line_dash=line_dash,
            x=x,
            y=y,
        )

    ######################################################################
    # End Backwards compatibility
    ######################################################################


class State(DrawingAction, DrawingActionDispatch):
    """A drawing state for a canvas.

    You should not create a [`State`][toga.widgets.canvas.State] directly; instead,
    you should use the [`state()`][toga.widgets.canvas.State.state] method on an
    existing state, or use [`Canvas.root_state`][toga.Canvas.root_state] to access the
    root state of the canvas.
    """

    def __init__(self):
        self.drawing_actions: list[DrawingAction] = []

    def _draw(self, context: Any) -> None:
        context.save()
        for action in self.drawing_actions:
            action._draw(context)
        context.restore()

    @property
    def _action_target(self):
        # State itself holds its drawing actions.
        return self

    def __enter__(self):
        self._is_open = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._is_open = False
        # Don't suppress any exceptions
        return False

    ######################################################################
    # 2026-1: Backwards compatibility for Toga <= 0.5.3
    ######################################################################

    @property
    def canvas(self) -> Canvas:
        warnings.warn(
            "State objects no longer hold a reference to their canvas.",
            DeprecationWarning,
            stacklevel=2,
        )

        from .canvas import Canvas

        # Get the first that matches.
        for ref in Canvas._instances:
            if canvas := ref():
                if self is canvas.root_state or self in canvas.root_state:
                    return canvas

    def redraw(self) -> None:
        warnings.warn(
            (
                "State.redraw() is deprecated. Call the canvas's redraw() method "
                "instead."
            ),
            DeprecationWarning,
            stacklevel=2,
        )

        from .canvas import Canvas

        # Redraw any canvases that contain self; could be multiple.
        for ref in Canvas._instances:
            if canvas := ref():
                if self is canvas.root_state or self in canvas.root_state:
                    canvas.redraw()

    ######################################################################
    # End backwards compatibility
    ######################################################################

    ###########################################################################
    # Operations on drawing objects
    ###########################################################################

    def __len__(self) -> int:
        """Returns the number of drawing objects that are in this state."""
        return len(self.drawing_actions)

    def __getitem__(self, index: int) -> DrawingAction:
        """Returns the drawing object at the given index."""
        return self.drawing_actions[index]

    def append(self, obj: DrawingAction) -> None:
        """Append a drawing object to the state.

        :param obj: The drawing object to add to the state.
        """
        self.drawing_actions.append(obj)

    def insert(self, index: int, obj: DrawingAction) -> None:
        """Insert a drawing object into the state at a specific index.

        :param index: The index at which the drawing object should be inserted.
        :param obj: The drawing object to add to the state.
        """
        self.drawing_actions.insert(index, obj)

    def remove(self, obj: DrawingAction) -> None:
        """Remove a drawing object from the state.

        :param obj: The drawing object to remove.
        """
        self.drawing_actions.remove(obj)

    def clear(self) -> None:
        """Remove all drawing objects from the state."""
        self.drawing_actions.clear()


@dataclass(repr=False)
class ClosePath(State):
    x: float | None = field(default=None, kw_only=True)
    y: float | None = field(default=None, kw_only=True)

    def __post_init__(self):
        super().__init__()

    def _draw(self, context: Any) -> None:
        if not hasattr(self, "_is_open"):
            context.close_path()
            return

        context.save()

        context.begin_path()
        if self.x is not None and self.y is not None:
            context.move_to(x=self.x, y=self.y)

        for action in self.drawing_actions:
            action._draw(context)

        context.close_path()
        context.restore()


@dataclass(repr=False)
class Fill(State):
    color: ColorT | None = color_property()
    fill_rule: FillRule = FillRule.NONZERO
    x: float | None = None
    y: float | None = None

    def __post_init__(self):
        super().__init__()

    def _draw(self, context: Any) -> None:
        if not hasattr(self, "_is_open"):
            context.save()
            if self.color is not None:
                context.set_fill_style(self.color)
            context.fill(self.fill_rule)
            context.restore()
            return

        context.save()

        context.in_fill = True  # Backwards compatibility for Toga <= 0.5.3
        if self.color:
            context.set_fill_style(self.color)

        context.begin_path()
        if self.x is not None and self.y is not None:
            context.move_to(x=self.x, y=self.y)

        for action in self.drawing_actions:
            action._draw(context)

        context.fill(self.fill_rule)
        context.in_fill = False  # Backwards compatibility for Toga <= 0.5.3

        context.restore()


@dataclass(repr=False)
class Stroke(State):
    color: ColorT | None = color_property()
    line_width: float | None = None
    line_dash: list[float] | None = None
    x: float | None = None
    y: float | None = None

    def __post_init__(self):
        super().__init__()

    def _draw(self, context: Any) -> None:
        if not hasattr(self, "_is_open"):
            context.save()
            if self.color is not None:
                context.set_stroke_style(self.color)
            if self.line_width is not None:
                context.set_line_width(self.line_width)
            if self.line_dash is not None:
                context.set_line_dash(self.line_dash)
            context.stroke()
            context.restore()
            return

        context.save()
        context.in_stroke = True  # Backwards compatibility for Toga <= 0.5.3
        if self.color is not None:
            context.set_stroke_style(self.color)
        if self.line_width is not None:
            context.set_line_width(self.line_width)
        if self.line_dash is not None:
            context.set_line_dash(self.line_dash)
        context.begin_path()

        if self.x is not None and self.y is not None:
            context.move_to(x=self.x, y=self.y)

        for action in self.drawing_actions:
            action._draw(context)

        context.stroke()

        context.in_stroke = False  # Backwards compatibility for Toga <= 0.5.3
        context.restore()
