from color_log import color
logging = color.setup(name='Sniffer', level=color.DEBUG)


import keyboard

import sys

# def on_key_release(key):
#   if key == Key.right:
#     print("Right key clicked")
#   elif key == Key.left:
#     print("Left key clicked")
#   elif key == Key.up:
#     print("Up key clicked")
#   elif key == Key.down:
#     print("Down key clicked")
#   elif key == Key.esc:
#     exit()


def main():
  cli_history: list = []
  hist_iter_flag: int = 0
  _lock_cli: bool = True
  go = True
  logging.info("Typing 'stop' to terminate the server.")

  while go:
    _input_str = ""
    keyboard.add_abbreviation("@", "john@stackabuse.com")
    while True:
      if keyboard.is_pressed('up'):
        print("keyboard.is_pressed('up'):")
        
        keyboard.p
        _lock_cli = False
        hist_iter_flag += 1
        if len(cli_history)>=hist_iter_flag:
          print(cli_history[-hist_iter_flag], end='', flush=True)
          _input_str = cli_history[-hist_iter_flag]
        else:
          _lock_cli = True
          hist_iter_flag -= 1
          # sys.stdout.flush()
          # print('fffffffflush')

      c = sys.stdin.read(1) # reads one byte at a time, similar to getchar()

      if c == '\n':
        # sys.stdout.flush()
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
      logging.info('run "ets.debug_off()"')
    elif cli_command == "debug on":
      logging.info('run "ets.debug_on()"')
    elif cli_command == "hist":
      logging.info(f'{cli_history = }')
    else:
      logging.critical('FUNCTION NOT ALLOWED')
      logging.info("Typing 'stop' to terminate the server.")
  
  logging.info('Goodbye!')


if __name__ == '__main__':
  main()