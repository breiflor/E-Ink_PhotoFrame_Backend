import numpy as np
import cv2
import json

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
        self.debug = self.config["debug"]
        self.w1=7/16.0
        #print w1
        self.w2=3/16.0
        self.w3=5/16.0
        self.w4=1/16.0

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
        image = cv2.resize(img,(800,480), interpolation= cv2.INTER_AREA)
        if self.debug :
            cv2.imshow("Resized Image", image)
            cv2.waitKey(0)
        return image

    def process_image(self,img):
        #return sucess
        blue =self.hist_eq(self.stucki(img[:,:,0]))
        green =self.hist_eq(self.stucki(img[:,:,1]))
        red =self.hist_eq(self.stucki(img[:,:,2]))
        image = cv2.merge((blue, green, red))
        if self.debug :
            cv2.imshow("converted Image", image)
            cv2.waitKey(0)
        pass

    def preview(self):
        #returns converted image object
        pass

    def store(self,path):
        pass

    def process_and_store(self,img,path):
        image = self.resize(self.load_image(img))
        bimg = self.process_image(image)



    def hist_eq(self,im):
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        cl1 = clahe.apply(im)
        return cl1

    def set_pixel(self,im,x,y,new):
        im[x,y]=new

    def stucki(self,im):   # stucki algorithm for image dithering
        w8= 8/42.0;
        w7=7/42.0;
        w5=5/42.0;
        w4= 4/42.0;
        w2=2/42.0;
        w1=1/42.0;
        width,height=im.shape
        for y in range(0,height-2):
            for x in range(0,width-2):
                old_pixel=im[x,y]
                if old_pixel<127:
                    new_pixel=0
                else:
                    new_pixel=255
                self.set_pixel(im,x,y,new_pixel)
                quant_err=old_pixel-new_pixel
                self.set_pixel(im,x+1,y, im[x+1,y] + w7 * quant_err);
                self.set_pixel(im,x+2,y, im[x+2,y]+ w5 * quant_err);
                self.set_pixel(im,x-2,y+1, im[x-2,y+1] + w2 * quant_err);
                self.set_pixel(im,x-1,y+1, im[x-1,y+1] + w4 * quant_err);
                self.set_pixel(im,x,y+1, im[x,y+1] + w8 * quant_err);
                self.set_pixel(im,x+1,y+1, im[x+1,y+1] + w4 * quant_err);
                self.set_pixel(im,x+2,y+1, im[x+2,y+1] + w2 * quant_err);
                self.set_pixel(im,x-2,y+2, im[x-2,y+2] + w1 * quant_err);
                self.set_pixel(im,x-1,y+2, im[x-1,y+2] + w2 * quant_err);
                self.set_pixel(im,x,y+2, im[x,y+2] + w4 * quant_err);
                self.set_pixel(im,x+1,y+2, im[x+1,y+2] + w2 * quant_err);
                self.set_pixel(im,x+2,y+2, im[x+2,y+2]+ w1 * quant_err);
        return im


    def quantize(self,im):  # Floyd-Steinberg METHOD of image dithering
        for y in range(0,480-1):
            for x in range(1,800-1):
                old_pixel=im[x,y]
                if old_pixel<127:
                    new_pixel=0
                else:
                    new_pixel=255
                self.set_pixel(im,x,y,new_pixel)
                quant_err=old_pixel-new_pixel
                self.set_pixel(im,x+1,y,im[x+1,y]+quant_err*self.w1)
                self.set_pixel(im,x-1,y+1, im[x-1,y+1] +  quant_err*self.w2 )
                self.set_pixel(im,x,y+1, im[x,y+1] +  quant_err * self.w3 )
                self.set_pixel(im,x+1,y+1, im[x+1,y+1] +  quant_err * self.w4 )


        return im

if __name__ == "__main__":
    processor = ImageProcessingPipline()
    processor.process_and_store("test_image.jpg",".")