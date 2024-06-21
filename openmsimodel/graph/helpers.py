from yfiles_jupyter_graphs import GraphWidget
import networkx as nx
from webcolors import name_to_hex
import json
from openmsimodel.graph.open_graph_widget import OpenGraphWidget


def color_mapping(index, node):
    try:
        color = node["properties"]["color"]
    except:
        color = "white"
    return name_to_hex(color)

def launch_graph_widget(graph_source, engine="yfiles"):
    print("Launching widget for {}".format(graph_source))
    if type(graph_source) == str:  # passing a single dot or graphml file
        if graph_source.endswith(".dot"):
            dot = nx.nx_pydot.read_dot(graph_source)
            graph_source = nx.Graph(dot)
        elif graph_source.endswith(".graphml"):
            if engine == "yfiles":
                graph_source = nx.read_graphml(graph_source)
    elif type(graph_source) == list:  # passing a list of graphml files
        merged_graph = nx.read_graphml(graph_source[0])
        for i in range(1, len(graph_source)):
            next_graph = graph_source[i]
            next_graph_ml = nx.read_graphml(next_graph)
            merged_graph = nx.compose(merged_graph, next_graph_ml)
        graph_source = merged_graph
    elif (
        graph_source.__class__ is not None
        and graph_source.__class__.__name__ == "AGraph"
    ):  # passing a graph object of type AGraph from PyGraphviz
        graph_source = nx.nx_agraph.from_agraph(graph_source)

    if engine == "yfiles":
        w = GraphWidget(graph=graph_source)
        w.set_node_color_mapping(color_mapping)
        w.directed = True
        w.hierarchic_layout()
        w.show()
    elif engine == "cytoscape":
        display(OpenGraphWidget.from_graphml(graph_source))
