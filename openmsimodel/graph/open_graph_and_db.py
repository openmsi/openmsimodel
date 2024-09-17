

from openmsimodel.graph.open_graph import OpenGraph
from openmsimodel.db.open_db import OpenDB
import questionary

class OpenGraphAndDB(OpenGraph, OpenDB):

    def __init__(self, name, source, output, database_name, private_path, science_kit=None):
        """
        Initialization of OpenGraphAndDB instance.

        :param database_name: Name of the database to connect to.
        :type database_name: str
        :param private_path: Path to a JSON file containing database credentials.
        :type private_path: str
        :param output: Path to the output directory.
        :type output: str
        """
        self.source = source
        self.output = output
        self.open_graph = OpenGraph(name, source, output, science_kit)
        self.open_db = OpenDB(database_name, private_path, output, self.source, science_kit)
        # self.auth = None
        # self.gemd_db = None
        # self.logger = Logger()
        # self.science_kit = science_kit
        # if self.science_kit:
        #     self.science_kit.open_dbs[database_name] = self
        # self.setup(database_name, private_path)

    # @classmethod
    def interactive_mode(self):
        while True:
            choice = questionary.select(
                "Do you want to interact with OpenDB or OpenGraph?",
                choices=["OpenDB", "OpenGraph", "Edit Graph & DB: Add Measurement", "Exit"]
            ).ask()
            
            if choice == "OpenDB":
                self.open_db.interactive_mode()
            elif choice == "OpenGraph":
                self.open_graph.interactive_mode()
            elif choice == "Exit":
                break

    
    @classmethod
    def get_command_line_arguments(cls):
        superargs, superkwargs = super().get_command_line_arguments()
        args = [*superargs, "name", "source", "output", "database_name", "private_path"]
        kwargs = {**superkwargs}
        return args, kwargs

    @classmethod
    def run_from_command_line(cls, args=None):
        parser = cls.get_argument_parser()
        args = parser.parse_args(args=args)
        open_graph_and_db = cls(args.name, args.source, args.output, args.database_name, args.private_path)
        open_graph_and_db.interactive_mode()
    

def main(args=None):
    """
    Main method to run from command line
    """
    OpenGraphAndDB.run_from_command_line(args)


if __name__ == "__main__":
    main()
