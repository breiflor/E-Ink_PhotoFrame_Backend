import numpy as np
#import PySimpleGUI as  sg
import PySimpleGUIWeb as sg
import cv2
import json
from ImageHandler import *
from PanelManager import *



class Configurator:

    def __init__(self,configfile= "config/configurator.json"):
        self.config = json.load(open(configfile,))
        self.debug = self.config["debug"]
        self.imghandler = ImageHandler(self.config["img_handler"])
        self.panel_manager = PanelManager(self.config["panel_Manager"])
        self.current_image = self.imghandler.list_images()[0]
        self.image_mode = "add to Eink Panel"
        self.layout = self.create_layout()
        self.window = sg.Window('EinkPanelConfigurator', self.layout)
        self.run_gui()

    def create_layout(self):
        return  [[sg.Text('EInk Panel Configurator'),sg.Button(button_text="upload new Image",key="-ADD-"),sg.FilesBrowse()],
                 [sg.Image(self.imghandler.img_name_to_png_path(self.current_image).__str__(),key="-IMAGE-")],
                 [sg.Input(default_text=self.current_image,key="-FILE-"), sg.Save(),sg.Button("delete"),sg.Button(self.image_mode,key="-MODE-")],
                 [sg.Combo(self.imghandler.list_images()),sg.Text("Preeview of all Images here: ")],
                 [sg.Column([[sg.Text("Panels")],[sg.Listbox(self.panel_manager.list_panels(),change_submits=True,key="-PANELS-",auto_size_text=True,size=(200,200))]]),
                  sg.Column([[sg.Text("Images")],[sg.Listbox(["select Panel to view Images"],change_submits=True,auto_size_text=True,size=(200,200),key="-IMAGES-")]]),
                  sg.Column([[sg.Button("ADD Panel")],[sg.Text("NAME"),sg.InputText(default_text="SelectPanel")],
                [sg.Text("sleep TIME in min"),sg.InputText(default_text="SelectPanel")],[sg.Button("STORE")]])
                  ]]

    def __del__(self):
        self.window.close()

    def update_image(self,image):
        self.window['-IMAGE-'].update("test_image.jpg")

    def run_gui(self):
        while(1): #TODO make close button evtl
            event, values = self.window.read()
            if event is not "__TIMEOUT__":
                print(event,values)
            if event == "-ADD-":
                print("ADD")



if __name__ == "__main__":
    config = Configurator()