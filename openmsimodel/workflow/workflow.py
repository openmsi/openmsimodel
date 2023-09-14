from pathlib import Path
from collections import defaultdict
import os
import shutil
import argparse
from .folder_or_file import FolderOrFile

# import sys
# sys.path.append("..")
# from openmsimodel.utilities.tools import *
from openmsimodel.utilities.runnable import Runnable
from openmsimodel.utilities.argument_parsing import OpenMSIModelParser

from gemd.json import GEMDJson
from gemd.util.impl import recursive_foreach


# TODO: extend Logging
class Workflow(Runnable):
    """Class to model a workflow, typically a set of processing steps, experiments, and characterizations, into GEMD, a data model.
    the definition of a workflow is meant to be flexible to the needs of the user. Workflows can be composed
    to construct even larger GEMD graphs.
    It offers utilities functions to build the model flexibly, break it down into smaller, easier to
    manage blocks, or complete operations such as dumping and loading models into/from JSONs.
    """

    ARGUMENT_PARSER_TYPE = OpenMSIModelParser

    def __init__(self, *args, **kwargs):
        """Initialization of workflow"""
        # self.root
        self.elements = []
        self.subs = defaultdict()
        self.terminal_subs = defaultdict()
        # self.blocks = defaultdict()
        # self.terminal_blocks = defaultdict()
        # self.encoder = GEMDJson()
        # if "output" in args:
        #     self.output = args.output

    def build(self):
        """
        This function builds the entire GEMD model that represents a certain Workflow.
        to be overwritten by child objects of Workflow that correspond to a specific workflow / user case.
        """
        pass

    def thin_dumps(self):
        """
        dumps the entire model into a JSON per object, each representing the 'thin' version' of the object
        in which pointers (i.e., true value) are replaced by links (e.g., uuid).
        """
        pass

    def dumps(self):
        """
        dumps the entire model into a single JSON, which contains all the model objects with data pointers (!= links).
        """
        pass

    def thin_loads(self):
        """
        loads the entire model from a list of JSONs, each representing the 'thin' version' of the model object
        in which pointers (i.e., true value) are replaced by links (e.g., uuid).
        """
        pass

    def loads(self):
        """
        loads the entire model from a single JSON, which contains all the model objects with data pointers (!= links)
        """
        pass

    def print_encoded(self, obj):
        """
        prints the passed GEMD object into a nicely readable full JSON
        :param obj: the object to print
        """
        print(self.encoder.dumps(obj, indent=3))

    def print_thin_encoded(self, obj):
        """
        prints the passed GEMD object into a nicely readable 'thin' JSON
        :param obj: the object to print
        """
        print(self.encoder.thin_dumps(obj, indent=3))

    # def thin_dumps_single_obj(self, obj):
    #     """
    #     :param obj: the object to print
    #     """
    #     self.thin_dumps_obj_dest = os.path.join(self.destination, obj._run.name)
    #     if os.path.exists(self.thin_dumps_obj_dest):
    #         shutil.rmtree(self.thin_dumps_obj_dest)
    #     os.makedirs(self.thin_dumps_obj_dest)
    #     for _obj in [obj._spec, obj._run]:
    #         recursive_foreach(_obj, self.out)
    #     plot_graph(self.thin_dumps_obj_dest)
    #     plot_graph(self.thin_dumps_obj_dest, obj_state == "spec")

    def local_out(self, item):
        """
        function object to run on individual item during recursion
        :param item: json item to write its destination
        se
        """
        fn = "_".join([item.__class__.__name__, item.name, item.uids["auto"], ".json"])
        with open(os.path.join(self.local_out_destination, fn), "w") as fp:
            # fp.write(self.encoder.thin_dumps(item, indent=3))
            fp.write(self.f(item, indent=3))

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
        workflow = cls(*args)
        workflow.build()


def main(args=None):
    """
    Main method to run from command line
    """
    Workflow.run_from_command_line(args)


if __name__ == "__main__":
    main()
