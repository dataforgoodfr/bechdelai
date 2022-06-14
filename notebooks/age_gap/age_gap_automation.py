import sys
sys.path.append("../..")
import bechdelai.data.wikipedia as wiki
import bechdelai.data.tmdb as tmdb
import process_couples as pc
import outputformat as ouf
import pandas as pd
from datetime import datetime
import requests
import io
import spacy
from spacy import displacy
from spacy.matcher import Matcher
from spacy.tokens import Span
from spacy.matcher import PhraseMatcher
from pathlib import Path


class Movie:
    def __init__(self, title, release_year=None):
        self.title = title
        self.release_year = release_year
        self.plot = self.get_plot()
        self.cast_wiki = self.get_cast_wiki()
        self.cast = self.get_cast_tmdb()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "Film : {}".format(self.title)

    def get_plot(self):
        for query_suffix in [' ('+str(self.release_year)+' film)',' (film)','']:
            try:
                return wiki.get_section_text(self.title+query_suffix, ['Plot'])['Plot']  # to improve
            except ValueError:
                continue
        return None

    def get_cast_wiki(self):
        return  pc.get_cast_from_wikipedia(self.title,self.release_year)

    def get_cast_tmdb(self):
        movie_id = tmdb.get_best_tmdb_id(self.title,self.release_year)

        # get casting data
        data = tmdb.get_movie_cast_from_id(movie_id)
        tmdb_cast = pd.DataFrame(data["cast"])
        wiki_cast = self.cast_wiki
        cast_df = pc.correct_cast_with_wikipedia(tmdb_cast,wiki_cast)

        # only use simple quotation marks'
        cast_df.replace(regex=r'\"',value="'",inplace=True)

        #remove any accents
        cast_df['name'] = cast_df['name'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
        cast_df['character'] = cast_df['character'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')

        # get release date
        release_date = tmdb.get_movie_details_from_id(movie_id)['release_date']
        release_date = datetime.strptime(release_date, '%Y-%m-%d')
        # complete with actors/actress ages
        cast_df['age_at_release'] = pc.compute_cast_age(cast_df,release_date)

        return cast_df

def main():
    verbs = ['kisses', 'sleeps with', 'goes on a date with', 'has sex with', 'marries', 'is in love with','is in couple with',
            'is the father of', 'is the mother of','is a friend of', 'is in the family of', 'is the enemy of']
    hp4 = Movie("Harry Potter and the Goblet of Fire",2005)
    ans = pc.compute_relationships_in_movie(hp4, verbs)
    ans.to_csv('hp4.csv')

    call_me = Movie("Call Me by Your Name",2017)
    ans = pc.compute_relationships_in_movie(call_me.cast,call_me.plot, verbs)
    ans.to_csv('call_me.csv')

    lebowski = Movie("The Big Lebowski",1998)
    ans = pc.compute_relationships_in_movie(lebowski.cast,lebowski.plot, verbs)
    ans.to_csv('lebowski.csv')

    print(ans)


if __name__ == "__main__":
    main()
