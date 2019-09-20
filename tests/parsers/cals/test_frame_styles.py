# coding: utf-8
import pytest

from benker.parsers.cals.frame_styles import BORDER_NONE
from benker.parsers.cals.frame_styles import BORDER_SOLID
from benker.parsers.cals.frame_styles import get_frame_styles


@pytest.mark.parametrize(
    "frame, expected",
    [
        (None, {}),
        (
            "none",
            {
                "border-bottom": BORDER_NONE,
                "border-left": BORDER_NONE,
                "border-right": BORDER_NONE,
                "border-top": BORDER_NONE,
            },
        ),
        (
            "all",
            {
                "border-bottom": BORDER_SOLID,
                "border-left": BORDER_SOLID,
                "border-right": BORDER_SOLID,
                "border-top": BORDER_SOLID,
            },
        ),
        (
            "topbot",
            {
                "border-bottom": BORDER_SOLID,
                "border-left": BORDER_NONE,
                "border-right": BORDER_NONE,
                "border-top": BORDER_SOLID,
            },
        ),
        (
            "sides",
            {
                "border-bottom": BORDER_NONE,
                "border-left": BORDER_SOLID,
                "border-right": BORDER_SOLID,
                "border-top": BORDER_NONE,
            },
        ),
        (
            "top",
            {
                "border-bottom": BORDER_NONE,
                "border-left": BORDER_NONE,
                "border-right": BORDER_NONE,
                "border-top": BORDER_SOLID,
            },
        ),
        (
            "bottom",
            {
                "border-bottom": BORDER_SOLID,
                "border-left": BORDER_NONE,
                "border-right": BORDER_NONE,
                "border-top": BORDER_NONE,
            },
        ),
    ],
)
def test_get_frame_styles(frame, expected):
    actual = get_frame_styles(frame)
    assert actual == expected
