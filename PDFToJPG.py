class PDFToJPG(object):
    
    def __init__(self):
        self.strategy = None
    
    @property
    def __strategy__(self):
        return self.strategy
    
    @__strategy__.setter
    def __strategy__(self, value):
        self.strategy = value
    
    def read(self, *args):
        """
        Use strategy to read files
        """
        print (self.strategy)
        if bool(self.strategy):
            pdf_list=self.strategy.read(*args)
            #self.strategy.download(*args)
            return pdf_list
        else:
            
            print ("default read")
            
    def download(self, *args):
        """
        Use strategy to read files
        """
        print (self.strategy)
        if bool(self.strategy):
            local_pdf_location=self.strategy.download(*args)
            return local_pdf_location
        else:
            print ("default download")
            
        
    
   # @staticmethod
    def process(self,*args):
        if bool(self.strategy):
            local_images_location=self.strategy.process(*args)
            return local_images_location
        #print ("processing")
    
    def export(self, *args):
        """
        Use strategy """
        #print "export started"
        if bool(self.strategy):
            pdf_name=self.strategy.upload(*args)
            return pdf_name
        else:
            print ("default upload")
            
    def move(self, *args):
        if bool(self.strategy):
            self.strategy.move(*args)
        else:
            print ("default move")
        