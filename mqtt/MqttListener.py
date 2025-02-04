import paho.mqtt.client as mqtt
from color_log import color
logging = color.setup(name=__name__, level=color.DEBUG)
from queue import Queue as _Queue
from data_handling.DataHandler import DataHandler

from wise_paas import ESP32
from utility.utility import unique
from time import time
class MQTTListener():
    def __init__(self, queue: _Queue, cv, config, log_level: int=color.DEBUG):
        self.config = config
        logging.info("Creating MQTT Obj")

        # the data handler is initialized
        self.dataHandler = DataHandler(queue, cv, config)

        self.monitor = ESP32(yaml_config=config)  # Building connection
        self.monitor_timer = int(time())
        

        # mqtt client is configured
        self.mqttc = mqtt.Client(client_id=self.config['MQTT_username_listener'],
                                 transport='tcp')
        self.mqttc.on_message = self.on_message
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_subscribe = self.on_subscribe
        logging.setLevel(log_level)


    # Subscribe to all Sensors at Base Topic
    def on_connect(self, mqttc, obj, flags, rc):
        mqttc.subscribe(self.config["MQTT_Topic"], 0)
        logging.info(f'''Connected to "{self.config["MQTT_Broker"]}:{self.config["MQTT_Port"]}"''')
    
    def on_subscribe(self, mosq, obj, mid, granted_qos):
        logging.info("Client successfully subscribed to topic")

    def on_message(self, mosq, obj, msg):
        try:
            self.monitor.received_list.append(msg.topic.split('/')[-1])
            online_list = unique(self.monitor.received_list)
            logging.info(f'{color.bg_green("[Monitor]")} ({online_list}) {msg.topic=}') # 這裡抓得到當下活著的機器
            self.dataHandler.received_esp32_list = online_list  # 每次訂閱到資料都會同步給dataHandler
            if time() - self.monitor_timer > 20:        # monitor every 20 seconds
                self.monitor.check_alive(online_list)
                self.monitor.received_list = []         # recovery
                self.monitor_timer = time()             # recovery
            self.dataHandler.put(str(msg.topic), str(msg.payload.decode("UTF-8")))

        except Exception as e:
            logging.fatal(f'Skipping! Unable to handle: [{msg.topic = }] {e}')

    def start(self):
        # Connect
        logging.info(f'''Connecting to "{self.config["MQTT_Broker"]}:{self.config["MQTT_Port"]}"...''')
        self.mqttc.username_pw_set(username=self.config['MQTT_username_listener'],
                                   password=self.config['MQTT_password_listener'])
        self.mqttc.connect(self.config["MQTT_Broker"],
                           self.config["MQTT_Port"],
                           self.config["Keep_Alive_Interval"])
        self.mqttc.loop_forever()

    def stop(self):
        self.mqttc.disconnect()
        self.mqttc.loop_stop()
        self.monitor.disconnect()

    def loop(self):
        while self.mqttc.loop() == 0:
            pass

