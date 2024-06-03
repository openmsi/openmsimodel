import ipycytoscape
import traitlets
import ipywidgets
import IPython
import networkx as nx
import json
import glob
import os
from openmsimodel.utilities.io import from_graphml, read_graphml_from_folder

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


class OpenGraphWidget(traitlets.HasTraits):
    cyto_widget = traitlets.Instance(ipycytoscape.CytoscapeWidget)
    json_display = traitlets.Instance(ipywidgets.Output)
    graph = traitlets.Any()

    @classmethod
    def from_graphml_folder(cls, graphml_folder):
        entire_graph = read_graphml_from_folder(graphml_folder)
        return OpenGraphWidget(graph=entire_graph)

    @classmethod
    def from_graphml(cls, graphml_filename):
        graph_source = from_graphml(graphml_filename)
        return OpenGraphWidget(graph=graph_source)

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
