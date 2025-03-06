import os
from pathlib import Path
from typing import Callable, List, Dict
import openmsimodel.stores.stores_config as stores_tools
from openmsimodel.utilities.runnable import Runnable
from openmsimodel.utilities.argument_parsing import OpenMSIModelParser
import questionary
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from gemd import MaterialTemplate, MeasurementTemplate
from openmsimodel.entity.gemd.material import Material
from openmsimodel.entity.gemd.measurement import Measurement
import re
import json
from gemd.json import GEMDJson


class AutomatableComponentNode:
    def __init__(self, value):
        self.value = value  # This could be a file name, component, or function
        self.children = []  # List of child nodes (representing relationships)

    def add_child(self, child_node):
        self.children.append(child_node)

    def __repr__(self):
        return f"{self.value} -> {[child.value for child in self.children]}"


class AutomatableComponentTree:
    def __init__(self):
        self.root = AutomatableComponentNode("root")
        self.file_mappings = {}  # Mapping of file names to their corresponding nodes

    def add_mapping(self, file_name, automatable_component):
        """
        Add a new file name and map it to an automatable component in the tree.
        """
        if file_name not in self.file_mappings:
            file_node = AutomatableComponentNode(file_name)
            self.root.add_child(file_node)
            self.file_mappings[file_name] = file_node
        else:
            file_node = self.file_mappings[file_name]

        component_node = AutomatableComponentNode(automatable_component)
        file_node.add_child(component_node)
        return component_node

    def find_component_by_file(self, file_name):
        """
        Return the automatable components mapped to a specific file name.
        """
        return self.file_mappings.get(file_name, None)

    def display_tree(self):
        """
        Display the entire tree structure.
        """
        self._display_node(self.root, level=0)

    def _display_node(self, node, level):
        indent = "  " * level
        for child in node.children:
            self._display_node(child, level + 1)


def rule_contains_string(file_name: str, match_str: str) -> bool:
    return match_str in file_name


class FolderEventHandler(FileSystemEventHandler):
    """
    Custom event handler for folder events.
    It calls the appropriate callback when a new file is created in the folder.
    """

    def __init__(self, name, root, callback_function):
        super().__init__()
        self.name = name
        self.root = root
        self.callback_function = callback_function

    def on_created(self, event):
        if event.is_directory:
            # Handle folder creation
            folder_name = os.path.basename(event.src_path)
            # print(f"New folder added: {folder_name}")
            self.callback_function(folder_name, event.src_path)
        else:
            # Handle file creation
            file_name = os.path.basename(event.src_path)
            # print(f"New file added: {file_name}")
            self.callback_function(file_name, event.src_path)


class GEMDModeller(Runnable):

    ARGUMENT_PARSER_TYPE = OpenMSIModelParser

    def __init__(
        self,
        files_folder,
        gemd_folder,
        instantiate_build,
        stores_config=stores_tools.stores_config,
    ):
        """
        Initialize the GEMDModeller with stores_config, files_folder, and gemd_folder.
        """
        self.encoder = (
            GEMDJson()
        )  # TODO: make the store's encoder universally available??
        self.files_folder = Path(files_folder)
        self.gemd_folder = Path(gemd_folder)
        self.instantiate_build = instantiate_build
        self.stores_config = stores_config
        self.automatable_components = []
        self.automatable_components_trees = {}

        # self.run_memory = {}
        self.file_observer = Observer()  # Observer to monitor folder changes

        # Create directories if they don't exist
        self.files_folder.mkdir(parents=True, exist_ok=True)
        self.gemd_folder.mkdir(parents=True, exist_ok=True)

    def add_automatable_component(
        self, rule_function, file_id_regex_pattern, required_schema, action_function
    ):
        self.automatable_components.append(
            {
                "rule_function": rule_function,
                "file_id_regex_pattern": file_id_regex_pattern,
                "required_schema": required_schema,
                "action_function": action_function,
            }
        )

    def functions(self):
        return [
            component["action_function"].__name__
            for component in self.automatable_components
        ]

    def ids(self):
        return list(set([component["id"] for component in self.automatable_components]))

    def required_schemas(self):
        return list(
            set(
                [
                    component["required_schema"]
                    for component in self.automatable_components
                ]
            )
        )

    def extract_id_from_filename_or_filepath(
        self, file_id_regex_pattern: (str, bool), file_name: str, file_path: str
    ) -> str:
        """
        Extract the ID from the filename using a regex file_id.
        Modify the file_id based on your ID format.
        """
        if file_id_regex_pattern[1] == True:  # extract id from filepath
            match = re.search(file_id_regex_pattern[0], file_path)
        else:  # extract id from filename
            # file_id_regex_pattern = r"\d+"  # Example: Match a sequence of digits (modify based on your ID file_id)
            match = re.search(file_id_regex_pattern[0], file_name)
        if match:
            return match.group(0)  # Return the matched ID
        else:
            raise ValueError(f"ID not found in filename: {file_name}")

    def process_file_in_files_folder(self, file_name: str, file_path: str):

        try:

            # Process the file and map to the automatable components tree
            for component in self.automatable_components:
                rule_function = component["rule_function"]

                if rule_function(file_name):

                    file_id = self.extract_id_from_filename_or_filepath(
                        component["file_id_regex_pattern"], file_name, file_path
                    )
                    # Check if the ID already has an automatable components tree, if not, create one
                    if file_id not in self.automatable_components_trees:
                        self.automatable_components_trees[file_id] = (
                            AutomatableComponentTree()
                        )

                    # Access the tree for this ID
                    component_tree = self.automatable_components_trees[file_id]

                    required_schema = component["required_schema"]
                    action_function = component["action_function"]
                    output = action_function(file_name, file_path, component)

                    # Add the mapping to the automatable components tree for this ID
                    component_tree.add_mapping(file_id, component)

                    self.dump_output_to_gemd_folder(output)
                    print(f"Rule was Found for {file_name} and applied. ")

                    return

            print(f"No Rules were Found for {file_name} ")

        except ValueError as e:
            print(e)
            raise e

    def process_file_in_gemd_folder(self, file_name: str, file_path: str):
        """
        Process files dumped into the gemd_folder.
        This could involve registering templates and specs, or handling runs.
        """
        # Logic for handling gemd_folder actions
        print(f"Processing file in gemd_folder: {file_name}")

    def dump_output_to_gemd_folder(self, output):

        for ele in output:
            json_file_path = self.gemd_folder / f"{ele.name}_{ele.typ}.json"
            with open(json_file_path, "w") as json_file:
                json_file.write(self.encoder.thin_dumps(ele, indent=2))
                # json.dump(ele, json_file, indent=4)
            # json.dump(self.encoder(ele, json_file, indent=4)

    def start_folder_monitoring(self):
        """
        Start monitoring both files_folder and gemd_folder.
        """
        # Monitor files_folder
        files_folder_event_handler = FolderEventHandler(
            "files", str(self.files_folder), self.process_file_in_files_folder
        )
        self.file_observer.schedule(
            files_folder_event_handler, str(self.files_folder), recursive=True
        )

        # Monitor gemd_folder
        gemd_folder_event_handler = FolderEventHandler(
            "gemd", str(self.gemd_folder), self.process_file_in_gemd_folder
        )
        self.file_observer.schedule(
            gemd_folder_event_handler, str(self.gemd_folder), recursive=False
        )

        # Process existing files and folders if instantiate_build is True
        if self.instantiate_build:
            self.process_existing_files_and_folders()

        # Start observing both folders
        self.file_observer.start()

    def process_existing_files_and_folders(self):
        """
        Process all existing files and folders in files_folder before monitoring starts.
        """
        print("Processing existing files and folders")

        # Process existing files and folders in files_folder
        for root, dirs, files in os.walk(self.files_folder):
            # Process files
            for file_name in files:
                file_path = os.path.join(root, file_name)
                print(f"- Processing initial file: {file_path}")
                self.process_file_in_files_folder(
                    file_name, file_path
                )  # Call the callback directly

            # Process folders
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                print(f"- Processing initial folder: {dir_path}")
                self.process_file_in_files_folder(
                    dir_name, dir_path
                )  # Call the callback directly

    def stop_folder_monitoring(self):
        """
        Stop monitoring both folders.
        """
        self.file_observer.stop()
        self.file_observer.join()

    @classmethod
    def get_argument_parser(cls, *args, **kwargs):
        parser = cls.ARGUMENT_PARSER_TYPE(*args, **kwargs)
        cl_args, cl_kwargs = cls.get_command_line_arguments()
        parser.add_arguments(*cl_args, **cl_kwargs)
        return parser

    # @classmethod
    def interactive_mode(self):

        while True:
            continue

    @classmethod
    def get_command_line_arguments(cls):
        superargs, superkwargs = super().get_command_line_arguments()
        args = [*superargs, "files_folder", "gemd_folder", "instantiate_build"]
        kwargs = {**superkwargs}
        return args, kwargs

    @classmethod
    def run_from_command_line(cls, args=None):
        parser = cls.get_argument_parser()
        args = parser.parse_args(args=args)
        gemd_modeller = cls(args.files_folder, args.gemd_folder, args.instantiate_build)
        gemd_modeller.interactive_mode()


def main(args=None):
    """
    Main method to run from command line
    """
    GEMDModeller.run_from_command_line(args)


if __name__ == "__main__":
    main()
