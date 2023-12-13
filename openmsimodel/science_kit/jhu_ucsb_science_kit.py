import networkx as nx
from pathlib import Path
from gemd.json import GEMDJson
import os
import shutil
import json

from openmsimodel.science_kit.science_kit import ScienceKit
from openmsimodel.graph.open_graph import OpenGraph


class JhuUcsbHTMDECScienceKit(ScienceKit):
    def __init__(self, root, output):
        ScienceKit.__init__(self)
        self.root = Path(root)
        self.output = Path(output)
        self.encoder = GEMDJson()
        self.record_ids = {
            "F072": [
                2255,
                2256,
                2257,
                2258,
                2272,
                2273,
                2274,
                2275,
                2287,
                2288,
                2292,
                2293,
                2294,
                2295,
                2296,
            ],
            "F086": [2135, 2136],
            "F104": [
                2062,
                2063,
                2064,
                2065,
                2066,
                2067,
                2068,
                2069,
                2070,
                2071,
                2072,
                2073,
                2074,
                2075,
                2076,
                2077,
                2078,
                2079,
                2080,
                2081,
                2082,
                2083,
                2084,
                2085,
                2086,
                2087,
                2088,
                2089,
                2090,
                2091,
                2092,
                2093,
                2094,
                2095,
                2096,
                2097,
                2098,
                2099,
                2100,
                2101,
                2102,
                2103,
                2104,
                2105,
                2106,
                2107,
                2108,
                2109,
                2110,
            ],
            "F105": [1497],
        }

    def build(self):
        # Gather all the laser shock knowledge
        open_graph = OpenGraph("laser_shock", source=self.root, output=self.output)
        all_G, all_relabeled_G, all_name_mapping = open_graph.build_graph()

        # Find the HTMDEC samples
        for sample_id in self.record_ids.keys():
            dest = self.output / sample_id
            if os.path.exists(dest):
                shutil.rmtree(dest)
            os.makedirs(dest)
            for record_id in self.record_ids[sample_id]:
                with open(
                    self.root
                    / "LaserShockLaunchPackage_recordId_{}.json".format(record_id),
                    "r",
                ) as f:
                    # obj = self.encoder.load(f)
                    obj = json.load(f)
                identifier = obj["uids"]["auto"]
                subgraph = OpenGraph.extract_subgraph(
                    all_G, all_name_mapping[identifier], [nx.descendants, nx.ancestors]
                )
                subgraph.name = all_name_mapping[identifier]
                # for node in subgraph.nodes:
                #     # self.
                #     recursive_foreach(node["object"], self.local_out)
                OpenGraph.save_graph(dest, subgraph, None, name=str(subgraph.name))

        # extend them with UCSB/Tim's work

    @classmethod
    def get_command_line_arguments(cls):
        superargs, superkwargs = super().get_command_line_arguments()
        args = [
            *superargs,
            "root",
            "output",
            # "iteration",
            # "synthesis_path",
            # "srjt_path",
        ]
        kwargs = {**superkwargs}
        return args, kwargs

    @classmethod
    def run_from_command_line(cls, args=None):
        parser = cls.get_argument_parser()
        args = parser.parse_args(args=args)
        science_kit = cls(args.root, args.output)
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
