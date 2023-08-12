from copy import deepcopy
from threading import Lock
from color_log import color, tracing_log
logging = color.setup(name=__name__, level=color.DEBUG)
from data_handling.TimeFrameAnalysis import TimeFrameAnalysis
from utility.utility import getTid, unique
from queue import Queue as _Queue
import datetime

class RoomAnalysis:
    def __init__(self, id, queue: _Queue, cv, config):
        self.config = config

        # Configuring multiThreading obj
        self.queue: _Queue = queue
        self.cv = cv
    
        self.roomId = id
        self.currTid = -1
        self.numEsp = config["room"][self.roomId]["numEsp"]
        self.received_esp32_list = []
        '''ESP32 status came from `DataHandler.py` (already apply `unique()`)'''
        self.currentAnalysisData = TimeFrameAnalysis(-1, 1, id)
        self.tracing = tracing_log.Tracing()
        logging.debug(color.bg_purple(f'Start tracing! Current TID={self.tracing.now()}'))
        self.tracing.last_upload_tid = self.tracing.now()

        self.lock = Lock()

    
    def putData(self, espId, header, rows):
        '''This function will calibration the TID(Time ID) whenever the data received'''
        # self.received_esp32_list.append(espId)
        espTid = getTid(header)
        _bypass = False
        logging.debug(color.bg_purple(f'Last push:  {self.tracing.last_upload_tid}') + \
                      f' ({datetime.datetime.fromtimestamp(self.tracing.last_upload_tid)})')
        quiet_period = self.tracing.now() - self.tracing.last_upload_tid
        if abs(quiet_period) >= 60*2:    # Force push every 2 minutes!
            logging.debug(color.bg_purple(
                f'Unable to receive all packet for {quiet_period} seconds. ') + \
                        color.bg_red('Force pushing to the queue!'))
            _bypass = True
            logging.warning('Taking too long waiting for all ESP32. Dropping them...' + color.bg_cyan(
                f"(total: {self.numEsp}->{len(self.received_esp32_list)})"))
            self.numEsp = len(self.received_esp32_list)
            self.currentAnalysisData.numEsp = self.numEsp      # This will update the final condition immediately

        if self.numEsp != len(self.received_esp32_list):
            logging.info(color.tt_lightpurple(
                f"Dynamically adjust awaiting ESP32...(total: {self.numEsp}->{len(self.received_esp32_list)})"))
            self.numEsp = len(self.received_esp32_list)
            self.currentAnalysisData.numEsp = self.numEsp      # This will update the final condition immediately

        if espTid < self.currTid:
            logging.warning(f"Old packet, won't be analyzed [{espTid=}, relative: {color.tt_red(self.currTid-espTid)}]")
            logging.warning(f"Trying to push it anyway")
            if self.currentAnalysisData.putRows(espId, header, rows, bypass=_bypass):
                logging.info(f"for [{espTid=}]: all the packets were sent, putting it into the queue")
                self.putDataQueue()
                logging.debug(f'Current Data:\n{self.currentAnalysisData.getDataFrame()}')
                # self.currTid += self.config['Sniffing_time']    # Will cause the negativer relative timestamp
                # self.tracing.last_upload_tid = self.currTid     # tracing last upload (to queue)
                with self.lock:
                    self.currentAnalysisData = TimeFrameAnalysis(self.currTid, self.numEsp, self.roomId)
        elif espTid == self.currTid:
            logging.debug(f"for [{espTid=}]: packets were sent, check if it is the last one")
            if self.currentAnalysisData.putRows(espId, header, rows, bypass=_bypass):
                logging.info(f"for [{espTid=}]: all the packets were sent, putting it into the queue")
                self.putDataQueue()
                logging.debug(f'Current Data:\n{self.currentAnalysisData.getDataFrame()}')
                self.currTid += self.config['Sniffing_time']
                self.tracing.last_upload_tid = self.currTid     # tracing last upload (to queue)
                with self.lock:
                    self.currentAnalysisData = TimeFrameAnalysis(self.currTid, self.numEsp, self.roomId)

        else:
            # The current Time id it's updated, because from now the analysis will be done refering to new Time id
            self.currTid = espTid
            # TODO analyze data with what i have?
            with self.lock:
                self.currentAnalysisData = TimeFrameAnalysis(self.currTid, self.numEsp, self.roomId)
            if self.currentAnalysisData.putRows(espId, header, rows, bypass=_bypass):
                self.putDataQueue()
                logging.debug(f'Current Data:\n{self.currentAnalysisData.getDataFrame()}')
                self.tracing.last_upload_tid = self.currTid     # tracing last upload (to queue)

    def putDataQueue(self):
        with self.cv:
            self.cv.wait(timeout=4)
            with self.lock:
                self.queue.put(deepcopy(self.currentAnalysisData))
            self.cv.notify_all()
