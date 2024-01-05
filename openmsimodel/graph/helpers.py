from yfiles_jupyter_graphs import GraphWidget
import networkx as nx
from webcolors import name_to_hex
import ipycytoscape
import ipywidgets
import traitlets
import json
import IPython.display


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
        color = node.get("properties", {}).get("color", "white")
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


_style = [
    {
        "selector": "node",
        "css": {
            "content": "data(name)",
            "text-valign": "center",
            "background-color": "data(color)",
        },
    },
    {"selector": "node:parent", "css": {"background-opacity": 0.333}},
    {"selector": "edge", "style": {"width": 4, "line-color": "#9dbaea"}},
    {
        "selector": "edge.directed",
        "style": {
            "curve-style": "bezier",
            "target-arrow-shape": "triangle",
            "target-arrow-color": "#9dbaea",
        },
    },
    {"selector": "edge.multiple_edges", "style": {"curve-style": "bezier"}},
]


class CytoscapeGraphWidget(traitlets.HasTraits):
    cyto_widget = traitlets.Instance(ipycytoscape.CytoscapeWidget)
    json_display = traitlets.Instance(ipywidgets.Output)
    graph = (
        traitlets.Any()
    )  # Would be nice to use a specific class here, which may be a networkx DiGraph.

    @classmethod
    def from_graphml(cls, graphml_filename):
        g = nx.read_graphml(graphml_filename)
        for n, d in g.nodes(data=True):
            d.update(json.loads(d.pop("object", "{}")))
        return cls(graph=g)

    @traitlets.default("json_display")
    def _default_json_display(self):
        return ipywidgets.Output(layout=ipywidgets.Layout(width="30%"))

    @traitlets.default("cyto_widget")
    def _default_cyto_widget(self):
        cw = ipycytoscape.CytoscapeWidget(layout=ipywidgets.Layout(width="70%"))
        cw.graph.add_graph_from_networkx(self.graph)
        cw.set_style(_style)

        def update_json(node):
            import IPython.display

            with self.json_display:
                self.json_display.clear_output(wait=True)
                IPython.display.display(IPython.display.JSON(data=node["data"]))

        cw.on("node", "click", update_json)
        return cw

    def _ipython_display_(self):
        IPython.display.display(
            ipywidgets.HBox(
                [self.cyto_widget, self.json_display],
                layout=ipywidgets.Layout(width="90%"),
            )
        )
