"""Srt analysis functions"""
from itertools import permutations

import neuralcoref
import spacy
from flair.data import Sentence
from flair.models import SequenceTagger

# load the NER tagger
tagger = SequenceTagger.load("ner")

# Load neuralcoref model
nlp = spacy.load("en_core_web_sm")
neuralcoref.add_to_pipe(nlp)


def merge_if_in(elements):
    """Merge elements if start and end intersects"""
    delete_i = []
    for i, j in permutations(range(len(elements)), 2):
        if i in delete_i:
            continue
        e1 = elements[i]
        e2 = elements[j]

        start1, end1 = e1[1], e1[2]
        start2, end2 = e2[1], e2[2]

        if (start1 <= start2 <= end1) & (start1 <= end2 <= end1):
            delete_i.append(j)

    return [e for (i, e) in enumerate(elements) if i not in delete_i]


def extract_keyword(txt):
    """Extract wanted entities"""
    # make a sentence
    sentence = Sentence(txt)

    # run NER over sentence
    tagger.predict(sentence)

    # Run spacy en + neuralcoref
    doc = nlp(txt)

    vocab = list(
        map(
            lambda x: (x.text, x.start, x.end, x.root.pos_),  # x.root.pos_
            doc._.coref_scores.keys(),
        )
    )
    vocab = list(
        filter(
            lambda x: x[3] in ["NOUN", "PRON", "PROPN"],
            vocab
            # lambda x: x[3] in ["PRON", "PROPN"], vocab
        )
    )
    entities = list(
        filter(lambda x: x.tag in ["PER", "MISC"], sentence.get_spans("ner"))
    )
    entities = [
        (e.text, e.tokens[0].idx - 1, e.tokens[-1].idx, e.tag) for e in entities
    ]
    entities += vocab
    entities = merge_if_in(entities)

    return entities


def word_is_synonym_of_person(txt, person_syn_dict):
    """If contains a word that match to a person then
    returns the word else return False
    """
    for s in txt.split():
        if s.lower() in person_syn_dict:
            return s.lower()

    return False
