from copy import deepcopy
from threading import Lock
from color_log import color
logging = color.setup(name=__name__, level=color.DEBUG)
from data_handling.TimeFrameAnalysis import TimeFrameAnalysis
from utility.utility import getTid
from queue import Queue as _Queue


class RoomAnalysis:
    def __init__(self, id, queue: _Queue, cv, config):
        self.config = config

        # Configuring multiThreading obj
        self.queue: _Queue = queue
        self.cv = cv
    
        self.roomId = id
        self.currTid = -1
        self.numEsp = config["room"][self.roomId]["numEsp"]
        self.currentAnalysisData = TimeFrameAnalysis(-1, 1, id)

        self.lock = Lock()


    def putData(self, espId, header, rows):
        '''This function will calibration the TID(Time ID) whenever the data received'''
        espTid = getTid(header)
        # DEBUG
        # print("Trying to take the lock for the room: ",self.roomId)
        if espTid < self.currTid:
            logging.warning("Old packet, all the packets captured that are written into it will not be be analyzed")
        elif espTid == self.currTid:
            logging.debug(f"for [{espTid=}]: packets were sent, check if it is the last one")
            if self.currentAnalysisData.putRows(espId, header, rows):
                logging.info(f"for [{espTid=}]: all the packets were sent, putting it into the queue")
                self.putDataQueue()
                logging.warning(f'{self.currentAnalysisData.getDataFrame() = }')
                self.currTid += self.config['Sniffing_time']
                with self.lock:
                    self.currentAnalysisData = TimeFrameAnalysis(self.currTid, self.numEsp, self.roomId)

        else:
            # The current Time id it's updated, because from now the analysis will be done refering to new Time id
            self.currTid = espTid
            # TODO analyze data with what i have?
            with self.lock:
                self.currentAnalysisData = TimeFrameAnalysis(self.currTid, self.numEsp, self.roomId)
            if self.currentAnalysisData.putRows(espId, header, rows):
                self.putDataQueue()

    def putDataQueue(self):
        with self.cv:
            self.cv.wait(timeout=4)
            logging.warning(f'{self.queue.qsize() = }')
            with self.lock:
                print('*%'*60)
                self.queue.put(deepcopy(self.currentAnalysisData))
            logging.warning(f'{self.queue.qsize() = }')
            self.cv.notify_all()
