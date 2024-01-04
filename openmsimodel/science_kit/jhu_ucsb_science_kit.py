import networkx as nx
from pathlib import Path
from gemd.json import GEMDJson
import os
import shutil
import json
import csv
from datetime import datetime
import networkx as nx

from openmsimodel.science_kit.science_kit import ScienceKit
from openmsimodel.graph.open_graph import OpenGraph


def extract_record_ids(csv_file_path):
    # Initialize an empty dictionary to store the mapping
    flyer_id_to_record_ids = {}
    record_ids_to_metadata = {}

    # Open the CSV file and read its contents
    with open(csv_file_path, mode="r") as csv_file:
        csv_reader = csv.DictReader(csv_file)

        # Iterate through each row in the CSV
        for row in csv_reader:
            flyer_id = str(row["Flyer ID"])
            record_id = str(row["recordId"])
            try:
                date = datetime.strptime(str(row["Date"]), "%m/%d/%Y")
            except ValueError as e:
                print(e)
                continue
            record_ids_to_metadata[record_id] = date
            # Check if the Flyer ID is already a key in the dictionary
            if flyer_id.startswith("F"):
                if flyer_id in flyer_id_to_record_ids:
                    # Append the record ID to the existing list
                    flyer_id_to_record_ids[flyer_id].append(record_id)
                else:
                    # Create a new list with the record ID as the first element
                    flyer_id_to_record_ids[flyer_id] = [record_id]

    return flyer_id_to_record_ids, record_ids_to_metadata


class JhuUcsbHTMDECScienceKit(ScienceKit):
    def __init__(self, root, output, launch_pkg_filemaker_path):
        ScienceKit.__init__(self)
        self.root = Path(root)
        self.output = Path(output)
        self.encoder = GEMDJson()
        self.flyer_id_to_record_ids, self.record_ids_to_metadata = extract_record_ids(
            launch_pkg_filemaker_path
        )

    def build(self):
        structured_data = []

        # Gather all the laser shock knowledge
        open_graph = OpenGraph("laser_shock", source=self.root, output=self.output)
        all_G, all_relabeled_G, all_name_mapping = open_graph.build_graph()

        # Find the HTMDEC samples
        for sample_id in self.flyer_id_to_record_ids.keys():
            dest = self.output / sample_id
            if os.path.exists(dest):
                shutil.rmtree(dest)
            os.makedirs(dest)
            for record_id in self.flyer_id_to_record_ids[sample_id]:
                try:
                    with open(
                        self.root
                        / "LaserShockLaunchPackage_recordId_{}.json".format(record_id),
                        "r",
                    ) as f:
                        obj = json.load(f)
                except Exception as e:
                    print(e)
                    continue
                identifier = obj["uids"]["auto"]
                subgraph = OpenGraph.extract_subgraph(
                    all_G, all_name_mapping[identifier], [nx.descendants, nx.ancestors]
                )
                subgraph.name = all_name_mapping[identifier]
                structured_data.append(
                    [subgraph, self.record_ids_to_metadata[record_id]]
                )
                OpenGraph.save_graph(dest, subgraph, None, name=str(subgraph.name))

        # # build final graph
        # structured_data = sorted(structured_data, key=lambda x: x[1])

        # structured_graph = nx.Graph()
        # for i in range(len(structured_data) - 1):
        #     G = structured_data[i][0]
        #     date = structured_data[i][1]
        #     if structured_graph:
        #         last_node_merged = max(structured_graph.nodes)
        #         first_node_G = min(G.nodes)
        #         edge_metadata = {
        #             "order": i,
        #             "date": str(date),
        #             "from": from_name,
        #             "to": G.name,
        #         }
        #         # # Check if the edge already exists
        #         # if structured_graph.has_edge(last_node_merged, first_node_G):
        #         #     # Update edge metadata if the edge exists
        #         #     structured_graph[last_node_merged][first_node_G].update(
        #         #         edge_metadata
        #         #     )
        #         # else:
        #         #     # Add the edge if it doesn't exist
        #         #     structured_graph.add_edge(
        #         #         last_node_merged, first_node_G, **edge_metadata
        #         #     )
        #         structured_graph.add_edge(
        #             last_node_merged, first_node_G, **edge_metadata
        #         )
        #     structured_graph = nx.compose(structured_graph, G)
        #     from_name = G.name

        # OpenGraph.save_graph(
        #     self.output, structured_graph, None, name="structured_graph"
        # )

    @classmethod
    def get_command_line_arguments(cls):
        superargs, superkwargs = super().get_command_line_arguments()
        args = [
            *superargs,
            "root",
            "output",
            "launch_pkg_filemaker_path",
        ]
        kwargs = {**superkwargs}
        return args, kwargs

    @classmethod
    def run_from_command_line(cls, args=None):
        parser = cls.get_argument_parser()
        args = parser.parse_args(args=args)
        science_kit = cls(args.root, args.output, args.launch_pkg_filemaker_path)
        # science_kit = cls(**args)
        science_kit.build()

        # with open(os.path.join(args.output, "log.txt"), "w") as sys.stderr:
        #     science_kit.build()
        # science_kit.encoder.dumps(
        #     science_kit.terminal_process
        # )
        # science_kit.thin_dumps(science_kit.terminal_process)
        # science_kit.dumps(science_kit.terminal_process)
        # science_kit.thin_structured_dumps()


def main(args=None):
    """
    Main method to run from command line
    """
    JhuUcsbHTMDECScienceKit.run_from_command_line(args)


if __name__ == "__main__":
    main()
