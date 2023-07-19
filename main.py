import argparse
import yaml
import threading
from color_log import color
logging = color.setup(name='Sniffer', level=color.DEBUG)
from server.EtsServer import EtsServer



def main(config, persistence, fake):
    # parameters initalization
    logging.info(f"{persistence=}, {fake=}")
    ets = EtsServer(config, fake=fake, db_persistence=persistence)
    ets.start()
    go = True
    while go:
        logging.info("Typing 'stop' to terminate the server.")
        cli_command = input()
        logging.debug(f"{'='*30} {cli_command} {'='*30}")
        if cli_command == "stop":
            go = False
        else:
            logging.critical('FUNCTION NOT ALLOWED')
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


