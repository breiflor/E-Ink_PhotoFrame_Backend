import numpy as np
#import PySimpleGUI as sg
import PySimpleGUIWeb as sg
import json

class Configurator:

    def __init__(self,configfile= "config/configurator.json"):
        self.config = json.load(open(configfile,))
        self.debug = self.config["debug"]
        self.layout = self.create_layout()
        self.window = sg.Window('Window Title', self.layout)

    def create_layout(self):
        return  [[sg.Text('My one-shot window.')],
                 [sg.InputText()],
                 [sg.Submit(), sg.Cancel()]]

    def __del__(self):
        self.window.close()

if __name__ == "__main__":
    config = Configurator()
    while(1):
        event, values = config.window.read()