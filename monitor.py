import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import config

queue = None
class Watcher:
    DIRECTORY_TO_WATCH = config.prediction_source

    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH)
        
        self.observer.start()
class Handler(FileSystemEventHandler):
    
    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None

        elif event.event_type == 'created' or event.event_type == "modified":
            # Take any action here when a file is first created.
            if event.src_path.endswith(".pdf"):
                queue.put(event.src_path)
            #else:
                #print("Received created event - %s." % event.src_path)
             #   pass
       