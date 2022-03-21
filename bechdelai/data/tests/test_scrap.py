"""Tests scrap functions
"""
import pytest

from bechdelai.data.scrap import create_header
from bechdelai.data.scrap import get_data_from_url
from bechdelai.data.scrap import get_json_from_url
from bechdelai.data.scrap import NotJSONContentException
from bechdelai.data.scrap import RequestException


@pytest.mark.parametrize(
    "url, host",
    [
        ("http://test.com", "test.com"),
        ("http://i.am.an.url.com", "i.am.an.url.com"),
    ],
)
def test_create_header(url, host):
    """Test the function create header with correct input"""
    header = create_header(url)
    assert header["Host"] == host


@pytest.mark.parametrize(
    "url",
    [10, 1.2, ["http://error.com"]],
)
def test_create_header_typeerror(url):
    """Test the function create header with incorrect input"""

    with pytest.raises(TypeError):
        create_header(url)


@pytest.mark.parametrize(
    "url",
    ["not_an_url", "http:/test.com", "https//42.fr"],
)
def test_create_header_url_http_error(url):
    """Test the function create header with string but not url"""

    with pytest.raises(ValueError):
        create_header(url)


@pytest.mark.parametrize(
    "url, exception",
    [
        (1, TypeError),
        (["url"], TypeError),
        ("not_an_url", ValueError),
    ],
)
def test_get_data_from_url_error(url, exception):
    """Test errors for get_data_from_url"""
    with pytest.raises(exception):
        get_data_from_url(url)


@pytest.mark.parametrize(
    "url, expected_status_code",
    [
        ("https://www.python.org/", 200),
        ("https://python.org/", 500),
        ("https://www.python.org/not_valid", 404),
    ],
)
def test_get_data_from_url(url, expected_status_code):
    """Test get_data_from_url"""
    ans = get_data_from_url(url)

    assert ans.status_code == expected_status_code


@pytest.mark.parametrize(
    "url, exception",
    [
        ("https://www.python.org/not_valid", RequestException),
        ("https://www.python.org", NotJSONContentException),
    ],
)
def test_get_json_from_url_error(url, exception):
    """Test errors for get_json_from_url"""
    with pytest.raises(exception):
        get_json_from_url(url)


@pytest.mark.parametrize(
    "url, expected_result",
    [
        # Dummy online API
        (
            "https://jsonplaceholder.typicode.com/todos/1",
            {"userId": 1, "id": 1, "title": "delectus aut autem", "completed": False},
        ),
    ],
)
def test_get_json_from_url(url, expected_result):
    """Test get_data_from_url"""
    data = get_json_from_url(url)

    assert data == expected_result
