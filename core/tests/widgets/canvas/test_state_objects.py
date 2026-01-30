from contextlib import nullcontext

import pytest

from toga.colors import REBECCAPURPLE, rgb
from toga.constants import FillRule
from toga.widgets.canvas import (
    ClosePath,
    Fill,
    LineTo,
    Scale,
    State,
    Stroke,
)
from toga_dummy.utils import assert_action_performed

REBECCA_PURPLE_COLOR = rgb(102, 51, 153)


def test_sub_state(widget):
    """A state can produce a sub-state."""
    with widget.state() as sub_state:
        widget.line_to(30, 40)
    # A fresh state has been created as a sub-state of the canvas.
    assert isinstance(sub_state, State)
    assert sub_state is not widget.root_state

    assert_action_performed(widget, "redraw")
    assert repr(sub_state) == "State()"

    # The first and last instructions can be ignored; they're the root canvas state
    print(widget._impl.draw_instructions[1:-1])
    assert widget._impl.draw_instructions[1:-1] == [
        "save",
        ("line to", {"x": 30, "y": 40}),
        "restore",
    ]


@pytest.mark.parametrize(
    "kwargs, args_repr, has_move, properties",
    [
        # Defaults
        (
            {},
            "x=None, y=None",
            False,
            {"x": None, "y": None},
        ),
        # X only
        (
            {"x": 10},
            "x=10, y=None",
            False,
            {"x": 10, "y": None},
        ),
        # Y only
        (
            {"y": 20},
            "x=None, y=20",
            False,
            {"x": None, "y": 20},
        ),
        # X and Y
        (
            {"x": 10, "y": 20},
            "x=10, y=20",
            True,
            {"x": 10, "y": 20},
        ),
    ],
)
def test_closed_path(widget, kwargs, args_repr, has_move, properties):
    """A state can produce a ClosedPath sub-state."""
    with widget.close_path(**kwargs) as closed_path:
        widget.line_to(30, 40)

    # A fresh state has been created as a sub-state of the canvas.
    assert isinstance(closed_path, ClosePath)
    assert repr(closed_path) == f"ClosePath({args_repr})"

    assert_action_performed(widget, "redraw")

    # All the attributes can be retrieved.
    for attr, value in properties.items():
        assert getattr(closed_path, attr) == value

    # The first and last instructions can be ignored; they're the root canvas state
    assert widget._impl.draw_instructions[1:-1] == [
        "save",
        "begin path",
    ] + ([("move to", {"x": 10, "y": 20})] if has_move else []) + [
        ("line to", {"x": 30, "y": 40}),
        "close path",
        "restore",
    ]


@pytest.mark.parametrize(
    "kwargs, args_repr, has_move, properties",
    [
        # Defaults
        (
            {},
            "color=None, fill_rule=FillRule.NONZERO, x=None, y=None",
            False,
            {
                "color": None,
                "fill_rule": FillRule.NONZERO,
                "x": None,
                "y": None,
            },
        ),
        # X only
        (
            {"x": 10},
            "color=None, fill_rule=FillRule.NONZERO, x=10, y=None",
            False,
            {
                "color": None,
                "fill_rule": FillRule.NONZERO,
                "x": 10,
                "y": None,
            },
        ),
        # Y only
        (
            {"y": 20},
            "color=None, fill_rule=FillRule.NONZERO, x=None, y=20",
            False,
            {"color": None, "fill_rule": FillRule.NONZERO, "x": None, "y": 20},
        ),
        # X and Y
        (
            {"x": 10, "y": 20},
            "color=None, fill_rule=FillRule.NONZERO, x=10, y=20",
            True,
            {"color": None, "fill_rule": FillRule.NONZERO, "x": 10, "y": 20},
        ),
        # Color
        (
            {"color": REBECCAPURPLE},
            (
                f"color={REBECCA_PURPLE_COLOR!r}, "
                "fill_rule=FillRule.NONZERO, x=None, y=None"
            ),
            False,
            {
                "color": REBECCA_PURPLE_COLOR,
                "fill_rule": FillRule.NONZERO,
                "x": None,
                "y": None,
            },
        ),
        # Explicitly don't set color
        (
            {"color": None},
            "color=None, fill_rule=FillRule.NONZERO, x=None, y=None",
            False,
            {
                "color": None,
                "fill_rule": FillRule.NONZERO,
                "x": None,
                "y": None,
            },
        ),
        # Fill Rule
        (
            {"fill_rule": FillRule.EVENODD, "x": None, "y": None},
            "color=None, fill_rule=FillRule.EVENODD, x=None, y=None",
            False,
            {
                "color": None,
                "fill_rule": FillRule.EVENODD,
                "x": None,
                "y": None,
            },
        ),
        # All args
        (
            {"color": REBECCAPURPLE, "fill_rule": FillRule.EVENODD, "x": 10, "y": 20},
            f"color={REBECCA_PURPLE_COLOR!r}, fill_rule=FillRule.EVENODD, x=10, y=20",
            True,
            {
                "color": REBECCA_PURPLE_COLOR,
                "fill_rule": FillRule.EVENODD,
                "x": 10,
                "y": 20,
            },
        ),
    ],
)
def test_fill(widget, kwargs, args_repr, has_move, properties):
    """A state can produce a Fill sub-state."""
    with widget.fill(**kwargs) as fill:
        widget.line_to(30, 40)

    # A fresh state has been created as a sub-state of the canvas.
    assert isinstance(fill, Fill)
    assert repr(fill) == f"Fill({args_repr})"

    # All the attributes can be retrieved.
    for attr, value in properties.items():
        assert getattr(fill, attr) == value

    # The first and last instructions can be ignored; they're the root canvas state
    commands = [
        "save",
        ("set fill style", color)
        if (color := properties["color"]) is not None
        else None,
        "begin path",
        ("move to", {"x": properties["x"], "y": properties["y"]}) if has_move else None,
        ("line to", {"x": 30, "y": 40}),
        ("fill", {"fill_rule": properties["fill_rule"]}),
        "restore",
    ]

    assert widget._impl.draw_instructions[1:-1] == [
        command for command in commands if command is not None
    ]


@pytest.mark.parametrize(
    "kwargs, args_repr, has_move, properties",
    [
        # Defaults
        (
            {},
            "color=None, line_width=None, line_dash=None, x=None, y=None",
            False,
            {
                "color": None,
                "line_width": None,
                "line_dash": None,
                "x": None,
                "y": None,
            },
        ),
        # X only
        (
            {"x": 10},
            "color=None, line_width=None, line_dash=None, x=10, y=None",
            False,
            {
                "color": None,
                "line_width": None,
                "line_dash": None,
                "x": 10,
                "y": None,
            },
        ),
        # Y only
        (
            {"y": 20},
            "color=None, line_width=None, line_dash=None, x=None, y=20",
            False,
            {
                "color": None,
                "line_width": None,
                "line_dash": None,
                "x": None,
                "y": 20,
            },
        ),
        # X and Y
        (
            {"x": 10, "y": 20},
            "color=None, line_width=None, line_dash=None, x=10, y=20",
            True,
            {
                "color": None,
                "line_width": None,
                "line_dash": None,
                "x": 10,
                "y": 20,
            },
        ),
        # Color
        (
            {"color": REBECCAPURPLE},
            (
                f"color={REBECCA_PURPLE_COLOR!r}, "
                f"line_width=None, line_dash=None, x=None, y=None"
            ),
            False,
            {
                "color": REBECCA_PURPLE_COLOR,
                "line_width": None,
                "line_dash": None,
                "x": None,
                "y": None,
            },
        ),
        # Explicitly don't set color
        (
            {"color": None},
            "color=None, line_width=None, line_dash=None, x=None, y=None",
            False,
            {
                "color": None,
                "line_width": None,
                "line_dash": None,
                "x": None,
                "y": None,
            },
        ),
        # Line width
        (
            {"line_width": 4.5, "x": None, "y": None},
            "color=None, line_width=4.500, line_dash=None, x=None, y=None",
            False,
            {
                "color": None,
                "line_width": 4.5,
                "line_dash": None,
                "x": None,
                "y": None,
            },
        ),
        # Line dash
        (
            {
                "line_dash": [2, 7],
                "x": None,
                "y": None,
            },
            "color=None, line_width=None, line_dash=[2, 7], x=None, y=None",
            False,
            {
                "color": None,
                "line_width": None,
                "line_dash": [2, 7],
                "x": None,
                "y": None,
            },
        ),
        # All args
        (
            {
                "color": REBECCAPURPLE,
                "line_width": 4.5,
                "line_dash": [2, 7],
                "x": 10,
                "y": 20,
            },
            (
                f"color={REBECCA_PURPLE_COLOR!r}, "
                f"line_width=4.500, line_dash=[2, 7], x=10, y=20"
            ),
            True,
            {
                "color": REBECCA_PURPLE_COLOR,
                "line_width": 4.5,
                "line_dash": [2, 7],
                "x": 10,
                "y": 20,
            },
        ),
    ],
)
def test_stroke(widget, kwargs, args_repr, has_move, properties):
    """A state can produce a Stroke sub-state."""
    with widget.stroke(**kwargs) as stroke:
        widget.line_to(30, 40)

    # A fresh state has been created as a sub-state of the canvas.
    assert isinstance(stroke, Stroke)
    assert repr(stroke) == f"Stroke({args_repr})"

    # All the attributes can be retrieved.
    for attr, value in properties.items():
        assert getattr(stroke, attr) == value

    commands = [
        "save",
        ("set stroke style", color)
        if (color := properties["color"]) is not None
        else None,
        ("set line width", line_width)
        if (line_width := properties["line_width"]) is not None
        else None,
        ("set line dash", line_dash)
        if (line_dash := properties["line_dash"]) is not None
        else None,
        "begin path",
        ("move to", {"x": properties["x"], "y": properties["y"]}) if has_move else None,
        ("line to", {"x": 30, "y": 40}),
        "stroke",
        "restore",
    ]

    # The first and last instructions can be ignored; they're the root canvas state
    assert widget._impl.draw_instructions[1:-1] == [
        command for command in commands if command is not None
    ]


def test_order_change(widget):
    """The order of state objects can be changed."""
    # Initially nothing on the state.
    assert len(widget.root_state) == 0

    # Set up an inner state that has contained operations, including a sub-state
    widget.line_to(0, 0)
    with widget.state() as state:
        widget.line_to(10, 20)
        second = widget.line_to(20, 30)
        with widget.fill() as fill:
            widget.line_to(25, 25)
        widget.line_to(30, 40)
        widget.line_to(40, 50)
    widget.line_to(99, 99)

    # Counts are as expected
    assert len(widget.root_state) == 3
    assert len(state) == 5
    assert len(fill) == 1

    # Initial draw instructions are as expected
    assert widget._impl.draw_instructions == [
        "save",
        ("line to", {"x": 0, "y": 0}),
        "save",
        ("line to", {"x": 10, "y": 20}),
        ("line to", {"x": 20, "y": 30}),
        # Begin fill
        "save",
        "begin path",
        ("line to", {"x": 25, "y": 25}),
        ("fill", {"fill_rule": FillRule.NONZERO}),
        "restore",
        # End fill
        ("line to", {"x": 30, "y": 40}),
        ("line to", {"x": 40, "y": 50}),
        "restore",
        ("line to", {"x": 99, "y": 99}),
        "restore",
    ]

    # Remove the second draw instruction
    state.remove(second)
    widget.redraw()

    # Drawing objects are as expected
    assert len(widget.root_state) == 3
    for i, cls in enumerate([LineTo, State, LineTo]):
        assert isinstance(widget.root_state[i], cls)
    with pytest.raises(IndexError):
        widget.root_state[3]

    assert len(state) == 4
    assert len(fill) == 1

    # Draw instructions no longer have the second
    from pprint import pprint

    pprint(widget._impl.draw_instructions)
    assert widget._impl.draw_instructions == [
        "save",
        ("line to", {"x": 0, "y": 0}),
        "save",
        ("line to", {"x": 10, "y": 20}),
        # Begin fill
        "save",
        "begin path",
        ("line to", {"x": 25, "y": 25}),
        ("fill", {"fill_rule": FillRule.NONZERO}),
        "restore",
        # End fill
        ("line to", {"x": 30, "y": 40}),
        ("line to", {"x": 40, "y": 50}),
        "restore",
        ("line to", {"x": 99, "y": 99}),
        "restore",
    ]

    # Insert the second draw instruction at index 3
    state.insert(3, second)
    widget.redraw()

    # Counts are as expected
    assert len(widget.root_state) == 3
    assert len(state) == 5
    assert len(fill) == 1

    # Draw instructions show the new position
    assert widget._impl.draw_instructions == [
        "save",
        ("line to", {"x": 0, "y": 0}),
        "save",
        ("line to", {"x": 10, "y": 20}),
        # Begin fill
        "save",
        "begin path",
        ("line to", {"x": 25, "y": 25}),
        ("fill", {"fill_rule": FillRule.NONZERO}),
        "restore",
        # End fill
        ("line to", {"x": 30, "y": 40}),
        ("line to", {"x": 20, "y": 30}),
        ("line to", {"x": 40, "y": 50}),
        "restore",
        ("line to", {"x": 99, "y": 99}),
        "restore",
    ]

    # Remove the fill state
    state.remove(fill)
    widget.redraw()

    # Counts are as expected
    assert len(widget.root_state) == 3
    assert len(state) == 4
    assert len(fill) == 1

    # Draw instructions show the new position
    assert widget._impl.draw_instructions == [
        "save",
        ("line to", {"x": 0, "y": 0}),
        "save",
        ("line to", {"x": 10, "y": 20}),
        ("line to", {"x": 30, "y": 40}),
        ("line to", {"x": 20, "y": 30}),
        ("line to", {"x": 40, "y": 50}),
        "restore",
        ("line to", {"x": 99, "y": 99}),
        "restore",
    ]

    # Insert the fill state at a negative index
    state.insert(-1, fill)
    widget.redraw()
    # Draw instructions show the new position
    assert widget._impl.draw_instructions == [
        "save",
        ("line to", {"x": 0, "y": 0}),
        "save",
        ("line to", {"x": 10, "y": 20}),
        ("line to", {"x": 30, "y": 40}),
        ("line to", {"x": 20, "y": 30}),
        # Begin fill
        "save",
        "begin path",
        ("line to", {"x": 25, "y": 25}),
        ("fill", {"fill_rule": FillRule.NONZERO}),
        "restore",
        # End fill
        ("line to", {"x": 40, "y": 50}),
        "restore",
        ("line to", {"x": 99, "y": 99}),
        "restore",
    ]

    # Clear the state
    state.clear()
    widget.redraw()

    # Counts are as expected
    assert len(widget.root_state) == 3
    assert len(state) == 0

    # No draw instructions other than the outer state.
    assert widget._impl.draw_instructions == [
        "save",
        ("line to", {"x": 0, "y": 0}),
        "save",
        "restore",
        ("line to", {"x": 99, "y": 99}),
        "restore",
    ]


def test_contains(widget):
    """Whether a drawing action is in a state can be tested."""
    with widget.Stroke() as stroke:
        reset_transform = stroke.reset_transform()
        with stroke.Fill() as fill:
            line_to = fill.line_to(0, 0)
        close_path = stroke.close_path()

    scale = Scale(1, 1)

    for action in [stroke, reset_transform, fill, line_to, close_path]:
        assert action in widget.root_state

    assert close_path not in fill
    assert scale not in widget.root_state


@pytest.mark.parametrize(
    "StateClass, args, kwargs, fail, attrs",
    [
        ###########
        # ClosePath
        ###########
        (
            ClosePath,
            (5, 10),
            {},
            False,
            {"x": 5, "y": 10},
        ),
        (
            ClosePath,
            (5,),
            {"y": 10},
            False,
            {"x": 5, "y": 10},
        ),
        (
            ClosePath,
            (5,),
            {"x": 5},
            True,
            None,
        ),
        (
            ClosePath,
            (5,),
            {"x": 5, "y": 10},
            True,
            None,
        ),
        ######
        # Fill
        ######
        (
            Fill,
            (5, 10),
            {},
            False,
            {"fill_rule": FillRule.NONZERO, "color": None, "x": 5, "y": 10},
        ),
        (
            Fill,
            (5,),
            {},
            False,
            {"fill_rule": FillRule.NONZERO, "color": None, "x": 5, "y": None},
        ),
        (
            Fill,
            (REBECCAPURPLE,),
            {},
            False,
            {
                "fill_rule": FillRule.NONZERO,
                "color": REBECCA_PURPLE_COLOR,
                "x": None,
                "y": None,
            },
        ),
        (
            Fill,
            (REBECCAPURPLE, FillRule.EVENODD, 5, 10),
            {},
            False,
            {
                "fill_rule": FillRule.EVENODD,
                "color": REBECCA_PURPLE_COLOR,
                "x": 5,
                "y": 10,
            },
        ),
        # Unfortunately there's not a graceful way to handle something like
        # Fill(REBECCAPURPLE, fill_rule=FillRule.EVENODD), without renaming the *actual*
        # fill_rule parameter, since Python throws a TypeError from the repeated
        # argument before even getting to our code.
        ########
        # Stroke
        ########
        (
            Stroke,
            (5, 10),
            {},
            False,
            {"color": None, "line_width": None, "line_dash": None, "x": 5, "y": 10},
        ),
        (
            Stroke,
            (5,),
            {},
            False,
            {"color": None, "line_width": None, "line_dash": None, "x": 5, "y": None},
        ),
        (
            Stroke,
            (REBECCAPURPLE,),
            {},
            False,
            {
                "color": REBECCA_PURPLE_COLOR,
                "line_width": None,
                "line_dash": None,
                "x": None,
                "y": None,
            },
        ),
        (
            Stroke,
            (REBECCA_PURPLE_COLOR,),
            {},
            False,
            {
                "color": REBECCA_PURPLE_COLOR,
                "line_width": None,
                "line_dash": None,
                "x": None,
                "y": None,
            },
        ),
        (
            Stroke,
            (
                5,
                10,
                REBECCAPURPLE,
            ),
            {},
            False,
            {
                "color": REBECCA_PURPLE_COLOR,
                "line_width": None,
                "line_dash": None,
                "x": 5,
                "y": 10,
            },
        ),
        (
            Stroke,
            (REBECCAPURPLE, 2, [1, 2]),
            {},
            False,
            {
                "color": REBECCA_PURPLE_COLOR,
                "line_width": 2,
                "line_dash": [1, 2],
                "x": None,
                "y": None,
            },
        ),
        (
            Stroke,
            (REBECCAPURPLE, 2, [1, 2], 5, 10),
            {},
            False,
            {
                "color": REBECCA_PURPLE_COLOR,
                "line_width": 2,
                "line_dash": [1, 2],
                "x": 5,
                "y": 10,
            },
        ),
        (
            Stroke,
            (
                5,
                5,
                REBECCAPURPLE,
            ),
            {"x": 10},
            True,
            None,
        ),
    ],
)
def test_deprecated_signatures(StateClass, args, kwargs, fail, attrs):
    """State subclasses correctly interpret and warn on deprecated usage."""
    if fail:
        context = pytest.raises(TypeError)
    else:
        context = nullcontext()

    with pytest.warns(DeprecationWarning):
        with context:
            state = StateClass(*args, **kwargs)

    if not fail:
        for name, value in attrs.items():
            assert getattr(state, name) == value
