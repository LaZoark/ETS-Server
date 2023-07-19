from data_handling.RoomAnalysis import RoomAnalysis
from threading import Lock
from color_log import color
logging = color.setup(name=__name__, level=color.DEBUG)

class DataHandler:
    def __init__(self, queue, cv, config):
        # configurations
        self.queue = queue
        self.cv = cv

        self.config = config
        self.numRoom = config["numRoom"]
        self.roomsConf = config["room"]

        self.lock = Lock()
        self.rooms = dict()
    
    def put(self, topic, payload):
        #DEBUG
        logging.info("MQTT Data Received...")
        logging.info(f'MQTT Topic: ["{topic}"]')
        # logging.info(f'Data: \n{payload}')
        logging.info(f'Data: {payload}')

        roomId, espId = topic.split("/")[1:3]
        # topic ETS\%room\%esp:
        if roomId not in self.rooms:
            self.rooms[roomId] = RoomAnalysis(roomId, self.queue, self.cv, self.config)
        allRows = payload.split('\n')
        allRowsFiltered = list(filter(lambda x: x != "", allRows))
        header = allRowsFiltered[0]
        self.rooms[roomId].putData(espId, header, allRowsFiltered[1:])
