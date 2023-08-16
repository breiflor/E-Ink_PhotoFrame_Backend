import json
from pathlib import Path

class PanelManager:

    def __init__(self,configfile = "config/panelManager.json"):
        self.config = json.load(open(configfile,))
        self.debug = self.config["debug"]
        self.eink_config_storage = self.config["eink_panel_storage"]
        self.load_panels()

    def load_panels(self):
        self.panels = []
        Path(self.eink_config_storage).mkdir(parents=True, exist_ok=True)
        for asset in Path(self.eink_config_storage).absolute().iterdir():
            if asset.suffix == ".json":
                self.panels.append(asset.name)
        if self.debug: print("found eink Panels: ",self.panels)

    def add_panel(self,name,images=[],refresh_after_minutes=60):
        panel = {}
        panel["name"] = name
        panel["images"] = images
        panel["refresh"] = refresh_after_minutes
        panel["current_image"] = "no data - waiting for panel connection"
        panel["status"] = "to be filled by panel"
        p = self.eink_config_storage+"/"+name+".json"
        with open(p,"wt") as fp:
            json.dump(panel,fp)
        self.load_panels()

    def list_panels(self):
        self.load_panels()
        return self.panels

    def remove_panel(self,name):
        p = Path(self.eink_config_storage+"/"+name).with_suffix(".json")
        if p.is_file():
            p.unlink()
        self.load_panels()

    def add_image_to_panel(self,name,image):
        try:
            p = Path(self.eink_config_storage+"/"+name).with_suffix(".json")
            panel = json.load(open(p,))
            panel["images"].append(Path(image).with_suffix("").name)
            p = self.eink_config_storage+"/"+name+".json"
            with open(p,"wt") as fp:
                json.dump(panel,fp)
            return True
        except:
            if self.debug: print("Panel does not exist",name)
            return False

    def remove_image_from_panel(self,name,image):
        try:
            p = Path(self.eink_config_storage+"/"+name).with_suffix(".json")
            panel = json.load(open(p,))
            panel["images"].remove(Path(image).with_suffix("").name)
            p = self.eink_config_storage+"/"+name+".json"
            with open(p,"wt") as fp:
                json.dump(panel,fp)
            return True
        except:
            if self.debug: print("Panel does not exist",name)
            return False

    def list_images_from_panel(self,name):
        try:
            p = Path(self.eink_config_storage+"/"+name).with_suffix(".json")
            panel = json.load(open(p,))
            if self.debug: print("Images on Panel: ",name,panel["images"])
            return panel["images"]
        except:
            if self.debug: print("Panel does not exist",name)
            return []

    def change_refresh_time(self,name,time):
        try:
            p = Path(self.eink_config_storage+"/"+name).with_suffix(".json")
            panel = json.load(open(p,))
            panel["refresh"] = time
            p = self.eink_config_storage+"/"+name+".json"
            with open(p,"wt") as fp:
                json.dump(panel,fp)
            if self.debug: print("Changed refresh time to",time)
            return True
        except:
            if self.debug: print("Panel does not exist",name)
            return False

    def get_refresh_time(self,name):
        try:
            p = Path(self.eink_config_storage+"/"+name).with_suffix(".json")
            panel = json.load(open(p,))
            if self.debug: print("Refresh time of panel",name, panel["refresh"])
            return panel["refresh"]
        except:
            if self.debug: print("Panel does not exist",name)
            return 0



if __name__ == "__main__":
    panelhand = PanelManager()
    panelhand.load_panels()
    panelhand.add_panel("test")
    panelhand.add_image_to_panel("test","hallo")
    panelhand.remove_panel("test")
    panelhand.add_panel("eink1",["test_image","test_image2"])
    print(panelhand.list_images_from_panel("eink1"))
    panelhand.remove_image_from_panel("eink1","test_image")
    panelhand.change_refresh_time("eink1",42)
    print(panelhand.get_refresh_time("eink1"))