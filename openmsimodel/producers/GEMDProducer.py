from openmsimodel.interactive.gemd_automation import GEMDAutomation
from openmsistream.data_file_io.actor.data_file_upload_directory import DataFileUploadDirectory
from openmsistream.data_file_io.entity.upload_data_file import UploadDataFile

class GEMDProducer(GEMDAutomation, DataFileUploadDirectory):
    '''
    Class that combines functionalities of GEMDAutomation and DataFileUploadDirectory.
    It watches a folder for new files, uploads them as they are added, and processes them.
    '''
    output_folder = "./producer_output"

    def __init__(self, dirpath, config_path, upload_regex, watchdog_lag_time,datafile_type=UploadDataFile, use_polling_observer=False, **kwargs):
        GEMDAutomation.__init__(self)
        DataFileUploadDirectory.__init__(self, dirpath, config_path, upload_regex, datafile_type, watchdog_lag_time, use_polling_observer, **kwargs)

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
    """
    Main method to run from command line
    """
    GEMDProducer.run_from_command_line(args)
# def main(args=None):
#     folder_to_watch = "./live_grapher_input"
#     config_path = Path("./config.yaml")  # Adjust the path to your config file
#     upload_regex = RUN_CONST.DEFAULT_UPLOAD_REGEX  # Adjust the constant as needed
#     datafile_type = UploadDataFile  # Adjust as needed
#     watchdog_lag_time = RUN_CONST.DEFAULT_WATCHDOG_LAG_TIME  # Adjust the constant as needed

#     gemd_consumer = GEMDConsumer(
#         dirpath=Path(folder_to_watch),
#         config_path=config_path,
#         upload_regex=upload_regex,
#         datafile_type=datafile_type,
#         watchdog_lag_time=watchdog_lag_time,
#     )

#     observer = Observer()
#     observer.schedule(gemd_consumer, folder_to_watch, recursive=False)
#     observer.start()

#     try:
#         while True:
#             time.sleep(1)
#     except KeyboardInterrupt:
#         observer.stop()
#     observer.join()

if __name__ == "__main__":
    main()