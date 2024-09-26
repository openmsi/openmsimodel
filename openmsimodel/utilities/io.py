import json
import os
from pathlib import Path
import glob
import networkx as nx
import time

def from_graphml(graphml_filename):
    if not os.path.exists(graphml_filename):
        raise FileNotFoundError(f"GraphML file '{graphml_filename}' not found.")
    time.sleep(1)
    graph_source = nx.read_graphml(graphml_filename)
    for n, d in graph_source.nodes(data=True):
        d.update(json.loads(d.pop("object", "{}")))
    return graph_source

def read_graphml_from_folder(graphml_folder):
    target = graphml_folder + "/*.graphml"
    graphml_filenames = glob.glob(target)
    entire_graph = nx.DiGraph()
    for graphml_filename in graphml_filenames:
        individual_graph = from_graphml(graphml_filename)
        entire_graph.add_nodes_from(individual_graph.nodes(data=True))
        entire_graph.add_edges_from(individual_graph.edges(data=True))
    return entire_graph

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