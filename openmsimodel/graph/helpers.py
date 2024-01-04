from yfiles_jupyter_graphs import GraphWidget
import networkx as nx
from webcolors import name_to_hex
from py2cytoscape import cyrest
import ipycytoscape
import json


def launch_graph_widget(g, engine="yfiles"):
    print("Launching {}".format(g))
    if type(g) == str:
        if g.endswith(".dot"):
            dot = nx.nx_pydot.read_dot(g)
            g = nx.Graph(dot)
        elif g.endswith(".graphml"):
            g = nx.read_graphml(g)
    elif g.__class__ is not None and g.__class__.__name__ == "AGraph":
        g = nx.nx_agraph.from_agraph(g)

    def node_color_mapping(index, node):
        try:
            color = node["properties"]["color"]
        except:
            color = "white"
        return name_to_hex(color)

    def edge_color_mapping(index, node):
        try:
            color = node["properties"]["color"]
        except:
            color = "white"
        return name_to_hex(color)

    if engine == "yfiles":
        w = GraphWidget(graph=g)
        w.set_node_color_mapping(node_color_mapping)
        w.directed = True
        w.hierarchic_layout()
        w.show()
    elif engine == "cytoscape":
        cytoscapeobj = ipycytoscape.CytoscapeWidget()
        g = nx.cytoscape_data(g)
        # print(type(g))
        # print(g.nodes.keys())
        # print(g.nodes["Cake [cake-d576929a6c518c058db29324c13db0c3, material_run]"])
        # print(g)
        cytoscapeobj.graph_data = g
        display(cytoscapeobj)
        # nx.cytoscape_data(G)
        # cy.layout.apply(name="force-directed")
