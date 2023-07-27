from color_log import color
logging = color.setup(name='Sniffer', level=color.DEBUG)

import sys
import subprocess


def main():
  cli_history: list = []
  hist_iter_flag: int = 0
  _lock_cli: bool = True
  go = True
  logging.info("Typing 'stop' to terminate the server.")

  while go:
    _input_str: str = ""
    while True:
      c = sys.stdin.read(1)
      
      if c == 'u':
        pass
        # _lock_cli = False
        # hist_iter_flag += 1
        # if len(cli_history)>=hist_iter_flag:
        #   print(cli_history[-hist_iter_flag], end='', flush=True)
        #   _input_str = cli_history[-hist_iter_flag]
        # else:
        #   _lock_cli = True
        #   hist_iter_flag -= 1

      elif c == '\n':
        break
      _input_str += c

    cli_command = _input_str
    cli_history.append(cli_command)


    # cli_command = input()
    if _lock_cli:
      logging.debug(f"{'='*30} {cli_command} {'='*30}")

    if cli_command == "stop":
      go = False
    elif cli_command == "debug off":
      _lock_cli = True
      logging.info('run "ets.debug_off()"')
    elif cli_command == "debug on":
      _lock_cli = True
      logging.info('run "ets.debug_on()"')
    elif cli_command == "hist":
      _lock_cli = True
      cli_history.pop()
      logging.info(f'{cli_history = }')

    elif len(cli_command)>1 and cli_command[0]=='!':
      _lock_cli = True
      if len(cli_command[1:])>1:
        try:
          _cli_commands = cli_command[1:].split(' ')
          process_1 = subprocess.run(_cli_commands)
          logging.info(f'{process_1 = }')
          logging.info(f'{process_1.args = }')
          logging.info(f'{process_1.returncode = }')
          logging.info(f'{process_1.stdout = }')
        except Exception as e:
          # logging.error("Not allowed.", exc_info=e)
          logging.error("Not allowed.")

    elif len(cli_command)<1:
      _lock_cli = False
      pass

    else:
      _lock_cli = True
      logging.critical('FUNCTION NOT ALLOWED')
      logging.info("Typing 'stop' to terminate the server.")
  
  logging.info('Goodbye!')


if __name__ == '__main__':
  main()