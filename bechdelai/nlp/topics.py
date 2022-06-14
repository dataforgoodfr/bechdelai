from typing import List

from gensim.corpora.dictionary import Dictionary
from gensim.models import LdaMulticore
from sklearn.feature_extraction.text import TfidfVectorizer


def gensim_topic_modeling(tokens: List[str]):
    dictionary = Dictionary(tokens)
    dictionary.filter_extremes(no_below=5, no_above=0.5, keep_n=1000)
    corpus = [dictionary.doc2bow(doc) for doc in tokens]
    lda_model = LdaMulticore(corpus=corpus, id2word=dictionary, iterations=50, num_topics=10, workers = 4, passes=10)
    return lda_model



def tfidf_topic_modeling(tokens: List[str],):
    vectorizer = TfidfVectorizer(min_df=3, max_df=0.5, ngram_range=(1,3), max_features=50, stop_words='english')
    vectorizer.fit(tokens)
    return vectorizer.get_feature_names_out()
