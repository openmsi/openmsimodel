from yfiles_jupyter_graphs import GraphWidget
import networkx as nx
from webcolors import name_to_hex
import ipycytoscape
import traitlets
import ipywidgets
import IPython
import json

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


class OpenMSIWidget(traitlets.HasTraits):
    cyto_widget = traitlets.Instance(ipycytoscape.CytoscapeWidget)
    json_display = traitlets.Instance(ipywidgets.Output)
    graph = traitlets.Any()

    @classmethod
    def from_graphml(self, graphml_filename):
        g = nx.read_graphml(graphml_filename)
        for n, d in g.nodes(data=True):
            d.update(json.loads(d.pop("object", "{}")))
        return OpenMSIWidget(graph=g)

    @traitlets.default("json_display")
    def _default_json_display(self):
        return ipywidgets.Output()

    @traitlets.default("cyto_widget")
    def _default_cyto_widget(self):
        cw = ipycytoscape.CytoscapeWidget(ipywidgets.Layout(width="70%"))
        cw.graph.add_graph_from_networkx(self.graph)
        cw.set_style(_style)

        def update_json(node):
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


def color_mapping(index, node):
    try:
        color = node["properties"]["color"]
    except:
        color = "white"
    return name_to_hex(color)


def launch_graph_widget(g, engine="yfiles"):
    print("Launching {}".format(g))
    if type(g) == str:
        if g.endswith(".dot"):
            dot = nx.nx_pydot.read_dot(g)
            g = nx.Graph(dot)
        elif g.endswith(".graphml"):
            if engine == "yfiles":
                g = nx.read_graphml(g)
    elif type(g) == list:
        merged_graph = nx.read_graphml(g[0])
        for i in range(1, len(g)):
            next_graph = g[i]
            next_graph_ml = nx.read_graphml(next_graph)
            merged_graph = nx.compose(merged_graph, next_graph_ml)
        g = merged_graph
    elif g.__class__ is not None and g.__class__.__name__ == "AGraph":
        g = nx.nx_agraph.from_agraph(g)

    if engine == "yfiles":
        w = GraphWidget(graph=g)
        w.set_node_color_mapping(color_mapping)
        w.directed = True
        w.hierarchic_layout()
        w.show()
    elif engine == "cytoscape":
        display(OpenMSIWidget.from_graphml(g))
        # g = nx.cytoscape_data(g)
        # cytoscapeobj = ipycytoscape.CytoscapeWidget()
        # cytoscapeobj.graph.add_graph_from_json(g["elements"])

        # # # Add nodes from the graph data to the Cytoscape widget
        # for node_data in g["elements"]["nodes"]:
        #     print(node_data)
        #     break

        # cytoscapeobj.set_style(
        #     [
        #         {
        #             "selector": "node",
        #             "id": "data(name)",
        #             "css": {"background-color": "data(color)"},
        #         },
        #         {"selector": "edge", "css": {"line-color": "pink"}},
        #     ]
        # )

        # display(cytoscapeobj)
