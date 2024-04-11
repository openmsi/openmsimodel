import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from openmsimodel.graph.open_graph_widget import OpenGraphWidget
import os

class LivePlotter(FileSystemEventHandler):
    def __init__(self, display_func):
        self.display_func = display_func
        self.current_display = None

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".graphml"):
            print(f"New graph found: {event.src_path}")
            if self.current_display:
                self.current_display.close()
            self.current_display = self.display_func(
                OpenGraphWidget.from_graphml_folder(os.path.dirname(event.src_path))
            )


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
