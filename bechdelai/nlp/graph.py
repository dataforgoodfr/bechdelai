
import itertools
from typing import Dict, List

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from pylab import rcParams


def get_edges_df(count_dict: Dict[str, int], entity_mapping: Dict[str, str]) -> pd.DataFrame:
    """Get the edges of the graph from a dict of counts.

    Args:
        count_dict (Dict[str, int]): The counts of interactions
        entity_mapping (Dict[str, str]): The mapping of the entities to their group

    Returns:
        pd.DataFrame: The edges dataframe of the graph
    """
    return pd.DataFrame([(entity_mapping.get(a, a), entity_mapping.get(b, b), c) for (a,b),c in zip(count_dict.keys(), count_dict.values()) if a != b], columns = ['source', 'target', 'weight'])  


def coocurrence_graph(doc, entity_mapping: Dict[str, str]) -> nx.Graph:
    """Get an entity coocurrence graph.

    Args:
        doc (_type_): The document to analyze
        entity_mapping (Dict[str, str]): The mapping of the entities to their group

    Returns:
        pd.DataFrame: The edges of the graph
    """
    relations = {}
    for s in doc.sents:
        ent_text = [entity_mapping.get(e.text, e.text) for e in s.ents if e.label_ in ["PERSON", "ORG", "GPE", "LOC"]]
        if len(ent_text) > 1:
            for ent_a, ent_b in itertools.combinations(ent_text, 2):
                k = tuple(sorted((ent_a, ent_b)))
                if relations.get((ent_a, ent_b)) is None:
                    relations[k] = 1
                else:
                    relations[k] = relations[k] + 1
    edges_df = get_edges_df(relations, entity_mapping)
    return build_graph(edges_df)

def build_graph(edges_df: pd.DataFrame) -> nx.Graph:
    """Build the graph.

    Args:
        edges_df (_type_): The edges of the graph

    Returns:
        nx.Graph: The graph
    """
    return nx.from_pandas_edgelist(edges_df, edge_attr = True)

def regrouped_entites_graph(count_dict: Dict[str, int], entity_mapping: Dict[str, str]) -> nx.Graph:
    """Get the graph of the regrouped entities.

    Args:
        count_dict (Dict[str, int]): The counts of interactions
        entity_mapping (Dict[str, str]): The mapping of the entities to their group

    Returns:
        nx.Graph: The graph
    """
    modifiers_df = get_edges_df(count_dict, entity_mapping)
    return build_graph(modifiers_df)
    


def visualize_graph(G, name) -> None:
    """Visualize the graph.

    Args:
        edges_df (_type_): The edges of the graph
    """
    plt.figure()
    plt.title(name)
    rcParams['figure.figsize'] = 14, 10
    labels = nx.get_edge_attributes(G, 'weight')
    pos = nx.spring_layout(G, scale=20, k=3/np.sqrt(G.order()))
    d = dict(G.degree)
    nx.draw(
        G, 
        pos,
        node_color='lightblue', 
        alpha = 0.75,
        with_labels=True, 
        nodelist=d, 
        node_size=[d[k]*200 for k in d],
        edgelist = labels
    )
    nx.draw_networkx_edge_labels(G,pos,edge_labels=labels)
    plt.show()


def pagerank_algorithm(G) -> None:
    """Run the pagerank algorithm.

    Args:
        G (_type_): The graph to run the algorithm on
    """
    pr = nx.pagerank(G)
    pr = {k: v for k, v in sorted(pr.items(), reverse = True, key=lambda item: item[1])}
    pr_df = pd.DataFrame([pr]).T.reset_index().rename(columns = {0 : 'pr', 'index' : 'name'})

    # visualize page rank to see character importance
    plt.figure()
    plt.barh(y = pr_df['name'].head(10), width = pr_df['pr'].head(10))
    plt.title("Page Rank of the Network")
    plt.ylabel("Characters")
    plt.xlabel("Page Rank Score")
    plt.show()
