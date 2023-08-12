from data_handling.RoomAnalysis import RoomAnalysis
from threading import Lock
from color_log import color
logging = color.setup(name=__name__, level=color.DEBUG)
from queue import Queue as _Queue
import typing

class DataHandler:
    def __init__(self, queue: _Queue, cv, config):
        # configurations
        self.queue = queue
        self.cv = cv

        self.config = config
        self.numRoom = config["numRoom"]
        self.roomsConf = config["room"]

        self.lock = Lock()
        self.rooms: typing.Dict[str, RoomAnalysis] = dict()
        self.received_esp32_list = []
        '''Syncing ESP32 status from `MqttListener.py` to `RoomAnalysis.py` (already apply `unique()`)'''

    def put(self, topic: str, payload: str):
        '''Putting data to `RoomAnalysis`.
        This will also sync ESP32 status across `DataHandler.py` and `MqttListener.py`.
        '''
        logging.info(f'Receiving data from MQTT Topic: ["{color.bg_green(topic)}"]')
        logging.info(f'Data: {payload}')

        roomId, espId = topic.split("/")[1:3]
        if espId not in self.config["room"]["1"]["EspCoor"]:
            if espId == r'lib_esp32_\x0e':
                espId = 'lib_esp32_3'   # [BUG] Seem like it is cause by "lib_esp32_3"
            else:
                logging.error(f'[{espId = }], but expect: {self.config["room"]["1"]["EspCoor"]}')
                raise NameError(f'{espId = }')
        # topic ETS\%room\%esp:
        if roomId not in self.rooms:
            self.rooms[roomId] = RoomAnalysis(roomId, self.queue, self.cv, self.config)
        allRows = payload.split('\n')
        allRowsFiltered = list(filter(lambda x: x != "", allRows))
        header = allRowsFiltered[0]
        # Sync the amount of the online ESP32
        self.rooms[roomId].received_esp32_list = self.received_esp32_list
        self.rooms[roomId].putData(espId, header, allRowsFiltered[1:])
