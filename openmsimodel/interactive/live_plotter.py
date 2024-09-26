import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
# from openmsimodel.graph.open_graph_widget import OpenGraphWidget
from openmsimodel.graph.helpers import launch_graph_widget
from openmsimodel.utilities.io import read_graphml_from_folder
import os

class LivePlotter(FileSystemEventHandler):
    '''
    Class that watches a folder, and visualizes all detected graphs in real time. 
    '''
    def __init__(self, display_func):
        self.display_func = display_func
        self.current_display = None

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".graphml"):
            print(f"New graph found: {event.src_path}")
            graph_source = read_graphml_from_folder(os.path.dirname(event.src_path))
            print(graph_source)
            launch_graph_widget(graph_source=graph_source, engine='yfiles')
            # )


def watch_folder_to_plot(folder_path, display_func):
    observer = Observer()
    observer.schedule(LivePlotter(display), path=folder_path)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
