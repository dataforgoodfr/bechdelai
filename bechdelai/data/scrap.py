"""Functions to scrap website
"""
import requests

DEFAULT_HEADER = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
    "Accept-Language": "en-GB,en;q=0.5",
}


class RequestException(Exception):
    """Exception class for request error"""

    pass


class NotJSONContentException(Exception):
    """Exception class when request return is not a JSON"""

    pass


def create_header(url: str) -> dict:
    """Create a header dictionnary if it need
    to be changed (e.g. for an API)

    Parameters
    ----------
    url : str
        url to request (needed to get the host)

    Returns
    -------
    dict
        header dictionnary

    Raises
    ------
    TypeError
        url must be a string
    ValueError
        url must start with 'http'
    """
    if not isinstance(url, str):
        raise TypeError("url must be a string")
    if not (url.startswith("http://") or url.startswith("https://")):
        raise ValueError("url must start with 'http'")

    header = DEFAULT_HEADER

    url_split = url.split("//")
    http = url_split[0]
    host = url_split[1].split("/")[0]

    header["Host"] = host
    header["Referer"] = http + "//" + host
    header["Origin"] = http + "//" + host

    return header


def get_data_from_url(url: str) -> requests.Response:
    """Return answer of a request get
    from a wanted url

    Parameters
    ----------
    url : str
        url to request

    Returns
    -------
    requests.Response
        answer from requests.get function

    Raises
    ------
    TypeError
        url must be a string
    ValueError
        url must start with 'http'
    """

    if not isinstance(url, str):
        raise TypeError("url must be a string")
    if not (url.startswith("http://") or url.startswith("https://")):
        raise ValueError("url must start with 'http'")

    headers = create_header(url)
    r = requests.get(url, headers=headers)

    return r


def get_json_from_url(url: str) -> dict:
    """Get json results from an endpoint

    Parameters
    ----------
    url : str
        url to request

    Returns
    -------
    dict
        JSON resulted from the endpoint call

    Raises
    ------
    RequestException
        Status code different from 200
    """
    ans = get_data_from_url(url)

    if ans.status_code != 200:
        raise RequestException(f"Status code different from 200, got {ans.status_code}")

    content_type = ans.headers["Content-Type"]
    if "json" not in content_type:
        raise NotJSONContentException(f"Result is not a JSON, got {content_type}")

    data = ans.json()

    return data
