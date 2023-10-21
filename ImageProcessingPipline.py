import numpy as np
import cv2
import json
import pathlib

class ImageProcessingPipline:
    """
            This class, implements the Image Processing needed to generate the BIN file from a png or jpg.
    """

    def __init__(self,path= "./storage",configfile = "config/imageProcessing.json"):
        """
        inits all the parmeters
        :param configfile: path to the json config file. The json contains all parameters.
        :type configfile: string
        """

        self.config = json.load(open(configfile,))
        self.storagepath = path
        self.debug = self.config["debug"]
        self.height = self.config["height"]
        self.width = self.config["width"]
        #self.color_palette = np.array([[0, 0, 0],[255, 255, 255],[0, 255, 0],[255, 0, 0],[0, 0, 255],[0, 255, 255],[0, 128, 255]]) #TODO ajust color palette and load it via Json
        #self.color_palette = np.array([[0, 0, 0],[255, 255, 255],[19, 100, 10],[106, 37, 47],[10, 10,189],[0, 200, 255],[10, 52,236]]) # mesured
        #self.color_palette = np.array([[0, 0, 0],[255, 255, 255],[19, 255, 10],[255, 37, 47],[10, 10,255],[0, 200, 255],[10, 52,255]])
        #self.color_palette = np.array([[0, 0, 0],[255, 255, 255],[19*2.5, 100*2.5, 10*2.5],[106*2.4, 37*2.4, 0*2.4],[10*1.349, 10*1.349,189*1.349],[0, 200, 255],[10*1.08, 52*1.08,236*1.08]])
        self.color_palette = self.load_color_palette(self.config["color_palette"])
        self.color_palette = self.color_palette/255
        self.path = pathlib.Path(self.storagepath)
        self.path.mkdir(parents=True, exist_ok=True)

    def load_image(self, img):
        #loads image in Class
        print(img)
        image = cv2.imread(img,cv2.IMREAD_UNCHANGED)
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
        if img.shape[:2][0] > img.shape[:2][1]: # autorotate images before scaling
            img = cv2.rotate(img,cv2.ROTATE_90_CLOCKWISE)
        if self.config["stretch"]:
            image = cv2.resize(img,(self.width,self.height), interpolation= cv2.INTER_AREA)
        else:
            scale_width = self.width/img.shape[:2][1]
            scale_hight = self.height/img.shape[:2][0]
            if scale_width < scale_hight:
                scale = scale_width
                if self.config["cut"]:
                    scale = scale_hight
            else:
                scale = scale_hight
                if self.config["cut"]:
                    scale = scale_width
            img = cv2.resize(img,(int(scale*img.shape[:2][1]),int(scale*img.shape[:2][0])), interpolation= cv2.INTER_AREA)
            if self.config["cut"]:
                image = img[0:self.height,0:self.width]
            else:
                filler = np.zeros([self.height,self.width-img.shape[:2][1],3],dtype=np.uint8)
                filler.fill(self.config["fill"])
                image = img[0:self.height,0:self.width]
                image = np.column_stack([image,filler])
        print(image.shape)
        if self.debug :
            cv2.imshow("Resized Image", image)
            cv2.waitKey(0)
        return image

    def process_image(self,img):
        #return sucess
        image = self.fs_dither(img)
        panel = self.create_array(image)
        byteimage = self.calculate_panel_array(panel)
        if self.debug :
            cv2.imshow("converted Image", image)
            cv2.waitKey(0)
        return image,byteimage

    def get_new_val(self,old_val):
        idx = np.argmin(np.sum((old_val[None,:] - self.color_palette)**2, axis=1))
        return self.color_palette[idx],idx


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
                new_val,id = self.get_new_val(old_val)
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

    def create_array(self,img):
        arr = np.array(img, dtype=float) / 255
        panel = [np.zeros((self.width,self.height)),np.zeros((self.width,self.height)),np.zeros((self.width,self.height)),np.zeros((self.width,self.height)),np.zeros((self.width,self.height)),np.zeros((self.width,self.height)),np.zeros((self.width,self.height))]


        for ir in range(self.height):
            if self.debug :
                print("Progress"+str(100*ir/self.height)+"%")
            for ic in range(self.width):
                # NB need to copy here for RGB arrays otherwise err will be (0,0,0)!
                old_val = arr[ir, ic].copy()
                new_val,id = self.get_new_val(old_val)
                panel[id][ic][ir] = 1
                # In this simple example, we will just ignore the border pixels.
        return panel


    def store(self,image,bin,name):
        n = pathlib.Path(name).name.strip(pathlib.Path(name).suffix)
        imagepath = self.path.absolute().name+"/"+n+".png"
        binpath = self.path.absolute().name+"/"+n+".csv"
        cv2.imwrite(imagepath,image)
        bin.tofile(binpath, sep=",")
        return n


    def process_and_store_cmd(self,img):
        image = self.resize(self.load_image(img))
        image,bimg = self.process_image(image)
        self.store(image,bimg,img)

    def process_and_store(self,img,name):
        image = self.resize(self.load_image(img))
        image,bimg = self.process_image(image)
        return self.store(image,bimg,name)

    def calculate_panel_array(self, panel):
        arr = np.zeros((self.height,int(self.width/2)),dtype=np.uint8)
        for ir in range(self.height):
            for ic in range(int(self.width/2)):
                entry = 0
                for i in range(len(panel)): #LSB
                    if panel[i][ic*2][ir] > 0:
                        entry += i
                    if panel[i][ic*2+1][ir] > 0: #MSB
                        entry += (i*16) #Bitshift by 4 ;)
                arr[ir][ic]= entry
        print(arr)
        return arr

    def load_color_palette(self, palette):
        return np.array([palette["black"],palette["white"],palette["green"],palette["blue"],palette["red"],palette["yellow"],palette["orange"]])

if __name__ == "__main__":
    processor = ImageProcessingPipline()
    processor.process_and_store_cmd("sleepy.jpeg")