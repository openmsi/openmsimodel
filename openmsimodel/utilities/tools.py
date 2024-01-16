import json
import networkx as nx
from collections import defaultdict
import shutil
import os
from gemd.util.impl import recursive_foreach
from gemd.json import GEMDJson

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.colors as colors
import matplotlib.cm as cmx
import matplotlib.patches as mpatches
from matplotlib import pylab
from pathlib import Path

# _encoder = None
# _subdirpath = None


def out(item):
    """
    function object to run on individual item during recursion
    :param item: json item to write its destination
    """
    fn = "_".join([item.__class__.__name__, item.name, item.uids["auto"], ".json"])
    with open(os.path.join(_subdirpath, fn), "w") as fp:
        fp.write(_encoder.thin_dumps(item, indent=3))


def handle_value(G, uid, attributes):
    # TODO: add pointing to templates?
    for att in attributes:
        if att["type"] == "property_and_conditions":
            value = att["property"]["value"]
            att_name = att["property"]["name"]
        else:
            value = att["value"]
            att_name = att["name"]

        if value["type"] == "nominal_real":
            node_name = "{}, {} {}".format(att_name, value["nominal"], value["units"])
            G.add_node(node_name, shape="rectangle", color="orange")
            G.add_edge(uid, node_name)
            # G.add_edge(node_name, uid)
        if value["type"] == "nominal_categorical":
            node_name = "{}, {}".format(att_name, value["category"])
            G.add_node(node_name, shape="rectangle", color="orange")
            # G.add_edge(node_name, uid)
            G.add_edge(uid, node_name)


def handle_attributes(G, uid, obj_data, object_class, obj_state):
    if "parameters" in obj_data:
        handle_value(G, uid, obj_data["parameters"])
    if "properties" in obj_data:
        handle_value(G, uid, obj_data["properties"])
    if "conditions" in obj_data:
        handle_value(G, uid, obj_data["conditions"])


def handle_gemd_obj(G, uid, obj_data, obj_type, obj_state, add_attributes):
    if obj_type.startswith("process"):
        if obj_type.endswith(obj_state):
            G.add_node(uid, color="red")
            if add_attributes:
                handle_attributes(G, uid, obj_data, "process", obj_state)
    elif obj_type.startswith("ingredient"):  # TODO if node doesn't exist, create?
        if obj_type.endswith(obj_state):
            G.add_node(uid, color="blue")
            process = obj_data["process"]["id"]
            G.add_edge(uid, process)
            if add_attributes:
                handle_attributes(G, uid, obj_data, "ingredient", obj_state)
            if "material" in obj_data and obj_data["material"]:
                material = obj_data["material"]["id"]
                G.add_edge(material, uid)
    elif obj_type.startswith("material"):
        if obj_type.endswith(obj_state):
            G.add_node(uid, color="green")
            if add_attributes:
                handle_attributes(G, uid, obj_data, "material", obj_state)
            # if "process" in obj_data and obj_data["process"]:
            if obj_data["process"] and obj_data["process"]:
                process = obj_data["process"]["id"]
                G.add_edge(process, uid)  # ?
    elif obj_type.startswith("measurement"):
        if obj_type.endswith(obj_state):
            G.add_node(uid, color="purple")
            if add_attributes:
                handle_attributes(G, uid, obj_data, "measurement", obj_state)
            if "material" in obj_data and obj_data["material"]:
                material = obj_data["material"]["id"]
                G.add_edge(uid, material)


def save_graph(graph, file_name):
    plt.figure(num=None, figsize=(20, 20), dpi=80)
    plt.axis("off")
    fig = plt.figure(1)
    pos = nx.spring_layout(graph)
    nx.draw_networkx_nodes(graph, pos)
    nx.draw_networkx_edges(graph, pos)
    nx.draw_networkx_labels(graph, pos)

    cut = 1.00
    xmax = cut * max(xx for xx, yy in pos.values())
    ymax = cut * max(yy for xx, yy in pos.values())
    plt.xlim(0, xmax)
    plt.ylim(0, ymax)

    plt.savefig(file_name, bbox_inches="tight")
    pylab.close()
    del fig


"""helper to extract GEMD data from all scenarios, whether folder of JSONs or single JSON, thin or full, etc.
    it raises IOError in case the data can't be properly extracted.
    """


def read_gemd_data(dirpath, encoder):
    """helper to extract GEMD data from all scenarios, whether folder of JSONs or single JSON, thin or full, etc.
    it raises IOError in case the data can't be properly extracted.

    Args:
        dirpath (str, Path): path to directory or file containing GEMD knowledge
        encoder (GEMDJson): GEMD encoder

    Raises:
        IOError: if folder or file doesn't match the criteria

    Returns:
        list: all gemd objects extracted from folder or file
    """
    gemd_objects = []
    gemd_paths = []
    # try:
    if True:
        if type(dirpath) == list:
            print("Extracting list...")
            for obj in dirpath:
                gemd_objects.append(json.loads(encoder.thin_dumps(obj)))
        elif os.path.isdir(dirpath):
            print("Extracting folder...")
            for dp, dn, filenames in os.walk(dirpath):
                for f in filenames:
                    if f.endswith(".json"):
                        path = os.path.join(dp, f)
                        with open(path) as fp:
                            gemd_objects.append(json.load(fp))
                            gemd_paths.append(Path(path))
        elif os.path.isfile(dirpath) and str(dirpath).endswith(".json"):
            print("Extracting file...")
            if f.endswith(".json"):
                with open(dirpath) as fp:
                    gemd_objects = json.load(fp)

            #     gemd_objects = json.load(fp)
    # except:
    #     raise IOError(  # FIXME
    #         f"couldn't extract GEMD data. Expected folder of JSONs or single JSON with 1+ objects. "
    #     )
    if len(gemd_objects) == 0:  # FIXME: better message, like filenotfound
        raise ValueError(f"Couldn't extract any gemd object from {dirpath}. ")
    return gemd_objects, gemd_paths


def plot_graph(
    dirpath, obj_state="run", objectpath=None, tmp="tmp", add_attributes=False
):
    """
    creates a NetworkX graph representation of the GEMD relationships by reading every object
    generated by the GEMDEncoder object, storing all of its links by uid, and forming directed relationships,
    such as ingredient->process, or process->material
    It then allows filtering the objects mapped (i.e., removing spec or runs,
    measurements or ingredients) and saves a NetworkX graph in "dot" as .png

    :param dirpath: source of graph
    :param obj_state: to plot a graph of specs, runs or templates
    """
    G = nx.DiGraph()
    object_mapping = defaultdict()
    name_mapping = defaultdict()
    encoder = GEMDJson()
    nb_disregarded = 0

    if objectpath:  # plotting a graph from a single, full json (!= thin)
        with open(objectpath) as fp:
            object = encoder.load(fp)
    else:  # plotting a graph from a bunch of thin jsons
        gemd_objects = [
            os.path.join(dp, f)
            for dp, dn, filenames in os.walk(dirpath)
            for f in filenames
            if f.endswith(".json")
        ]
    if len(gemd_objects) == 0:
        return

    # adding objects to graph one by one
    for i, obj in enumerate(gemd_objects):
        if "raw_jsons" in obj:
            continue
        fp = open(obj, "r")
        obj_data = json.load(fp)
        obj_type = obj_data["type"]
        if (
            obj_type.startswith("parameter")
            or obj_type.startswith("condition")
            or obj_type.startswith("property")
        ):
            nb_disregarded += 1
            continue
        obj_uid = obj_data["uids"]["auto"]
        obj_name = obj_data["name"]
        name_mapping[obj_uid] = "{},  {}".format(obj_name, obj_uid[:3])
        handle_gemd_obj(G, obj_uid, obj_data, obj_type, obj_state, add_attributes)
        if i % 1000 == 0:
            print("{} gemd objects processed...".format(i))

    # converting to grapviz
    _relabeled_G = nx.relabel_nodes(G, name_mapping)

    relabeled_G = nx.nx_agraph.to_agraph(_relabeled_G)
    relabeled_G.node_attr.update(nodesep=0.4)
    relabeled_G.node_attr.update(ranksep=1)

    relabeled_G.layout(prog="dot")

    # plotting
    relabeled_G.draw(os.path.join(dirpath, "{}_graph.svg".format(obj_state)))
    plt.close()
    with open(os.path.join(dirpath, "{}_graph.dot".format(obj_state)), "x") as f:
        f.write(str(relabeled_G))

    # info
    print("cycles in the graph: {}".format(list(nx.simple_cycles(G))))
    print(
        "nb of disregarded elements (i.e., templates/specs): {}/{}".format(
            nb_disregarded, len(gemd_objects)
        )
    )
