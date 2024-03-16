import numpy as np
from threading import Thread
import PySimpleGUIWeb as sg
import cv2
import json
from ImageHandler import *
from PanelManager import *
from Uploader import *
from Eink_Panel_Instance import *

class Configurator:

    def __init__(self,configfile= "config/configurator.json"):
        self.current_panel = None
        self.config = json.load(open(configfile,))
        self.debug = self.config["debug"]
        self.imghandler = ImageHandler(self.config["img_handler"])
        self.panel_manager = PanelManager(self.config["panel_Manager"])
        self.current_image = self.imghandler.list_images()[0]
        self.layout = self.create_layout()
        self.flth = Thread(target=app.run,args=(self.config["ip"],self.config["upload_port"]))
        self.flth.daemon = True
        self.flth.start()
        self.panel_handlers = []
        self.start_panel_handlers()
        if self.config["image_sync"]:
            self.last_sync = datetime.today().day-1 # needed for nightly updates
        self.window = sg.Window('EinkPanelConfigurator', self.layout,web_ip=self.config["ip"],web_port=int(self.config["port"]),disable_close=True)
        set_cbk(self.uploaded_image)
        self.run_gui()

    def create_layout(self):
        return  [[sg.Text('EInk Panel Configurator'),sg.Text('File Upload via Browser: '+self.config["ip"]+":"+self.config["upload_port"]+"/add")],
                 [sg.Image(self.imghandler.img_name_to_png_path(self.current_image).__str__(),key="-IMAGE-")],
                 [sg.Input(default_text="Enter Name Here",key="-FILE-"), sg.Save(key="-SAVE-"),sg.Button("delete",key="-DEL-"),sg.Button("add to Eink Panel",key="-MODE-")],
                 [sg.Combo(self.imghandler.list_images(),change_submits=True,key="-IMG_LIST-",),sg.Text("Preeview of all Images here: ")],
                 [sg.Column([[sg.Text("Panels")],[sg.Listbox(self.panel_manager.list_panels(),change_submits=True,key="-PANELS-",auto_size_text=True,size=(200,200))]]),
                  sg.Column([[sg.Text("Images")],[sg.Listbox(["select Panel to view Images"],change_submits=True,auto_size_text=True,size=(200,200),key="-IMAGES-")]]),
                  sg.Column([[sg.Button("Add Panel"),sg.Button("Remove Panel")],[sg.Text("NAME",key="-NAME-"),sg.InputText(default_text="Fill in Panel name",key="-Name-")],
                [sg.Text("sleep TIME in min"),sg.InputText(default_text="SelectPanel",key="-TIME-")],[sg.Button("STORE"),sg.Button("sync",visible=True)]])
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
            self.window["-FILE-"].update("",visible=True)
            #self.window["--"].update()
            self.window["-SAVE-"].update(visible=True)
            self.window["-DEL-"].update(visible=False)
            self.window["-MODE-"].update(visible=False)
        else:
            self.window['-IMAGE-'].update(self.imghandler.img_name_to_png_path(self.current_image).__str__())
            self.window["-SAVE-"].update(visible=False)
            self.window["-DEL-"].update(visible=True)
            self.window["-FILE-"].update(self.current_image)
            if self.current_panel is None:
                self.window["-MODE-"].update(visible=False)
            else:
                if self.image_is_mapped_to_panel():
                    self.window["-MODE-"].update("remove_from_panel",visible=True)
                else:
                    self.window["-MODE-"].update("add_to_panel",visible=True)
                self.window["-TIME-"].update(self.panel_manager.get_refresh_time(self.current_panel))


    def run_gui(self):
        while(1): #TODO make close button evtl
            if self.config["image_sync"] :
                if self.last_sync is not datetime.today().day:
                    self.panel_manager.sync_image_list(self.imghandler.sync_images())
            event, values = self.window.read()
            if event != "__TIMEOUT__":
                if self.debug:
                    print(event,values)
            if event == "-SAVE-":
                self.current_image = self.imghandler.add_image("uploaded_image.png",values["-FILE-"])+".png"
                self.window["-IMG_LIST-"].update(values=self.imghandler.list_images())
                self.update_screen()
            if event == "-IMG_LIST-":
                self.current_image = values["-IMG_LIST-"]
                self.window["-FILE-"].update(self.current_image)
                self.update_screen()
            if event == "-DEL-":
                self.imghandler.remove_image(values["-FILE-"])
                self.window["-IMG_LIST-"].update(values=self.imghandler.list_images()) #TODO safe delete
                self.current_image = self.imghandler.list_images()[0]
                self.update_screen()
            if event == "-PANELS-":
                self.current_panel = values["-PANELS-"][0]
                self.window["-IMAGES-"].update(self.panel_manager.list_images_from_panel(self.current_panel))
                self.update_screen()
            if event == "-IMAGES-":
                self.current_image = values["-IMAGES-"][0]+".png"
                self.update_screen()
            if event == "sync":
                self.panel_manager.sync_image_list(self.imghandler.sync_images())
            if event == "-MODE-":
                if self.image_is_mapped_to_panel():
                    self.panel_manager.remove_image_from_panel(self.current_panel,self.current_image)
                else:
                    self.panel_manager.add_image_to_panel(self.current_panel,self.current_image)
                self.window["-IMAGES-"].update(self.panel_manager.list_images_from_panel(self.current_panel))
                self.update_screen()
            if event == "STORE":
                if self.current_panel is not None:
                    self.panel_manager.change_refresh_time(self.current_panel,int(values["-TIME-"]))
                self.update_screen()
            if event == "Add Panel":
                self.panel_manager.add_panel(values["-Name-"])
                self.window["-Name-"].update("")
                self.current_panel = None
                self.window["-PANELS-"].update(self.panel_manager.list_panels())
            if event == "Remove Panel":
                self.panel_manager.remove_panel(self.current_panel)
                self.current_panel = None
                self.window["-PANELS-"].update(self.panel_manager.list_panels())

    def image_is_mapped_to_panel(self):
        try:
            for image in self.panel_manager.list_images_from_panel(self.current_panel):
                if image+".png" == self.current_image:
                    return True
        except:
            pass
        return False

    def start_panel_handlers(self):
        for panel_name in self.panel_manager.list_panels():
            panel_handle = Thread(target=self.start_panel,args=(self,panel_name))
            self.panel_handlers.append(panel_handle)

    def start_panel(self,name):
        instance = Eink_Panel(name)


if __name__ == "__main__":
    config = Configurator()