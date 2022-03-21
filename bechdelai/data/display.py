"""Functions for notebook usage
Shows returned suggestion and return ID for the wanted movie
"""
from IPython.display import display
from IPython.display import HTML


def show_movie_suggestions(suggestions, top=None):
    """Show suggestions as html with
    list index for each element

    Parameters
    ----------
    suggestions: list(tuple)
        list of tuple for movie suggestion. It requires
        the first element to be a html string.
    top: int, default=None
        Number of items to show, if None display
        all the suggestions
    """
    if top is not None:
        suggestions = suggestions[:top]

    for i, elem in enumerate(suggestions):
        display(HTML(f"{i} " + elem[0]))


def show_movie_suggestions_get_id(suggestions, top=None, verbose=True):
    """Show suggestions and returns wanted ID

    suggestions can be retrived from these functions:
    - `IMDB`:
        suggestions = find_movie_from_kerword(query)
    - `TMDB`:
        data = search_movie_from_query(query)
        suggestions = format_results_for_suggestion(data)

    Parameters
    ----------
    suggestions: list(tuple)
        list of tuple for movie suggestion.
        It follows this format (`html str for display`, `movie id`)
    top: int, default=None
        Number of items to show, if None display
        all the suggestions

    Returns
    -------
    int:
        Movie id
    """
    show_movie_suggestions(suggestions, top)

    print()
    idx = int(input("Select wanted index:"))

    if verbose:
        print("ID of the movie:", str(suggestions[idx][1]))

    return suggestions[idx][1]
