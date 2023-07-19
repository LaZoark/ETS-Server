import argparse
import yaml
import threading
# import logging
from color_log import color
logging = color.setup(name='Sniffer', level=color.DEBUG)
from server.EtsServer import EtsServer

# # TODO: 
# # The following part should move to another file for the maintenance purpose
# logging.basicConfig(
#     level=logging.DEBUG,
#     format="[%(levelname)s] %(message)s (%(filename)s:%(lineno)d)",
#     # format="[%(asctime)s][%(levelname)s] %(message)s (%(filename)s:%(lineno)d)",
#     # datefmt="%Y-%m-%d %H:%M:%S",
#     )



def main(config, persistence, fake):
    # parameters initalization
    logging.info(f"{persistence=}, {fake=}")
    ets = EtsServer(config, fake=fake, db_persistence=persistence)
    ets.start()
    go = True
    while go:
        # a = input("type 'stop' to stop the server.\n")
        logging.info("Typing 'stop' to terminate the server.")
        a = input()
        logging.debug(f"{'='*30} {a} {'='*30}")
        if a == "stop":
            go = False
    ets.stop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ETS Server')
    parser.add_argument('-c', '--config', default=None, type=str, 
                        help='config file path (default: configurations.yaml)')
    parser.add_argument('-p', '--persistence', action='store_true', 
                        help='use to avoid to clean existing database')
    parser.add_argument('-fp', '--fakepublisher', action='store_true', 
                        help='Run the mqtt fake publisher')

    args = parser.parse_args()
    config = {}
    if args.config:
        filename = args.config 
        # os.path.join(os.path.dirname(__file__), args.config)
    else:
        filename = 'configurations.yaml' 
        # os.path.join(os.path.dirname(__file__), 'configurations.yaml')
    try:
        with open(filename, 'r') as f:
            config = yaml.load(f, yaml.FullLoader)
    except Exception as e:
        logging.critical(e)
        exit(-1)
    main(config, True if args.persistence else False, True if args.fakepublisher else False)


