from yfiles_jupyter_graphs import GraphWidget
import networkx as nx


def launch_graph_widget(g):
    if type(g) == str:
        g = nx.Graph(nx.nx_pydot.read_dot(g))
    elif g.__class__.__name__ == "AGraph":
        g = nx.nx_agraph.from_agraph(g)
    w = GraphWidget(graph=g)
    w.directed = True
    w.show()
