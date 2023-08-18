import numpy as np
from threading import Thread
#import PySimpleGUI as  sg
import PySimpleGUIWeb as sg
import cv2
import json
from ImageHandler import *
from PanelManager import *
from Uploader import *


class Configurator:

    def __init__(self,configfile= "config/configurator.json"):
        self.current_panel = None
        self.config = json.load(open(configfile,))
        self.debug = self.config["debug"]
        self.imghandler = ImageHandler(self.config["img_handler"])
        self.panel_manager = PanelManager(self.config["panel_Manager"])
        self.current_image = self.imghandler.list_images()[0]
        self.image_mode = "add to Eink Panel"
        self.layout = self.create_layout()
        #self.window = sg.Window('EinkPanelConfigurator', self.layout)
        self.flth = Thread(target=app.run,args=(self.config["ip"],self.config["upload_port"]))
        self.flth.daemon = True
        self.flth.start()
        self.window = sg.Window('EinkPanelConfigurator', self.layout,web_ip=self.config["ip"],web_port=int(self.config["port"]),disable_close=True)
        set_cbk(self.uploaded_image)
        self.run_gui()

    def create_layout(self):
        return  [[sg.Text('EInk Panel Configurator'),sg.Button(button_text="upload new Image",key="-ADD-"),sg.FileBrowse("Browse Files"),sg.Text('File Upload via Browser: '+self.config["ip"]+":"+self.config["upload_port"]+"/add")],
                 [sg.Image(self.imghandler.img_name_to_png_path(self.current_image).__str__(),key="-IMAGE-")],
                 [sg.Input(default_text=self.current_image,key="-FILE-"), sg.Save(key="-SAVE-"),sg.Button("delete",key="-DEL-"),sg.Button(self.image_mode,key="-MODE-")],
                 [sg.Combo(self.imghandler.list_images()),sg.Text("Preeview of all Images here: ")],
                 [sg.Column([[sg.Text("Panels")],[sg.Listbox(self.panel_manager.list_panels(),change_submits=True,key="-PANELS-",auto_size_text=True,size=(200,200))]]),
                  sg.Column([[sg.Text("Images")],[sg.Listbox(["select Panel to view Images"],change_submits=True,auto_size_text=True,size=(200,200),key="-IMAGES-")]]),
                  sg.Column([[sg.Button("ADD Panel")],[sg.Text("NAME"),sg.InputText(default_text="SelectPanel")],
                [sg.Text("sleep TIME in min"),sg.InputText(default_text="SelectPanel")],[sg.Button("STORE")]])
                  ]]

    def __del__(self):
        self.flth.join(0)
        self.window.close()

    def uploaded_image(self,image):
        cv2.imwrite("uploaded_image.png",self.imghandler.preeview_image(image))
        self.current_image = None
        self.window['-IMAGE-'].update("uploaded_image.png")
        self.update_screen()

    def update_screen(self):
        if self.current_image is None:
            self.window["-FILE-"].update("Enter Name Here",visible=True)
            #self.window["--"].update()
            self.window["-SAVE-"].update(visible=True)
            self.window["-DEL-"].update(visible=False)
            self.window["-MODE-"].update(visible=False)
        else:
            self.window['-IMAGE-'].update(self.imghandler.img_name_to_png_path(self.current_image).__str__())
            self.window["-SAVE-"].update(visible=False)
            self.window["-FILE-"].update(visible=False)
            self.window["-DEL-"].update(visible=True)
            if self.current_panel is None:
                self.window["-MODE-"].update(visible=False)
            else:
                if self.image_is_mapped_to_panel():
                    self.window["-MODE-"].update("remove_from_panel",visible=True)
                else:
                    self.window["-MODE-"].update("add_to_panel",visible=True)


    def run_gui(self):
        while(1): #TODO make close button evtl
            event, values = self.window.read()
            if event is not "__TIMEOUT__":
                print(event,values)
            if event == "-ADD-":
                print("ADD")
            if event == "-SAVE-":
                self.current_image = self.imghandler.add_image("uploaded_image.png",values["-FILE-"])
                self.update_screen()

    def image_is_mapped_to_panel(self):
        try:
            for image in self.panel_manager.list_images_from_panel(self.current_panel):
                print(image,self.current_image)
                if image == self.current_image:
                    return True
        except:
            pass
        return False


if __name__ == "__main__":
    config = Configurator()