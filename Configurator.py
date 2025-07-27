import time

import numpy as np
from threading import Thread
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
        self.panel_handlers = []
        self.panels = []
        self.start_panel_handlers()
        if self.config["image_sync"]:
            self.last_sync = datetime.today().day-1 # needed for nightly updates
        self.loop()


    def loop(self):
        while(1): #TODO make close button evtl
            if self.config["image_sync"] :
                if self.last_sync is not datetime.today().day:
                    self.panel_manager.sync_image_list(self.imghandler.sync_images())
                    self.last_sync = datetime.today().day
            time.sleep(7200)

    def start_panel_handlers(self):
        for panel_name in self.panel_manager.list_panels():
            panel_handle = Thread(target=self.start_panel,args=(panel_name,))
            panel_handle.start()
            self.panel_handlers.append(panel_handle)

    def start_panel(self,name):
        instance = Eink_Panel(self.panel_manager.eink_config_storage+"/"+name)
        self.panels.append(instance)


if __name__ == "__main__":
    config = Configurator()