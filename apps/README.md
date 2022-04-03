# Apps

In this directory we can find all apps developed for `bechdelai`.

## 1. Extract movies from Allociné and TMDB `get_movies_allocine_tmdb/`

Goal of the app:
- Given filters such as genre, country or year extract a choosen number of movies from `Allociné`
- Then retrieves associated `TMDB` id movie
- From these ids get metadata for each movie and cast and crew details

**Install and run**

```bash
cd ..
pip install .
pip install streamlit
streamlit run apps/get_movies_allocine_tmdb/app.py
```
