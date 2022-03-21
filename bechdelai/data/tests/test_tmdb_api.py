"""Test function for TMDB API

Requires a .env file with TMDB_API_KEY set
"""
import pytest

from bechdelai.data.tmdb import format_results_for_suggestion
from bechdelai.data.tmdb import get_movie_cast_from_id
from bechdelai.data.tmdb import get_movie_details_from_id
from bechdelai.data.tmdb import search_movie_from_query


@pytest.mark.parametrize("query", ["batman", "astérix", "totoro"])
def test_search_movie_from_query(query):
    """Test search_movie_from_query"""
    data = search_movie_from_query(query)

    assert "results" in data

    first_title = data["results"][0]["title"].lower()

    assert query in first_title


@pytest.mark.parametrize(
    "movie_id, expected_title",
    [
        (81, "Nausicaä of the Valley of the Wind"),
        (7453, "The Hitchhiker's Guide to the Galaxy"),
    ],
)
def test_get_movie_details_from_id(movie_id, expected_title):
    """Test get_movie_details_from_id"""
    data = get_movie_details_from_id(movie_id)

    title = data["title"]

    assert title == expected_title


@pytest.mark.parametrize(
    "movie_id, expected_cast_len, expected_crew_len",
    [
        (81, 27, 28),
        (7453, 25, 151),
    ],
)
def test_get_movie_cast_from_id(movie_id, expected_cast_len, expected_crew_len):
    """Test get_movie_cast_from_id"""
    data = get_movie_cast_from_id(movie_id)

    cast = data["cast"]
    crew = data["crew"]

    assert len(cast) == expected_cast_len
    assert len(crew) == expected_crew_len


@pytest.mark.parametrize(
    "search_res, expected_exception",
    [
        ([1], ValueError),
        ({"key": 1}, ValueError),
    ],
)
def test_format_results_for_suggestion_error(search_res, expected_exception):
    """Test format_results_for_suggestion input error"""
    with pytest.raises(expected_exception):
        format_results_for_suggestion(search_res)


@pytest.mark.parametrize(
    "search_res",
    [
        {
            "results": [
                {
                    "id": 1,
                    "poster_path": "tmp.png",
                    "original_title": "None",
                    "release_date": "2020",
                }
            ]
        }
    ],
)
def test_format_results_for_suggestion(search_res):
    """Test format_results_for_suggestion is working"""
    res = format_results_for_suggestion(search_res)

    assert len(res) == len(search_res["results"])
