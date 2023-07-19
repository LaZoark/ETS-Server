from threading import Thread, current_thread

from analysis.DBhandler import DbHandler
from analysis.localization import analyze
from color_log import color
logging = color.setup(name=__name__, level=color.INFO)

class Analyzer:
    def __init__(self, queue, cv, config, db_persistence=False):
        self.config = config

        self.queue = queue
        self.cv = cv
        self.db_persistence = db_persistence
        self.thread = Thread(target=self.run, args=(self.queue,))

    def start(self):
        if not self.db_persistence:
            try:
                with DbHandler(self.config, self.db_persistence) as dh:
                    dh.createDatabase()
                    dh.createTable()
                    logging.info("Connected to database")
                    logging.info("Created Table and Database")
            except Exception as e:
                logging.error(f"Unable to connect to database", exc_info=e)
        self.thread.start()

    def run(self, queue):
        t = current_thread()
        entries = []
        while getattr(t, "do_run", True):
            logging.debug("Analyzer running")
            with self.cv:
                logging.debug("Analyzer go to sleep")
                self.cv.wait_for(
                    lambda: not queue.empty() or not getattr(t, "do_run", True), 
                    timeout=5)
            logging.debug("Analyzer woke up")
            while not queue.empty():
                try:
                    time_frame_analysis = queue.get(timeout=2)
                except Exception as e:
                    logging.error(e)
                    continue
                queue.task_done()

                analyzed_entries = analyze(time_frame_analysis, self.config)

                entries += analyzed_entries
            # If there is at least something to send, i send data to database
            logging.debug("is there something to send to the database?")
            if len(entries) > 0:
                logging.debug("YES, there is something to send to the database")
                try:
                    logging.debug(f"{self.db_persistence=}")
                    with DbHandler(self.config, persistence=self.db_persistence) as dh:
                        logging.debug("Connection is ok")
                        dh.insert(entries)
                        logging.info("Data inserted to the database with success! Cleaning buffer...")
                        entries = []
                except Exception as e:
                    logging.error("Unable to send entries, retrying the next time",
                                  exc_info=e)

    def stop(self):
        logging.info("Stopping Analyzer!")
        self.thread.do_run = False
        with self.cv:
            self.cv.notify()
        self.thread.join()
