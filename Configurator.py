import numpy as np
import PySimpleGUI as sg
import json

class Configurator:

    def __init__(self,configfile= "config/configurator.json"):
        self.config = json.load(open(configfile,))
        self.debug = self.config["debug"]



if __name__ == "__main__":
    config = Configurator()