from .folder_or_file import FolderOrFile
from gemd.json import GEMDJson
from collections import defaultdict


# TODO: extend Logging
class Workflow:
    """
    Class to model a workflow, typically a set of processing steps, experiments, and characterizations, into GEMD, a data model.
    It offers utilities functions to build the model flexibly, break it down into smaller, easier to
    manage blocks, or complete operations such as dumping and loading models into/from JSONs.
    """

    def __init__(self, *args, **kwargs):
        self.blocks = defaultdict()
        self.terminal_blocks = defaultdict()
        self.encoder = GEMDJson()
        self.output_folder = kwargs["output_folder"]

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

    def build_model(self):
        """
        This function builds the entire GEMD model that represents a certain Workflow.
        to be overwritten by child objects of Workflow that correspond to a specific workflow / user case.
        """
        pass

    def add_block(self):
        """
        mode 2
        this like to add an existing block seq.
        should link everything
        """

        pass
