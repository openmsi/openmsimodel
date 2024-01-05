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
        g = nx.cytoscape_data(g)
        cytoscapeobj = ipycytoscape.CytoscapeWidget()
        cytoscapeobj.graph.add_graph_from_json(g["elements"])
        # cytoscapeobj.graph_data = g  # .add_graph_from_json(g["elements"])

        # # Add nodes from the graph data to the Cytoscape widget
        for node_data in g["elements"]["nodes"]:
            print(node_data)
            break
        #     node_id = node_data["data"]["id"]
        #     node_style = {
        #         "background-color": node_data["data"].get("color", "gray"),
        #         "shape": node_data["data"].get("shape", "ellipse"),
        #     }
        #     cytoscapeobj.graph.add_node(node_id, **node_style)

        # # Add edges from the graph data to the Cytoscape widget
        # for edge_data in g["elements"]["edges"]:
        #     edge_id = edge_data["data"]["id"]
        #     source_id = edge_data["data"]["source"]
        #     target_id = edge_data["data"]["target"]
        #     cytoscapeobj.graph.add_edge(source_id, target_id, id=edge_id)

        cytoscapeobj.set_style(
            [
                # {"selector": "node", "css": {"background-color": "red"}},
                {
                    "selector": "node",
                    "id": "data(name)",
                    "css": {"background-color": "data(color)"},
                },
                {"selector": "edge", "css": {"line-color": "pink"}},
            ]
        )

        display(cytoscapeobj)

        # print(cytoscapeobj)
        # nx.cytoscape_data(G)
        # cy.layout.apply(name="force-directed")
