import pytest

from toga.style.pack import (
    BOLD,
    ITALIC,
    NORMAL,
    SANS_SERIF,
    SMALL_CAPS,
    SYSTEM,
    SYSTEM_DEFAULT_FONT_SIZE,
    Pack,
)


def assert_font(style, values):
    # Test against retrieving the composite property
    assert style.font == values

    # Also test against the underlying individual properties
    (font_style, font_variant, font_weight, font_size, font_family) = values

    assert style.font_style == font_style
    assert style.font_variant == font_variant
    assert style.font_weight == font_weight
    assert style.font_size == font_size
    assert style.font_family == font_family


def test_default_values():
    """A blank Pack instance has the correct default values."""
    assert_font(Pack(), (NORMAL, NORMAL, NORMAL, SYSTEM_DEFAULT_FONT_SIZE, [SYSTEM]))


@pytest.mark.parametrize(
    "value",
    [
        (ITALIC, SMALL_CAPS, BOLD, 12, ["Comic Sans", SANS_SERIF]),
        # Should also work with optionals reordered
        (SMALL_CAPS, BOLD, ITALIC, 12, ["Comic Sans", SANS_SERIF]),
        (BOLD, SMALL_CAPS, ITALIC, 12, ["Comic Sans", SANS_SERIF]),
    ],
)
def test_assign_all_non_default(value):
    """Assigning all three optionals works, regardless of order."""
    style = Pack(font=value)

    assert_font(style, (ITALIC, SMALL_CAPS, BOLD, 12, ["Comic Sans", SANS_SERIF]))


@pytest.mark.parametrize(
    "value",
    [
        # Full assignment, in order and out of order
        (NORMAL, SMALL_CAPS, NORMAL, 12, ["Comic Sans", SANS_SERIF]),
        (NORMAL, NORMAL, SMALL_CAPS, 12, ["Comic Sans", SANS_SERIF]),
        # Only the non-default
        (SMALL_CAPS, 12, ["Comic Sans", SANS_SERIF]),
        # One NORMAL
        (SMALL_CAPS, NORMAL, 12, ["Comic Sans", SANS_SERIF]),
        (NORMAL, SMALL_CAPS, 12, ["Comic Sans", SANS_SERIF]),
    ],
)
def test_assign_one_non_default(value):
    """NORMAL values stay NORMAL when set explicitly or omitted, in any order"""
    style = Pack(font=value)

    assert_font(style, (NORMAL, SMALL_CAPS, NORMAL, 12, ["Comic Sans", SANS_SERIF]))


@pytest.mark.parametrize(
    "value",
    [
        # Full assignment, in order and out of order
        (NORMAL, SMALL_CAPS, NORMAL, 12, ["Comic Sans", SANS_SERIF]),
        (NORMAL, NORMAL, SMALL_CAPS, 12, ["Comic Sans", SANS_SERIF]),
        # Only the non-default
        (SMALL_CAPS, 12, ["Comic Sans", SANS_SERIF]),
        # One NORMAL
        (SMALL_CAPS, NORMAL, 12, ["Comic Sans", SANS_SERIF]),
        (NORMAL, SMALL_CAPS, 12, ["Comic Sans", SANS_SERIF]),
    ],
)
def test_assign_one_non_default_after_setting(value):
    """Non-NORMAL optionals reset to when set explicitly or omitted, in any order."""
    style = Pack(font_weight=BOLD, font_style=ITALIC)
    style.font = value

    assert_font(style, (NORMAL, SMALL_CAPS, NORMAL, 12, ["Comic Sans", SANS_SERIF]))
