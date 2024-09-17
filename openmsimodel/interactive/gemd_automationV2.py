import os
import time
import uuid
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from pathlib import Path

from .data_file_upload_directory import DataFileUploadDirectory  # Adjust the import path
from .open_graph import OpenGraph  # Adjust the import path
from .materials_sequence import MaterialsSequence  # Adjust the import path
from .measurement import Measurement, MeasurementTemplate  # Adjust the import path
from .material import Material, MaterialTemplate  # Adjust the import path
from .process import Process, ProcessTemplate  # Adjust the import path
from .ingredient import Ingredient  # Adjust the import path

class GEMDAutomation(FileSystemEventHandler, DataFileUploadDirectory):
    '''
    Class that watches a folder and for every new file matches its file extension and/or regex to a GEMD backbone.
    Extended to handle folders that are being streamed into using features from DataFileUploadDirectory.
    '''
    mapping = {}
    output_folder = "./live_grapher_output"
    open_graphs = []

    def __init__(self, dirpath, config_path, upload_regex, datafile_type, watchdog_lag_time, use_polling_observer=False, **kwargs):
        DataFileUploadDirectory.__init__(self, dirpath, config_path, upload_regex, datafile_type, watchdog_lag_time, use_polling_observer, **kwargs)
        FileSystemEventHandler.__init__(self)

    def on_created(self, event):
        if event.is_directory:
            return
        filepath = event.src_path
        filename = os.path.basename(filepath)
        print(f"New file added: {filename}")
        file_name, file_extension = os.path.splitext(filepath)
        if file_extension in self.mapping.keys():
            to_be_visualized = self.define_run(self.mapping[file_extension])
        else:
            to_be_visualized = self.define_spec(file_extension, self.mapping, self.output_folder)
        open_graph = self.dump_graph(to_be_visualized, self.output_folder)
        self.open_graphs.append(open_graph)
    
    def dump_graph(self, to_be_visualized, output):
        open_graph = OpenGraph(
            name=str(uuid.uuid4()),
            science_kit=None,
            source=to_be_visualized,
            output=output,
            which="run",
            dump_svg_and_dot=True,
        )
        G, relabeled_G, name_mapping = open_graph.build_graph(save=True)
        return open_graph

    def define_run(self, mapping):
        for ingredient in mapping[2]:
            ingredient.generate_new_spec_run()
        for measurement in mapping[3]:
            measurement.generate_new_spec_run()
        materials_sequence = MaterialsSequence(
            name="None",
            science_kit=None,
            ingredients=mapping[2],
            process=mapping[1].generate_new_spec_run(),
            material=mapping[0].generate_new_spec_run(),
            measurements=mapping[3],
        )
        materials_sequence.link_within()
        return materials_sequence.assets

    def define_spec(self, file_extension, mapping, output):
        measurement_name = input("Enter measurement name: ")
        measurement = Measurement(name=measurement_name, template=MeasurementTemplate(measurement_name))
        material_name = input("Enter material name: ")
        material = Material(name=material_name, template=MaterialTemplate(material_name))
        process_name = input("Enter process name: ")
        process = Process(name=process_name, template=ProcessTemplate(process_name))
        ingredient_name = input("Enter ingredient name: ")
        ingredient = Ingredient(name=ingredient_name)

        mapping[file_extension] = [material, process, [ingredient], [measurement]]
        return self.define_run(mapping[file_extension])

    def upload_files_as_added(self, topic_name, n_threads, chunk_size, max_queue_size, upload_existing):
        uploaded_files = super().upload_files_as_added(topic_name, n_threads, chunk_size, max_queue_size, upload_existing)
        for filepath in uploaded_files:
            filename = os.path.basename(filepath)
            print(f"Uploaded file: {filename}")
            file_name, file_extension = os.path.splitext(filepath)
            if file_extension in self.mapping.keys():
                to_be_visualized = self.define_run(self.mapping[file_extension])
            else:
                to_be_visualized = self.define_spec(file_extension, self.mapping, self.output_folder)
            open_graph = self.dump_graph(to_be_visualized, self.output_folder)
            self.open_graphs.append(open_graph)
        return uploaded_files

def main(args=None):

    while True:
        choice = questionary.select(
            "Are you running ",
            choices=["OpenDB", "OpenGraph", "Exit"]
        ).ask()
        
        if choice == "OpenDB":
            self.open_db.interactive_mode()
        elif choice == "OpenGraph":
            self.open_graph.interactive_mode()
        elif choice == "Exit":
            break
    folder_to_watch = "./live_grapher_input"
    config_path = Path("./config.yaml")  # Adjust the path to your config file
    upload_regex = RUN_CONST.DEFAULT_UPLOAD_REGEX  # Adjust the constant as needed
    datafile_type = UploadDataFile  # Adjust as needed
    watchdog_lag_time = RUN_CONST.DEFAULT_WATCHDOG_LAG_TIME  # Adjust the constant as needed

    gemd_automation = GEMDAutomation(
        dirpath=Path(folder_to_watch),
        config_path=config_path,
        upload_regex=upload_regex,
        datafile_type=datafile_type,
        watchdog_lag_time=watchdog_lag_time,
    )

    observer = Observer()
    observer.schedule(gemd_automation, folder_to_watch, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()