"""Cli function to scrap from Allociné and map to TMDB
"""
from time import time

import click

from bechdelai.data.allocine import get_movies
from bechdelai.data.allocine import get_tmdb_ids
from bechdelai.data.allocine import VALID_SORT_BY
from bechdelai.data.tmdb import get_movies_from_ids


@click.command()
@click.option(
    "-n", "--movies-number", "n_movies", required=True, help="Number of movies wanted."
)
@click.option(
    "-p", "--path", "path", required=True, help="Path where to save csv results."
)
@click.option(
    "--sort-by",
    "sort_by",
    default="popularity",
    help="How to sort movies in Allociné pages. Available choices: "
    + str(list(VALID_SORT_BY.keys())),
)
@click.option("--genre", default="", help="Filter for genre.")
@click.option("--year", default="", help="Filter for year.")
@click.option("--country", default="", help="Filter for country.")
@click.option("-v", "--verbose", default=True, help="The person to greet.")
def cli(n_movies, path, sort_by, genre, year, country, verbose):
    """CLI for scraping movies from Allociné and TMDB.

    It follows these steps:

    1. Extract N movies from Allociné

    2. Find corresponding TMDB id for each movie

    3. Get data for each movie with TMDB API: metadata, crew and cast

    4. Save csv results
    """
    n_movies = int(n_movies)
    verbose = bool(verbose)

    details_csv_name = "movies_details"
    crew_csv_name = "movies_crew"
    cast_csv_name = "movies_cast"

    details_df_path = f"{path}/{details_csv_name}.csv"
    crew_df_path = f"{path}/{crew_csv_name}.csv"
    cast_df_path = f"{path}/{cast_csv_name}.csv"

    print("===== Script start =====")
    t0 = time()
    print("(1 - start) get movies from allociné")

    movies = get_movies(
        n_movies=n_movies,
        genre=genre,
        country=country,
        year=year,
        sort_by=sort_by,
        verbose=True,
    )

    print("(1 - end) Allociné data retrieved after `%.1fsec`" % (time() - t0))
    print("(2 - start) match with TMDB ids")

    movies_id = get_tmdb_ids(movies)

    print("(2 - end) TMDB ids retrieved after `%.1fsec`" % (time() - t0))
    print("(3 - start) Get movie detail, cast and crew")

    movies_df, crew_df, cast_df = get_movies_from_ids(movies_id)

    print(
        "(3 - end) movie detail, cast and crew retrieved after `%.1fsec`"
        % (time() - t0)
    )
    print("(4 - start) save dataframes")

    movies_df.to_csv(details_df_path, index=False)
    cast_df.to_csv(cast_df_path, index=False)
    crew_df.to_csv(crew_df_path, index=False)

    print(f"- movies_df save at `{details_df_path}`")
    print(f"- cast_df save at `{cast_df_path}`")
    print(f"- crew_df save at `{crew_df_path}`")

    print("(4 - end) csv saved after `%.1fsec`" % (time() - t0))
    print("===== Script done =====")


if __name__ == "__main__":
    cli()
