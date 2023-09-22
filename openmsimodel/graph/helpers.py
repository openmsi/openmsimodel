from yfiles_jupyter_graphs import GraphWidget
import networkx as nx
from webcolors import name_to_hex


def launch_graph_widget(g):
    if type(g) == str:
        g = nx.Graph(nx.nx_pydot.read_dot(g))
    elif g.__class__.__name__ == "AGraph":
        g = nx.nx_agraph.from_agraph(g)

    def node_color_mapping(index, node):
        try:
            color = node["properties"]["color"]
        except:
            color = "white"
        return name_to_hex(color)

    w = GraphWidget(graph=g)
    w.set_node_color_mapping(node_color_mapping)
    w.directed = True
    w.show()
