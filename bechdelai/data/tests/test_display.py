"""Test display function
"""
import pytest

from bechdelai.data.display import show_movie_suggestions
from bechdelai.data.display import show_movie_suggestions_get_id


@pytest.mark.parametrize(
    "suggestions, top, input_idx, expected_id",
    [
        ([("HTML_1", 1), ("HTML_2", 2)], None, 1, 2),
        ([("HTML_1", 1), ("HTML_2", 2)], 1, 0, 1),
    ],
)
def test_show_movie_suggestions(suggestions, top, input_idx, expected_id, monkeypatch):
    """Test that show_movie_suggestions works"""
    # no assertion because it's just display
    show_movie_suggestions(suggestions, top)

    # monkeypatch the "input" function, so that it returns input_idx.
    monkeypatch.setattr("builtins.input", lambda _: input_idx)

    movie_id = show_movie_suggestions_get_id(suggestions, top)

    assert movie_id == expected_id
