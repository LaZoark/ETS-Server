from color_log import color
logging = color.setup(name='Sniffer', level=color.DEBUG)

import sys
import subprocess


def main():
  cli_history: list = []
  hist_iter_flag: int = 0
  _lock_cli: bool = True
  go: bool = True
  logging.info("Typing 'stop' to terminate the server.")

  while go:
    _input_str: str = ""
    while True:
      c = sys.stdin.read(1)
      if c == '\n':
        break
      _input_str += c

    cli_command = _input_str
    cli_history.append(cli_command)


    if cli_command == "stop":
      go = False
    elif cli_command == "debug off":
      _lock_cli = True
      logging.info('run "ets.debug_off()"')
    elif cli_command == "debug on":
      _lock_cli = True
      logging.info('run "ets.debug_on()"')
    elif cli_command[:4] == "hist":
      _lock_cli = True
      cli_history.pop()
      _cli_commands = cli_command.split(' ')
      if len(_cli_commands) == 1:
        logging.info(f'{cli_history = }')
      elif len(_cli_commands) == 2:
        if len(cli_history) > int(_cli_commands[-1]):
          cli_command = cli_history[int(_cli_commands[-1])]
        else:
          logging.error(f'Out of range. {cli_history = }')

    elif len(cli_command)>1 and cli_command[0]=='!':
      _lock_cli = True
      if len(cli_command[1:])>1:
        try:
          _cli_commands = cli_command[1:].split(' ')
          process_1 = subprocess.run(_cli_commands)
          logging.info(f'{process_1 = }')
        except:
          logging.error("Not allowed.")

    elif len(cli_command)<1:
      _lock_cli = False
      cli_history.pop()
      pass

    else:
      _lock_cli = True
      cli_history.pop()
      logging.critical('FUNCTION NOT ALLOWED')
      logging.info("Typing 'stop' to terminate the server.")
    
    if _lock_cli:
      logging.debug(f"{'='*30} {cli_command} {'='*30}")

  logging.info('Goodbye!')


if __name__ == '__main__':
  main()