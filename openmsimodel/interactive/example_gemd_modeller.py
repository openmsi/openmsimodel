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
        print(self.display_tree())
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
        print(f"{indent}{node.value}")
        for child in node.children:
            self._display_node(child, level + 1)

def rule_contains_string(file_name: str, match_str: str) -> bool:
    return match_str in file_name

class FolderEventHandler(FileSystemEventHandler):
    """
    Custom event handler for folder events.
    It calls the appropriate callback when a new file is created in the folder.
    """
    def __init__(self, callback_function):
        super().__init__()
        self.callback_function = callback_function

    def on_created(self, event):
        if not event.is_directory:
            file_name = os.path.basename(event.src_path)
            print(f"new file added: {file_name}")
            self.callback_function(file_name)

class GEMDModeller(Runnable):

    ARGUMENT_PARSER_TYPE = OpenMSIModelParser

    def __init__(self, files_folder, gemd_folder, stores_config=stores_tools.stores_config):
        """
        Initialize the GEMDModeller with stores_config, files_folder, and gemd_folder.
        """
        self.stores_config = stores_config
        self.files_folder = Path(files_folder)
        self.gemd_folder = Path(gemd_folder)
        self.automatable_components = []
        self.add_automatable_component(
            lambda s: s.endswith('.txt'),  # Rule function
            r"\d+",  # Pattern for extracting ID (you may want to modify this in the action function)
            [MaterialTemplate("Alloy")],  # Schema (or component)
            lambda file_name, component: Material(
                f'{self.extract_id_from_filename(component["pattern"], file_name)} Alloy', 
                template=component['schema'][0]  
            )
        )
        self.add_automatable_component(
            lambda s: s.endswith('.json'), 
            r"\d+",  
            [MeasurementTemplate("XRD")],  
            lambda file_name, component: Measurement(
                f'{self.extract_id_from_filename(component["pattern"], file_name)} XRD Analysis', 
                template=component['schema'][0]  
            )
        )
        # self.automatable_components.append(lambda s: return s.endswith('.txt'), 'r"\d+"')
        self.automatable_components_trees = {}
        
        self.run_memory = {}
        self.file_observer = Observer()  # Observer to monitor folder changes
        self.start_folder_monitoring()

        # Create directories if they don't exist
        self.files_folder.mkdir(parents=True, exist_ok=True)
        self.gemd_folder.mkdir(parents=True, exist_ok=True)

    def add_automatable_component(self, rule_function, pattern, schema, action_function):
        self.automatable_components.append({
            'rule_function': rule_function,
            'pattern': pattern,
            'schema': schema,
            'action_function': action_function,
        })

    def functions(self):
        return [component['action_function'].__name__ for component in self.automatable_components]

    def ids(self):
        return list(set([component['id'] for component in self.automatable_components]))

    def schemas(self):
        return list(set([component['schema'] for component in self.automatable_components]))

    def extract_id_from_filename(self, pattern: str, file_name: str) -> str:
        """
        Extract the ID from the filename using a regex pattern.
        Modify the pattern based on your ID format.
        """
        # pattern = r"\d+"  # Example: Match a sequence of digits (modify based on your ID pattern)
        match = re.search(pattern, file_name)
        if match:
            return match.group(0)  # Return the matched ID
        else:
            raise ValueError(f"ID not found in filename: {file_name}")

    def process_file_in_files_folder(self, file_name: str):
        print(f"Processing file: {file_name}")
        
        try:

            # Process the file and map to the automatable components tree
            for component in self.automatable_components:
                print(component)
                rule_function = component['rule_function']

                if rule_function(file_name):

                    file_id = self.extract_id_from_filename(component['pattern'], file_name)

                    # Check if the ID already has an automatable components tree, if not, create one
                    if file_id not in self.automatable_components_trees:
                        self.automatable_components_trees[file_id] = AutomatableComponentTree()
                    
                    # Access the tree for this ID
                    component_tree = self.automatable_components_trees[file_id]        
                    
                    schema = component['schema']
                    action_function = component['action_function']
                    output = action_function(file_name, component)
                    print("output")
                    print(output)

                    # Add the mapping to the automatable components tree for this ID
                    component_tree.add_mapping(file_name, component)

                    self.dump_output_to_gemd_folder(output)
                    return

            print(f'No Rules were Found for {file_name}.')

        except ValueError as e:
            print(e)

    def process_file_in_gemd_folder(self, file_name):
        """
        Process files dumped into the gemd_folder.
        This could involve registering templates and specs, or handling runs.
        """
        # Logic for handling gemd_folder actions
        print(f"Processing file in gemd_folder: {file_name}")

    def dump_output_to_gemd_folder(self, output):
        # for ele in output:
        output_path = self.gemd_folder / output.name
        with open(output_path, 'w') as f:
            f.write(str(output))

    def start_folder_monitoring(self):
        """
        Start monitoring both files_folder and gemd_folder.
        """
        # Monitor files_folder
        files_folder_event_handler = FolderEventHandler(self.process_file_in_files_folder)
        self.file_observer.schedule(files_folder_event_handler, str(self.files_folder), recursive=False)

        # Monitor gemd_folder
        gemd_folder_event_handler = FolderEventHandler(self.process_file_in_gemd_folder)
        self.file_observer.schedule(gemd_folder_event_handler, str(self.gemd_folder), recursive=False)

        # Start observing both folders
        self.file_observer.start()

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
        args = [*superargs, "gemd_folder", "files_folder"]
        kwargs = {**superkwargs}
        return args, kwargs

    @classmethod
    def run_from_command_line(cls, args=None):
        parser = cls.get_argument_parser()
        args = parser.parse_args(args=args)
        gemd_modeller = cls(args.gemd_folder, args.files_folder)
    
        gemd_modeller.interactive_mode()
    

def main(args=None):
    """
    Main method to run from command line
    """
    GEMDModeller.run_from_command_line(args)


if __name__ == "__main__":
    main()
