import numpy as np
import cv2
import json

class ImageProcessingPipline:
    """
            This class, implements the Image Processing needed to generate the BIN file from a png or jpg.
    """

    def __init__(self,configfile = "config/imageProcessing.json"):
        """
        inits all the parmeters
        :param configfile: path to the json config file. The json contains all parameters.
        :type configfile: string
        """
        self.config = json.load(open(configfile,))
        self.debug = self.config["debug"]

    def load_image(self, img):
        #loads image in Class
        pass

    def process_image(self):
        #return sucess
        pass

    def preview(self):
        #returns converted image object
        pass

    def store(self,path):
        pass

    def process_and_store(self,img,path):
        self.load_image(img)



