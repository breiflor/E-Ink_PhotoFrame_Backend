import json
from datetime import datetime,timedelta

from paho.mqtt import client as mqtt_client
from ImageHandler import ImageHandler
import numpy as np

class NumpyArrayEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            list = obj.tolist()
            s = ""
            for e in list:
                if e <32:
                    s= s + chr(e+40)
                else:
                    s = s+ chr(e)
            return s

        return json.JSONEncoder.default(self, obj)

class Eink_Panel:

    def __init__(self,configfile,mqtt_settings = "config/mqtt_config1.cfg"):
        self.config = json.load(open(configfile,))
        mqtt_data = json.load(open(mqtt_settings))
        self.height = 480
        self.width = 800
        self.quarter_pixels = int(self.height*self.width/4/2)
        self.state = "no Connection"
        self.last_update = None
        self.next_image_name = None
        self.img_handler = ImageHandler()
        self.ack_topic = "Eink_frame/"+self.config["name"]+"/ack"
        self.reset_topic = "Eink_frame/"+self.config["name"]+"/reset"
        self.request_image = "Eink_frame/"+self.config["name"]+"/get_image"
        self.send_topic = "Eink_frame/"+self.config["name"]+"/send_image"
        self.client = mqtt_client.Client("Eink_Panel_Handler_"+self.config["name"])
        self.image = self.load_next_image()
        self.client.on_connect = self.on_connect
        self.client.username_pw_set(mqtt_data["user"], mqtt_data["password"])
        self.client.connect(mqtt_data["broker"], mqtt_data["port"])
        self.client.loop_start()

    def __del__(self):
        self.client.loop_stop()

    def on_connect(self,client, userdata, flags, rc):
        self.client.subscribe(self.ack_topic)
        self.client.subscribe(self.reset_topic)
        self.client.subscribe(self.request_image)
        self.client.on_message = self.callback

    def callback(self,client,userdata,msg):
        if(msg.topic == self.reset_topic):
            self.reset()
        elif msg.topic == self.request_image:
            self.img_request()
        elif msg.topic == self.ack_topic:
            self.send_image(msg.payload.decode())

    def reset(self):
        self.state = "WAIT"
        self.last_update = None

    def img_request(self):
        if self.state == "no Connection":
            self.state = "WAIT"
        if self.state == "WAIT":
            if self.last_update is None or  datetime.now() - self.last_update > timedelta(minutes=self.config["refresh"]):
                self.state = "SENT SECTION 1"
                data = {"part": 1, "img": json.dumps(self.image[0:self.quarter_pixels-1], cls=NumpyArrayEncoder)}
                self.client.publish(self.send_topic,json.dumps(data))
            else:
                data = {"error": "Too early request"}
                self.client.publish(self.send_topic,json.dumps(data))

    def send_image(self,part):
        if self.state == "SENT SECTION 1" and part == "1" :
            self.state = "SENT SECTION 2"
            data = {"part": 2, "img": json.dumps(self.image[self.quarter_pixels:(2*self.quarter_pixels-1)], cls=NumpyArrayEncoder)}
            self.client.publish(self.send_topic,json.dumps(data))
        elif self.state == "SENT SECTION 2" and part == "2" :
            self.state = "SENT SECTION 3"
            data = {"part": 3, "img": json.dumps(self.image[2*self.quarter_pixels:(3*self.quarter_pixels-1)], cls=NumpyArrayEncoder)}
            self.client.publish(self.send_topic,json.dumps(data))
        elif self.state == "SENT SECTION 3" and part == "3" :
            self.state = "SENT SECTION 4"
            data = {"part": 4, "img": json.dumps(self.image[3*self.quarter_pixels:(4*self.quarter_pixels-1)], cls=NumpyArrayEncoder)}
            self.client.publish(self.send_topic,json.dumps(data))
        elif self.state == "SENT SECTION 4" and part == "4" :
            self.state = "Update Status Infos"
            data = {"part":5,"image_name":self.next_image_name,"refresh":self.config["refresh"]}
            self.client.publish(self.send_topic,json.dumps(data))
        elif self.state == "Update Status Infos" and part == "5":
            self.image = self.load_next_image()
            self.last_update = datetime.now()
            self.state = "WAIT"

    def load_next_image(self):
        if self.config["current_image"] == "no data - waiting for panel connection":
            self.next_image_name = self.config["images"][0]
        else :
            try:
                self.next_image_name = self.config["images"][(self.config["images"].index(self.config["current_image"])+1)%len(self.config["images"])]
            except:
                self.next_image_name = self.config["images"][0]
        return  self.img_handler.get_image_array(self.next_image_name)

if __name__ == "__main__":
    panel = Eink_Panel("eink_panel_storage/eink1.json")
    while(1):
        pass