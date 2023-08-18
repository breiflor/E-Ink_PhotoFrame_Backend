from ImageProcessingPipline import ImageProcessingPipline
import json
from pathlib import Path
import numpy as np
import cv2

class ImageHandler:

    def __init__(self,configfile = "config/imageHandler.json"):
        self.config = json.load(open(configfile,))
        self.debug = self.config["debug"]
        self.pipline = ImageProcessingPipline(self.config["path"],self.config["imageProcessing.json"])
        self.scan_for_images()

    def scan_for_images(self):
        self.images = []
        for asset in Path(self.config["path"]).absolute().iterdir():
            if asset.suffix == ".png":
                self.images.append(asset.name)
        if self.debug: print("found images: ",self.images)

    def list_images(self):
        return self.images

    def add_image(self,img):
        self.pipline.process_and_store(img)
        self.scan_for_images()

    def preeview_image(self,img):
        return self.pipline.process_image(self.pipline.resize(img))[0] #TODO Performace Optimization when caching data

    def add_image(self,img,name):
        imgpath = self.pipline.process_and_store(img,name)
        self.scan_for_images()
        return imgpath

    def remove_image(self,img_name):
        p = self.img_name_to_png_path(img_name)
        if p.is_file():
            p.unlink()
        p_csv = self.img_name_to_csv_path(img_name)
        if p_csv.is_file():
            p_csv.unlink()
        self.scan_for_images()

    def get_image_array(self,img_name):
        p = self.img_name_to_csv_path(img_name)
        return np.fromfile(p,dtype=np.uint8,sep=",")

    def show_image(self,img_name):
        p = self.img_name_to_png_path(img_name)
        cv2.imshow(img_name,self.pipline.load_image(p.__str__()))
        cv2.waitKey(0)

    def get_image(self,img_name):
        p = self.img_name_to_png_path(img_name)
        return self.pipline.load_image(p.__str__())

    def img_name_to_png_path(self,name):
        return Path(self.config["path"]+"/"+name).with_suffix(".png")

    def img_name_to_txt(self,name):
        return Path(name).with_suffix("")

    def img_name_to_csv_path(self,name):
        return Path(self.config["path"]+"/"+name).with_suffix(".csv")

if __name__ == "__main__":
    imhandler = ImageHandler()
    imhandler.remove_image("test_image2.png")
    imhandler.add_image("test_image2.jpg")
    print(imhandler.get_image_array("test_image2"))
    print(imhandler.get_image("test_image2"))
