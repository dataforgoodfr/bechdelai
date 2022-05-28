# BechdelAI
Measurement and automation of the Bechdel test, female (under)representation and representation inequalities in cinema and audiovisual media

![](https://dataforgood.fr/img/projects/bechdelai_new.png)


> This repo is under active development, the documentation may not be up to date

## Structure of the repo

```
- bechdelai         ----- Python code as a library
- data              ----- Reusable datasets
- notebooks         ----- Experiments
    - video         ----- Experiments on video data
    - audio         ----- Experiments on audio data
    - posters       ----- Experiments on posters
    - nlp           ----- Experiments on nlp
```


## Documentation

- Official website for the project is here (French) - https://dataforgood.fr/projects/bechdelai
- Project documentation is [here](https://dataforgood.slite.com/app/docs/~8IRrgyKYR) (French)


## Get movies from Allociné / TMDB

### Install

```bash
pip install -e .
```

### Run with cli

```
$ scrap-movies --help
Usage: scrap-movies [OPTIONS]

  CLI for scraping movies from Allociné and TMDB.

  It follows these steps:

  1. Extract N movies from Allociné

  2. Find corresponding TMDB id for each movie

  3. Get data for each movie with TMDB API: metadata, crew and cast

  4. Save csv results

Options:
  -n, --movies-number TEXT  Number of movies wanted.  [required]
  -p, --path TEXT           Path where to save csv results.  [required]
  --sort-by TEXT            How to sort movies in Allociné pages. Available
                            choices: ['popularity', 'alphabetic',
                            'press_note', 'public_note']
  --genre TEXT              Filter for genre.
  --year TEXT               Filter for year.
  --country TEXT            Filter for country.
  -v, --verbose BOOLEAN     The person to greet.
  --help                    Show this message and exit.
```

**Examples**

```bash
# Scrap first current most popular movie in Allociné
scrap-movies -n 1 -p .
```

```bash
# Scrap top 15 most popular movies in Allociné in 2018 from France
scrap-movies -n 15 -p . --year 2018 --country France
```

```bash
# Scrap top 50 with the best public notes
scrap-movies -n 50 -p . --sort-by public_note
```
