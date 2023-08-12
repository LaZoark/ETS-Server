# from wisepaasdatahubedgesdk.EdgeAgent import EdgeAgent
import wisepaasdatahubedgesdk.Common.Constants as constant
from wisepaasdatahubedgesdk.Model.Edge import (EdgeAgentOptions, DiscreteTagConfig,
                                               DCCSOptions, EdgeData, EdgeTag,
                                               EdgeConfig, NodeConfig, DeviceConfig,
                                               )
from color_log import color
logging = color.setup(name=__name__, level=color.DEBUG)
from wise_paas import agent
import typing
# from numpy import unique, ndarray
from utility.utility import unique
import paho.mqtt.client as mqtt


class Listener:
  def __init__(self, config, log_level: int=color.DEBUG):
    self.config = config
    # logging.info("Creating MQTT Obj")
    
    self.monitor = ESP32()  # Building connection
    self.n_devices = config["room"]['1']["numEsp"]
    self._n_devices = self.n_devices

    # mqtt client is configured
    self.mqttc = mqtt.Client(
      client_id=self.config['MQTT_username_listener'],
      transport='tcp')
    self.mqttc.on_message = self.on_message
    # self.mqttc.on_connect = self.on_connect
    # self.mqttc.on_subscribe = self.on_subscribe
    logging.setLevel(log_level)


    # Subscribe to all Sensors at Base Topic
  # def on_connect(self, mqttc, obj, flags, rc):
  #   mqttc.subscribe(self.config["MQTT_Topic"], 0)
  #   logging.info(f'''Connected to "{self.config["MQTT_Broker"]}:{self.config["MQTT_Port"]}"''')
  
  # def on_subscribe(self, mosq, obj, mid, granted_qos):
  #   logging.info("Client successfully subscribed to topic")

  def on_message(self, mosq, obj, msg):
    try:
      # self.dataHandler.put(str(msg.topic), str(msg.payload.decode("UTF-8")))
      logging.info(f'[Monitor] {msg.topic=}')
      self.monitor.received_list.append(msg.topic.split('/')[-1])
      self.n_devices -= 1
      if self.n_devices == 0:
        self.monitor.check_alive(unique(self.monitor.received_list))
        self.monitor.received_list = []     # recovery
        self.n_devices = self._n_devices    # recovery
        
    except Exception as e:
      logging.fatal(f'Skipping! Unable to handle: [{msg.topic = }] {e}')

  def start(self):
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

  def loop(self):
    while self.mqttc.loop() == 0:
      pass


class ESP32:
  # Constructor (EdgeAgentOptions options) 建立一個 EdgeAgent 物件.
  def __str__(self) -> str:
    return 'ESP32_Monitor'
  def __init__(self, yaml_config) -> None:
    __apiUrl = yaml_config['WISE_PaaS']['DataHub']['apiUrl']
    __nodeId = yaml_config['WISE_PaaS']['DataHub']['ESP32_monitor']['nodeId']
    __credentialKey = yaml_config['WISE_PaaS']['DataHub']['ESP32_monitor']['credentialKey']
    self.received_list = []
    self.options_config = EdgeAgentOptions(
      nodeId = __nodeId,
      heartbeat = 60,                                         # 預設是 60 seconds
      dataRecover = True,                                     # 是否需要斷點續傳, 預設為 true
      connectType = constant.ConnectType['DCCS'],             # 連線類型 (DCCS, MQTT), 預設是 DCCS
                                                              # 若連線類型是 DCCS, DCCSOptions 為必填
      DCCS = DCCSOptions(
        apiUrl = __apiUrl,                                    # DCCS API Url
        credentialKey = __credentialKey                       # Creadential key
      )
    )
    self.edgeAgent = agent.setup(self.options_config)

    config = EdgeConfig()
    config.node = NodeConfig(nodeType=constant.EdgeType['Gateway'])

    esp32_1_alive = DiscreteTagConfig(name='esp32_1_alive',
                                      description='whether esp32-1 is alive',
                                      readOnly=True,
                                      arraySize=0,
                                      state0 = '0',
                                      state1 = '1',
                                      )
    esp32_2_alive = DiscreteTagConfig(name='esp32_2_alive',
                                      description='whether esp32-2 is alive',
                                      readOnly=True,
                                      arraySize=0,
                                      state0 = '0',
                                      state1 = '1',
                                      )
    esp32_3_alive = DiscreteTagConfig(name='esp32_3_alive',
                                      description='whether esp32-3 is alive',
                                      readOnly=True,
                                      arraySize=0,
                                      state0 = '0',
                                      state1 = '1',
                                      )
    esp32_4_alive = DiscreteTagConfig(name='esp32_4_alive',
                                      description='whether esp32-4 is alive',
                                      readOnly=True,
                                      arraySize=0,
                                      state0 = '0',
                                      state1 = '1',
                                      )
    agent.create_device(config=config,
                        deviceId='esp32_status',
                        description='Monitor all the esp32.',
                        deviceType='status'
                        )
    self.tag_list = [esp32_1_alive, esp32_2_alive, esp32_3_alive, esp32_4_alive]
    self.tag_name_list = ['esp32_1_alive', 'esp32_2_alive', 'esp32_3_alive', 'esp32_4_alive']

    for _tag in self.tag_list:
      config.node.deviceList[0].discreteTagList.append(_tag)
      # config.node.deviceList[0].analogTagList.append(_tag)

    agent.config_upload(self.edgeAgent, config)

  def send_monitor(self, target: typing.Union[int, str], value: bool=False):
    value: int = 1 if value else 0
    edgeData = EdgeData()
    agent.prepare_data(
      edgeData=edgeData,
      deviceId='esp32_status',
      tagName=f'esp32_{target}_alive',
      value=value
    )
    if not self.edgeAgent.sendData(data=edgeData):
      logging.error(f'Unable to send monitor data')

  def connect(self):
    agent.connect(self.edgeAgent)
    # logging.info(f'Disconnected from WISE-IoT Agnet.')

  def disconnect(self):
    self.edgeAgent.disconnect()
    # logging.info(f'Disconnected from WISE-IoT Agnet.')

  def check_alive(self, espId: typing.Union[str, list]):
    '''Quick method to check the availability of all ESP32.
    Also uploading results to the DataHub.
    '''
    if isinstance(espId, str):
      _id = espId.split('_')[-1][0]  # removing the appending 'char'
      for check_id in ['1','2','3','4']:
        if _id == check_id:
          self.send_monitor(target=_id, value=True)
        else:
          self.send_monitor(target=_id, value=False)
    elif isinstance(espId, list):
      espId_list: typing.List[str] = espId
      online_list, offline_list = [], []
      for esp in espId_list:
        esp_id = esp.split('_')[-1][0]
        for check_id in ['1','2','3','4']:
          if esp_id == check_id:
            online_list.append(check_id)
          # else:
          #   if not check_id in online_list:
          #     offline_list.append(check_id)
      online_list = unique(online_list)
      # offline_list = unique(offline_list)
      offline_list = list(set(['1','2','3','4'])-set(online_list))
      logging.debug(f'{online_list=}, {offline_list=}')
      for offline_esp in offline_list:
        if not offline_esp in online_list:
          self.send_monitor(target=offline_esp, value=False)
      for online_esp in online_list:
        self.send_monitor(target=online_esp, value=True)
        
    else:
      logging.error(f'Unsupported type. (got "{type(espId)}")')
