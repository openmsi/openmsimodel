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
        graph_source = nx.read_graphml(graphml_filename)
        for n, d in graph_source.nodes(data=True):
            d.update(json.loads(d.pop("object", "{}")))
        return OpenMSIWidget(graph=graph_source)

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


def launch_graph_widget(graph_source, engine="yfiles"):
    print("Launching {}".format(graph_source))
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
        graph_source.__class__ is not None and graph_source.__class__.__name__ == "AGraph"
    ):  # passing a graph object of type AGraph from PyGraphviz
        graph_source = nx.nx_agraph.from_agraph(graph_source)

    if engine == "yfiles":
        w = GraphWidget(graph=graph_source)
        w.set_node_color_mapping(color_mapping)
        w.directed = True
        w.hierarchic_layout()
        w.show()
    elif engine == "cytoscape":
        display(OpenMSIWidget.from_graphml(graph_source))
        # graph_source = nx.cytoscape_data(graph_source)
        # cytoscapeobj = ipycytoscape.CytoscapeWidget()
        # cytoscapeobj.graph.add_graph_from_json(graph_source["elements"])

        # # # Add nodes from the graph data to the Cytoscape widget
        # for node_data in graph_source["elements"]["nodes"]:
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
