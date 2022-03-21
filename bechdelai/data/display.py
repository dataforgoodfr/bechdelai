from IPython.display import display
from IPython.display import HTML


def show_movie_suggestions(suggestions, top=None):
    """Show suggestions"""
    if top is not None:
        suggestions = suggestions[:top]

    for i, elem in enumerate(suggestions):
        display(HTML(f"{i} " + elem[0]))


def show_movie_suggestions_get_id(
    suggestions, top=None, with_cast_url=True, verbose=True
):
    """Show suggestions and returns wanted ID"""
    show_movie_suggestions(suggestions, top)

    print()
    idx = int(input("Select wanted index:"))

    if verbose:
        print("ID of the movie:", str(suggestions[idx][1]))
        if with_cast_url:
            print("URL of the casting:", suggestions[idx][2])

    if with_cast_url:
        return suggestions[idx][1], suggestions[idx][2]

    return suggestions[idx][1]
