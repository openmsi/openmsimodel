from pathlib import Path
from collections import defaultdict
import os
import shutil
import argparse
import json
from typing import Optional

from openmsimodel.utilities.runnable import Runnable
from openmsimodel.utilities.argument_parsing import OpenMSIModelParser
from openmsimodel.utilities.typing import Spec, Run

from gemd.json import GEMDJson
from gemd.util.impl import recursive_foreach


# TODO: extend Logging
class ScienceKit(Runnable):
    """Class to model a science_kit, an all-encompassing structure for your data models, graphs, databases, etc.
    the definition of a science_kit is meant to be flexible to the needs of the user.
    It offers utilities functions to build the model flexibly, break it down into smaller, easier to
    manage blocks, or complete operations such as dumping and loading models into/from JSONs.
    """

    ARGUMENT_PARSER_TYPE = OpenMSIModelParser

    def __init__(self, version="0.0.1"):
        """Initialization of science_kit"""
        self.version = version
        self.elements = []
        self.structures = {}
        self.instruments = {}
        self.open_graphs = {}
        self.open_dbs = {}

    def assets(self):
        if self.structures:
            for structure in self.structures.values():
                self.elements.extend(structure.assets)
        return self.elements

    def build(self):
        """
        This function builds the entire GEMD model that represents a certain ScienceKit.
        to be overwritten by child objects of ScienceKit that correspond to a specific science_kit / user case.
        """
        pass

    def dumps(self):
        """
        dumps the entire model into a JSON per object, each representing the 'thin' version' of the object
        in which pointers (i.e., true value) are replaced by links (e.g., uuid).
        """
        pass

    def loads(self):
        """
        loads the entire model from a list of JSONs, each representing the 'thin' version' of the model object
        in which pointers (i.e., true value) are replaced by links (e.g., uuid).
        """
        pass

    def out(self, item):
        """
        function object to run on individual item during recursion
        :param item: json item to write its destination
        se
        """
        fn = "_".join([item.__class__.__name__, item.name, item.uids["auto"], ".json"])
        with open(os.path.join(self.local_out_destination, fn), "w") as fp:
            fp.write(self.dump_function(item, indent=3))

    @classmethod
    def from_spec_or_run(
        cls,
        name: str,
        *,
        notes: Optional[str] = None,
        spec: Spec = None,
        run: Run = None,
    ):
        initial = MaterialsSequence.from_spec_or_run(
            run.name,
            notes=None,
            spec=spec,
            run=run,
        )

    #################### CLASS METHODS ####################

    @classmethod
    def get_command_line_arguments(cls):
        superargs, superkwargs = super().get_command_line_arguments()
        args = []
        kwargs = {**superkwargs}
        return args, kwargs

    @classmethod
    def run_from_command_line(cls, args=None):
        parser = cls.get_argument_parser()
        args = parser.parse_args(args=args)
        science_kit = cls(*args)
        science_kit.build()


def main(args=None):
    """
    Main method to run from command line
    """
    ScienceKit.run_from_command_line(args)


if __name__ == "__main__":
    main()
