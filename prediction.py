#imports
#from pdf2jpg import export
from multiprocessing import Pool, Process, Queue
import glob, os, time
from itertools import product
from shutil import copyfile
import multiprocessing
import logging, monitor
logging.basicConfig(level=logging.INFO)
import subprocess

#from functools import partial
#from contextlib import contextmanager

"""@contextmanager
def poolcontext(*args, **kwargs):
    pool = multiprocessing.Pool(*args, **kwargs)
    yield pool
    pool.terminate()
"""

class Prediction(object):
    """
    Prediction Simulation
    """
    def __init__(self, source, model , output="output"):
        #Model initialization
        self.model = model

        #Multi-processing vars
        self.queue = Queue()         #for prediction process
        self.pdf_monitor = Queue()   #for pdf processing process

        #Pdf directory (hard coded)
        self.dir_ = source           #Pdf
        self.output_dir = output   #Result

    def process_pdf(self):
        """
        Creates images per pdf inside the class directory (multiprocessing)
        """
    
        pdf_files = glob.glob(os.path.join(self.dir_, "*.pdf"))

        #with poolcontext(processes=3) as pool:
        #   pool.map(partial(export, in_dir=True, q=self.queue), pdf_files)
        map(lambda pdf_file: export(pdf_file, True, self.queue), pdf_files)

        while True:
            pdf_file = self.pdf_monitor.get()
            logging.debug("New pdf Detected: {}".format(pdf_file))
            export(pdf_file, True, self.queue)

    def predict_pdf(self, pdf_path):
        """
        Combines predictions of multiple images for same pdf
        Returns: str, class label for pdf
        """
        def avg_score(item, iter_, count):
            count = {count[i]:i for i in count.keys()}
            score = 0
            for i,s in iter_:
                if i==item:
                    score += s
            return score/count[item]
        pdf_dir = pdf_path.strip(".pdf")
        
        predictions = [self.model.predict(os.path.join(pdf_dir, img_name))  for img_name in os.listdir(pdf_dir) if img_name.endswith(".jpg")]
        items = [i for i,_ in predictions]
        count = {items.count(i):i for i,_ in predictions}

        class_ = count[max(count.keys())]
        score_ = avg_score(class_, predictions, count)
        #log the class_ and score_ in file for logging history
        with open("logs.txt", "a") as f:
            t = time.localtime()
            timestamp = time.strftime('%b-%d-%H:%M', t)
            f.write("{}, {}, {}, {}".format(timestamp, pdf_path, class_, score_))
            f.write("\n")
        return class_

    def shelf_pdf(self, pdf_path, shelf):
        """
        Puts the pdf into the shelf directory
        """
        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)
        if not os.path.exists(shelf):
            os.mkdir(shelf)    
        
        #Copy pdf
        #copyfile(pdf_path, os.path.join(shelf, pdf_path.split('/')[-1]))    
        
        #Copy its images 
        pdf_dir = pdf_path.strip(".pdf")
        map(lambda path: copyfile(os.path.join(pdf_dir, path),
                                    os.path.join(shelf, path)), os.listdir(pdf_dir))
        
    def action(self):
        """
        Performs prediction simulation actions
        """
        #Starting PDF --> JPG process 
        #p1 = Process(target=self.process_pdf)
        #p1.start()
        #logging.info("PDF --> JPG started")
        
        #Monitoring for pdfs in directory and processing them
        #monitor.queue = self.pdf_monitor
        #w = monitor.Watcher()
        #w.run()

        #while True:
            #processed_pdf = self.queue.get()
            #logging.info("Fetched: {}".format(processed_pdf)) 
        """print filter(lambda x: os.path.isdir(os.path.join(self.dir_, x)), os.listdir(self.dir_))   
        folders = list(filter(lambda x: os.path.isdir(os.path.join(self.dir_, x)), os.listdir(self.dir_)))
        folders_path=[]
        for folder in folders:
            folder=os.path.join(self.dir_,folder)
            folders_path.append(folder)
        print folders_path    
        for folder in folders_path:"""
        shelf = self.predict_pdf(self.dir_)
        print shelf
        logging.info("Shelving...")
        self.shelf_pdf(self.dir_, shelf=os.path.join(self.output_dir, shelf))
