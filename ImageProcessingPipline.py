import numpy as np
import cv2
import json
import pathlib

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
        self.storagepath = self.config["path"]
        self.debug = self.config["debug"]
        self.height = self.config["height"]
        self.width = self.config["width"]
        #self.color_palette = np.array([[255,255,255],[0,0,255],[0,255,0],[255,0,0],[0,0,0]]) #RGB Palette
        self.color_palette = np.array([[255, 255, 255],[50, 53, 120],[52, 103, 78],[205, 87, 85],[236, 216, 100],[206, 120, 95],[0, 0, 0]]) #TODO ajust color palette and load it via Json
        self.color_palette = self.color_palette/255
        self.path = pathlib.Path(self.storagepath)
        self.path.mkdir(parents=True, exist_ok=True)

    def load_image(self, img):
        #loads image in Class

        image = cv2.VideoCapture(img).read()[1]
        if self.debug :
            cv2.imshow("Loaded image", image)
            cv2.waitKey(0)
        return image


    def resize(self,img):
        """
        resizes the image
        :param img: input image
        :type img: cv img mat
        :return: resized image
        :rtype: cv img mat
        """
        image = cv2.resize(img,(self.width,self.height), interpolation= cv2.INTER_AREA)
        if self.debug :
            cv2.imshow("Resized Image", image)
            cv2.waitKey(0)
        return image

    def process_image(self,img):
        #return sucess

        image = self.fs_dither(img)
        if self.debug :
            cv2.imshow("converted Image", image)
            cv2.waitKey(0)

        pass

    def get_new_val(self,old_val):
        idx = np.argmin(np.sum((old_val[None,:] - self.color_palette)**2, axis=1))
        return self.color_palette[idx]

    def fs_dither(self,img):
        """
        Floyd-Steinberg dither the image img into a palette with nc colours per
        channel.

        """

        arr = np.array(img, dtype=float) / 255

        for ir in range(self.height):
            if self.debug :
                print("Progress"+str(100*ir/self.height)+"%")
            for ic in range(self.width):
                # NB need to copy here for RGB arrays otherwise err will be (0,0,0)!
                old_val = arr[ir, ic].copy()
                new_val = self.get_new_val(old_val)
                arr[ir, ic] = new_val
                err = old_val - new_val
                # In this simple example, we will just ignore the border pixels.

                if ic < self.width - 1:
                    arr[ir, ic+1] += err * 7/16
                if ir < self.height - 1:
                    if ic > 0:
                        arr[ir+1, ic-1] += err * 3/16
                    arr[ir+1, ic] += err * 5/16
                    if ic < self.width - 1:
                        arr[ir+1, ic+1] += err / 16

        carr = np.array(arr/np.max(arr, axis=(0,1)) * 255, dtype=np.uint8)
        return carr


    def store(self,image,bin,name):
        n = pathlib.Path(name).name.strip(pathlib.Path(name).suffix)
        imagepath = self.path.absolute().name+"/"+n+".png"
        binpath = self.path.absolute().name+"/"+n
        cv2.imwrite(imagepath,image)
        cv2.imwrite("binpath.bmp",image)
        np.save(binpath,bin)


    def process_and_store(self,img):
        image = self.resize(self.load_image(img))
        bimg = self.process_image(image)
        self.store(image,bimg,img)



if __name__ == "__main__":
    processor = ImageProcessingPipline()
    processor.process_and_store("test_image.jpg")