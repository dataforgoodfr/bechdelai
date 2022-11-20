"""
Utils script to fetch data from the website bechdeltest.com<br>
There is no rate limit to the API, so don't push them ;) please be cautious while calling it

"""
import requests
import pandas as pd


BASE_URL = "http://bechdeltest.com/api/v1"


def get_all_data() -> pd.DataFrame:
    """Get all data from the website Bechdeltest.com

    The columns available will be : 

    - imdbid	The IMDb id.
    - id	The bechdeltest.com unique id.
    - rating	The actual score. Number from 0 to 3 (0 means no two women, 1 means no talking, 2 means talking about a man, 3 means it passes the test).
    - title	The title of the movie. Any weird characters are HTML encoded (so Brüno is returned as "Br&uuml;no").
    - year	The year this movie was released (according to IMDb).

    See https://bechdeltest.com/api/v1/doc from more documentation with the getAllMovies route


    Returns:
        pd.DataFrame: Full dataset in a pandas Dataframe
    """
    url = "http://bechdeltest.com/api/v1/getAllMovies"
    r = requests.get(url).json()
    data = pd.DataFrame(r)
    return data



    