import networkx as nx
import pandas as pd
import os

# Load routes from CSV to build graph
def build_graph(csv_path='data/routes.csv'):
    df = pd.read_csv(csv_path)
    G = nx.Graph()
    for _, row in df.iterrows():
        src = row['source']
        dst = row['destination']
        dist = float(row['distance'])
        G.add_edge(src, dst, weight=dist)
    return G

def find_shortest_route(source, destination, csv_path='data/routes.csv'):
    G = build_graph(csv_path)
    if source not in G.nodes or destination not in G.nodes:
        return None, None
    try:
        route = nx.shortest_path(G, source=source, target=destination, weight='weight')
        distance = nx.shortest_path_length(G, source=source, target=destination, weight='weight')
        return route, distance
    except nx.NetworkXNoPath:
        return None, None
