"""Function to get data from TMDB API
"""
import urllib
import requests
import pandas as pd
import numpy as np
import os
from PIL import Image,UnidentifiedImageError
from tqdm.auto import tqdm
from os import environ
from io import BytesIO
from typing import Union,Optional,List,Dict,Tuple
from dotenv import load_dotenv
from IPython.display import display,HTML
from .fetch import fetch_json_from_url,fetch_image_from_url,RequestException

class APIKeyNotSetInEnv(Exception):
    """Exception class for API key not set"""

    pass


# main urls
MAIN_URL = "https://www.themoviedb.org"
IMG_URL = "https://image.tmdb.org/t/p/w94_and_h141_bestv2"
API_URL = "https://api.themoviedb.org/3"
IMG_URL = "https://image.tmdb.org/t/p/original"

# Url for the API
# SEARCH_API_URL = f"{API_URL}/search/movie?api_key={API_KEY}&query={{query}}"
# MOVIE_API_URL = f"{API_URL}/movie/{{movie_id}}?api_key={API_KEY}"
# CAST_API_URL = f"{API_URL}/movie/{{movie_id}}/credits?api_key={API_KEY}"
# PERSON_API_URL = f"{API_URL}/person/{{person_id}}?api_key={API_KEY}"
# SEARCH_IMDB_URL = (
#     f"{API_URL}//find/tt{{imdb_id}}?api_key={API_KEY}&external_source=imdb_id"
# )


# Html for suggestion diplays
FORMAT_SUGG_HTML = """
<tr>
    <td>
        <a href="{href}"><img src="{poster_url}"/></a>
    </td>
    <td>
        <a href="{href}">
            {title}
        </a> ({year})
    </td>
</tr>
"""

class TMDB:
    def __init__(self,api_key = None):

        if api_key is None:

            try:
                # load .env file
                load_dotenv(f"{os.getcwd()}/.env", verbose=True)
                load_dotenv()
                self.api_key = environ["TMDB_API_KEY"]
            except:
                raise APIKeyNotSetInEnv(
                    "You need to set your TMDB API key into a .env file in your current working directory.\n`TMDB_API_KEY=<API_KEY>`\n"
                    + "To get a key please check directly on the website https://developers.themoviedb.org/3/getting-started/introduction"
                )
        
        else:
            self.api_key = api_key

    def url_search_api(self,query):
        return f"{API_URL}/search/movie?api_key={self.api_key}&query={query}"

    def url_image(self,path):
        if path.startswith(IMG_URL):
            return path
        else:
            return f"{IMG_URL}{path}"

    def url_movie_details_api(self,movie_id):
        return f"{API_URL}/movie/{movie_id}?api_key={self.api_key}"

    def url_person_api(self,person_id):
        return f"{API_URL}/person/{person_id}?api_key={self.api_key}"

    def url_search_imdb(self,imdb_id):
        imdb_id = imdb_id.replace("tt","")
        return f"{API_URL}//find/tt{imdb_id}?api_key={self.api_key}&external_source=imdb_id"        

    def url_movie_api(self,movie_id,endpoint):
        return f"{API_URL}/movie/{movie_id}/{endpoint}?api_key={self.api_key}"
        

    def fetch_tmdb_api(self,endpoint):
        return fetch_json_from_url(f"{API_URL}/{endpoint}")


 
    def fetch_data_from_pages(self,api_url: str, n_pages: int = None) -> List[Dict]:
        """
        Fetches data from multiple pages of a TMDB API response.

        Args:
            api_url: The URL of the API endpoint.
            n_pages: The number of pages to fetch. If None, fetches all pages.

        Returns:
            A list of dictionaries containing the results from all pages.

        Raises:
            Exception: If an error occurs while fetching the data.
        """
        # Send request to the first page of the API response
        response = requests.get(api_url)
        response_json = response.json()

        # Check for errors
        if response.status_code != 200:
            raise Exception(f"Failed to fetch data. Status code: {response.status_code}. Error message: {response_json.get('status_message')}")

        # Extract the total number of pages from the response
        total_pages = response_json.get('total_pages')
        total_results = response_json.get('total_results')
        print(f"... There are {total_results} results with {total_pages} pages")

        # Determine the number of pages to fetch
        if n_pages is None:
            n_pages = total_pages
        else:
            n_pages = min(n_pages, total_pages)

        # Fetch data from all pages
        results = response_json.get('results')
        for page in tqdm(range(2, n_pages + 1)):
            response = requests.get(f"{api_url}&page={page}")
            response_json = response.json()

            # Check for errors
            if response.status_code != 200:
                raise Exception(f"Failed to fetch data. Status code: {response.status_code}. Error message: {response_json.get('status_message')}")

            # Append results from the current page to the results list
            results.extend(response_json.get('results'))

        return results


    def search_movie_from_query(self,query: str,n_pages = 1,return_json = False) -> dict:
        """Get TMDB API result for search movie endpoint given a query

        More info at:
        https://developers.themoviedb.org/3/search/search-movies

        You can find the website view with this url:
        https://www.themoviedb.org/search/movie?query=

        Parameters
        ----------
        query : str
            Movie query to research
        """
        url = self.url_search_api(query)
        json_results = fetch_json_from_url(url)
        if return_json:
            return json_results
        else:
            total_pages = json_results["total_pages"]
            total_results = json_results["total_results"]
            print(f"... There are {total_results} movies with {total_pages} pages of results for the search '{query}'")
            if n_pages is None:
                n_pages = total_pages
            results = json_results["results"]
            if n_pages == 1:
                return pd.DataFrame(results)
            else:
                for i in tqdm(range(2,min(n_pages,total_pages)+1)):
                    json_results = self.search_movie_from_query(f"{query}&page={i}",return_json = True)
                    results.extend(json_results["results"])
                return pd.DataFrame(results)
            


    def get_movie_details(self,movie_id) -> dict:
        """Get TMDB API result for movie details endpoint given an id

        You can find the website view with this url (example for id 81):
        https://www.themoviedb.org/movie/81

        Parameters
        ----------
        movie_id : str or int
            Movie id to get details from
        """
        url = self.url_movie_details_api(movie_id)
        return fetch_json_from_url(url)

    def get_movie_videos(self,movie_id:str) -> pd.DataFrame:
        url = self.url_movie_api(movie_id,"videos")
        results = fetch_json_from_url(url)
        return pd.DataFrame(results["results"])

    def get_movie_reviews(self,movie_id:str,n_pages: int = None) -> pd.DataFrame:
        url = self.url_movie_api(movie_id,"reviews")
        results = self.fetch_data_from_pages(url,n_pages)
        return pd.DataFrame(results)

    def get_movie_images(self,movie_id:str,n_pages: int = None) -> pd.DataFrame:
        url = self.url_movie_api(movie_id,"images")
        results = fetch_json_from_url(url)
        backdrops = pd.DataFrame(results["backdrops"]).assign(image_type = lambda x : "backdrop")
        posters = pd.DataFrame(results["posters"]).assign(image_type = lambda x : "poster")
        return pd.concat([backdrops,posters],ignore_index = True,axis = 0)

    def get_movie_keywords(self,movie_id:str) -> list:
        url = self.url_movie_api(movie_id,"keywords")
        results = fetch_json_from_url(url)["keywords"]
        return [x["name"] for x in results]

    def get_movies_now_playing(self,n_pages = None,region = None):
        url = f"{API_URL}/movie/now_playing?api_key={self.api_key}"
        if region is not None:
            url += f"&region={region}"
        results = self.fetch_data_from_pages(url,n_pages)
        return pd.DataFrame(results)

    def get_movies_popular(self,n_pages = None,region = None):
        url = f"{API_URL}/movie/popular?api_key={self.api_key}"
        if region is not None:
            url += f"&region={region}"
        results = self.fetch_data_from_pages(url,n_pages)
        return pd.DataFrame(results)
        
    def get_movies_top_rated(self,n_pages = None,region = None):
        url = f"{API_URL}/movie/top_rated?api_key={self.api_key}"
        if region is not None:
            url += f"&region={region}"
        results = self.fetch_data_from_pages(url,n_pages)
        return pd.DataFrame(results)


    def get_movie_cast(self,movie_id: int) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Fetches the cast and crew details for a movie from the TMDB API.
        The cast refers to the actors who appear on screen and play the characters, 
        while the crew consists of the people who work behind the scenes to make the movie or TV show, 
        such as the director, producers, cinematographer, sound engineers, and editors.

        We get data about
        - For the cast: gender, name, character's name, popularity, picture, order in the credits
        - For the crew: gender, name, job, department

        You can find the website view with this url (example for id 81):
        https://www.themoviedb.org/movie/81/cast

        Args:
            movie_id: The ID of the movie.

        Returns:
            A tuple containing two pandas dataframes - one for the cast and one for the crew.

        Raises:
            Exception: If an error occurs while fetching the data from the API.
        """
        # Construct the URL to fetch the movie credits data from the TMDB API
        url = self.url_movie_api(movie_id, "credits")

        # Fetch the JSON response from the API and convert it to pandas dataframes for the cast and crew
        results = fetch_json_from_url(url)
        cast = pd.DataFrame(results["cast"])
        crew = pd.DataFrame(results["crew"])

        return cast, crew


    def get_id_from_imdb_id(self,imdb_id) -> str:
        """Get TMDB API result for movie cast endpoint given an id

        Parameters
        ----------
        imdb_id : str or int
            Movie id to get cast from
        """
        url = self.url_search_imdb(str(imdb_id))

        res = fetch_json_from_url(url)
        if len(res["movie_results"]) == 0:
            return np.NaN
        else:
            return str(res["movie_results"][0]["id"])

    def format_results_for_suggestion(self,search_res: dict) -> list:
        """Format search movie results for `show_movie_suggestions()`

        Parameters
        ----------
        search_res : dict
            result of `search_movie_from_query()`

        Returns
        -------
        list
            List of formated tuple for displays.
            1st element is the html to display and the 2nd
            is the movie ID
        """
        if "results" not in search_res:
            raise ValueError("search_res must be the result of TMDB search movie endpoint")

        format_res = []
        # for each movie format is a tuple of
        # (html of the movie, movie id)
        for movie in search_res["results"]:
            movie_id = movie["id"]

            href = f"{MAIN_URL}/movie/{movie_id}"
            poster_url = f"{IMG_URL}/" + str(movie["poster_path"])
            title = movie["original_title"]
            year = movie["release_date"][:4]

            html = FORMAT_SUGG_HTML.format(
                href=href, poster_url=poster_url, title=title, year=year
            )
            format_res.append((html, movie_id))

        return format_res


    def get_all_movies_details(self,movie_ids: list,is_imdb_id:bool = False) -> tuple:
        """Returns TMDB API return for all movie ID
        set in the input

        Get metadata from `get_movie_details_from_id()` function
        and cast and crew from `get_movie_cast_from_id()` function

        Parameters
        ----------
        movie_ids : list
            List of TMDB ids

        Returns
        -------
        tuple
            3 dataframes: movie details, crew and cast
        """
        metadata_df = []
        crew_df = []
        cast_df = []

        for movie_id in tqdm(movie_ids):

            if is_imdb_id:
                movie_id = self.get_id_from_imdb_id(movie_id)

            if movie_id is None:
                continue

            data = self.get_movie_details(movie_id)
            metadata_df.append(data)

            cast,crew = self.get_movie_cast(movie_id)
            cast["movie_id"] = movie_id
            crew["movie_id"] = movie_id

            cast_df.append(cast)
            crew_df.append(crew)

        movies_df = pd.DataFrame(metadata_df)
        cast_df = pd.concat(cast_df,ignore_index = True,axis = 0)
        crew_df = pd.concat(crew_df,ignore_index = True,axis = 0)

        movies_df["id"] = movies_df["id"].astype(str)
        cast_df["movie_id"] = cast_df["movie_id"].astype(str)
        crew_df["movie_id"] = crew_df["movie_id"].astype(str)

        return movies_df, cast_df, crew_df


    def get_image_from_url(self, url: str) -> Image:
        """
        Fetches a poster image from the given URL and returns it as a PIL Image.

        This function takes a poster image URL as input and adds the TMDB base URL if it doesn't start with "https".
        It then calls the get_image_from_url function to fetch the image and returns it as a PIL Image.

        Args:
            url (str): The URL of the poster image to fetch.

        Returns:
            PIL.Image: The fetched poster image as a PIL Image object.
        """
        if not url.startswith("https"):
            url = self.url_image(url)
        img = fetch_image_from_url(url)
        return img

    def get_movie_details_from_imdb_id(self, imdb_id: str) -> dict:
        """
        Fetches movie details from TMDB using an IMDb ID and returns them as a dictionary.

        This function first retrieves the TMDB ID corresponding to the given IMDb ID using the
        get_id_from_imdb_id function. It then calls the get_movie_details_from_id function to
        fetch the movie details using the TMDB ID and returns them as a dictionary.

        Args:
            imdb_id (str): The IMDb ID of the movie to fetch.

        Returns:
            dict: A dictionary containing the fetched movie details.
        """
        tmdb_id = self.get_id_from_imdb_id(imdb_id)
        return self.get_movie_details_from_id(tmdb_id)


    def get_poster_image(self, movie_id: int, as_img: bool = True, backdrop: bool = False) -> Union[str, Image.Image]:
        """
        Returns the poster or backdrop image for a movie with the specified ID.

        Args:
            movie_id (int): The ID of the movie to retrieve the poster or backdrop for.
            as_img (bool): Whether to return the image as a PIL Image object (default True).
            backdrop (bool): Whether to retrieve the movie's backdrop image instead of the poster image (default False).

        Returns:
            Union[str, Image.Image]: If as_img is True, returns a PIL Image object containing the image data.
            If as_img is False, returns the URL of the image as a string.
        
        Raises:
            requests.exceptions.RequestException: If the request to the TMDB API fails for any reason.
            ValueError: If the specified movie ID is not a positive integer.
        """
        if not isinstance(movie_id, int) or movie_id <= 0:
            raise ValueError("movie_id must be a positive integer")
        
        details = self.get_movie_details(movie_id)
        path = details["poster_path"] if not backdrop else details["backdrop_path"]
        image_url = f"https://image.tmdb.org/t/p/original{path}"
        
        if as_img:
            image = fetch_image_from_url(image_url)
            return image
        else:
            return image_url



    def discover_movies(self, with_original_language: str = "fr", start_year: Optional[str] = None,
                            end_year: Optional[str] = None, year: Optional[str] = None, min_vote_count: int = 0,
                            n_pages: int = None, sort_by: str = "popularity.desc", **kwargs) -> pd.DataFrame:
        """
        Queries the TMDB Discover API to get a list of movies that match the specified criteria, across multiple pages.

        For more information on the Discover API, see:
        - https://developers.themoviedb.org/3/discover/movie-discover
        - https://www.themoviedb.org/talk/5f60b26c706b9f0039076517
        - https://www.themoviedb.org/documentation/api/discover

        Args:
            with_original_language (str): The original language of the movie. Defaults to "fr".
            start_year (str, optional): The earliest year a movie was released. Defaults to None.
            end_year (str, optional): The latest year a movie was released. Defaults to None.
            year (str, optional): The specific year a movie was released. Defaults to None.
            min_vote_count (int): The minimum number of votes a movie must have to be returned. Defaults to 0.
            pages (int): The number of pages of results to retrieve. Defaults to 1000.
            sort_by (str): The sorting criteria to use for the results. Defaults to "popularity.desc".
            **kwargs: Additional query parameters that can be passed to the Discover API.

        Returns:
            pd.DataFrame: A pandas DataFrame containing a list of movies that match the specified criteria.

        Raises:
            HTTPError: An error occurred while sending a request to the TMDB API.
        """

        query = {
            "with_original_language":with_original_language,
            "vote_count.gte":min_vote_count,
            "sort_by":sort_by,
            **kwargs
        }

        if year is not None: query["primary_release_year"] = year
        if start_year is not None: query["primary_release_date.gte"] = start_year
        if end_year is not None: query["primary_release_date.lte"] = end_year

        query_string = urllib.parse.urlencode(query)


        url = f"{API_URL}/discover/movie?api_key={self.api_key}&{query_string}"
        results = self.fetch_data_from_pages(url,n_pages)
        return pd.DataFrame(results)

    def download_all_posters(self,movie_ids: list, folder: str = "posters") -> None:
        """
        Downloads the poster images for all movies in a given DataFrame and saves them to a folder.

        Args:
            movies (list): list of movie TMDB ids 
            folder (str): Path to the folder where the images will be saved. If the folder does not exist, it will be created.

        Returns:
            None
        """

        if not os.path.exists(folder):
            os.mkdir(folder)

        for movie_id in tqdm(movie_ids):
            try:
                img = self.get_poster_image(movie_id)
            except UnidentifiedImageError:
                print("The poster of the movie with id =", movie_id, "cannot be downloaded (check poster path).")
            except RequestException:
                print("The poster of the movie with id =", movie_id, "cannot be downloaded (request error).")
            else:
                path = os.path.join(folder,f"{movie_id}.png")
                if not os.path.exists(path):
                    img.save(path)




    def get_person_details(self,person_id) -> dict:
        """Get TMDB API result for person details by id

        You can find the website view with this url (example for id 81):
        https://www.themoviedb.org/person/81

        Parameters
        ----------
        person_id : str or int
            Person id to get details from
        """
        url = self.url_person_api(person_id)
        return fetch_json_from_url(url)


    def get_person_credits(self,person_id) -> dict:
        url = f"{API_URL}/person/{person_id}/combined_credits?api_key={self.api_key}"
        return fetch_json_from_url(url)



    def get_person_images(self,person_id) -> dict:
        url = f"{API_URL}/person/{person_id}/images?api_key={self.api_key}"
        return fetch_json_from_url(url)

    def show_images_on_notebook(self,list_of_paths,width = 250):

        html = ""
        for path in list_of_paths:
            html += f"""<div style='width:{width}px;text-align:center;margin-left:20px;margin-bottom:30px;'><h5 style="font-size:9px;width:100%;word-wrap:break-word">{path}</h5><img style='width:100%' src='{self.url_image(path)}'/></div>"""
        
        div_html = f"<div style='display:flex;flex-wrap:wrap'>{html}</div>"

        return display(HTML(div_html))




    def download_image(self,paths):

        if not isinstance(paths,list): paths = [paths]

        imgs = []
        for path in paths:
            img = self.get_image_from_url(path)
            img.save(path.split("/")[-1])
            imgs.append(img)
        print("... Images saved in current working directory")

        if len(imgs) == 1:
            return imgs[0]
        else:
            return imgs




        
        

