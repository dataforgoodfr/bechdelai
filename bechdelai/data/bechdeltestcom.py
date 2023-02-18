"""
Utils script to fetch data from the website bechdeltest.com<br>
There is no rate limit to the API, so don't push them ;) please be cautious while calling it

"""
import requests
import pandas as pd


BASE_URL = "http://bechdeltest.com/api/v1"


def fetch_all_data() -> pd.DataFrame:
    """
    Fetches all movie data from Bechdeltest.com and returns it as a pandas DataFrame.

    This function sends an HTTP GET request to the Bechdeltest.com API endpoint "getAllMovies" and receives a
    JSON response containing information about all movies in their database. The response is parsed into a
    pandas DataFrame with the following columns:

    - imdbid: The IMDb ID of the movie.
    - id: The unique ID of the movie on Bechdeltest.com.
    - rating: The Bechdel test score of the movie, a number from 0 to 3 where 0 means no two women, 1 means no talking,
      2 means talking about a man, and 3 means it passes the test.
    - title: The title of the movie, with HTML encoding for special characters.
    - year: The year the movie was released according to IMDb.
    
    See https://bechdeltest.com/api/v1/doc from more documentation with the getAllMovies route

    Raises:
        requests.exceptions.RequestException: If the request to the Bechdeltest.com API fails for any reason.

    Returns:
        pd.DataFrame: A pandas DataFrame containing all movie data with the columns described above.
    """
    url = "http://bechdeltest.com/api/v1/getAllMovies"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for any HTTP error status code
        data = pd.DataFrame(response.json())
        return data
    except requests.exceptions.RequestException as e:
        raise e



    