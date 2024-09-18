import os
from pathlib import Path
from typing import Callable, List, Dict
import openmsimodel.stores.stores_config as stores_tools
from openmsimodel.utilities.runnable import Runnable
from openmsimodel.utilities.argument_parsing import OpenMSIModelParser
import questionary
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

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
        self.run_memory = {}
        self.file_observer = Observer()  # Observer to monitor folder changes
        self.start_folder_monitoring()

        # Create directories if they don't exist
        self.files_folder.mkdir(parents=True, exist_ok=True)
        self.gemd_folder.mkdir(parents=True, exist_ok=True)

    def add_automatable_component(self, rule_function, action_function, schema):
        self.automatable_components.append({
            'rule_function': rule_function,
            'action_function': action_function,
            'schema': schema
        })

    def functions(self):
        return [component['action_function'].__name__ for component in self.automatable_components]

    def schemas(self):
        return list(set([component['schema'] for component in self.automatable_components]))

    def process_file_in_files_folder(self, file_name):
        print(f"Processing file in gemd_folder: {file_name}")
        for component in self.automatable_components:
            rule_function = component['rule_function']
            if rule_function(file_name):
                schema = component['schema']
                action_function = component['action_function']
                output = action_function(file_name, schema)
                self.dump_output_to_gemd_folder(output)
                return
        print(f'No Rules were Found.')

    def process_file_in_gemd_folder(self, file_name):
        """
        Process files dumped into the gemd_folder.
        This could involve registering templates and specs, or handling runs.
        """
        # Logic for handling gemd_folder actions
        print(f"Processing file in gemd_folder: {file_name}")

    def dump_output_to_gemd_folder(self, output):
        output_path = self.gemd_folder / "output.json"
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

            choice = questionary.select(
                "Welcome!",
                choices=[
                        "Add An Automatable Component (Action Rule + Action Function + Assortiment)", 
                        "List Existing Automatable Components",
                        "Exit"]
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
