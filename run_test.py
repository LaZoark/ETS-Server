from color_log import color
logging = color.setup(name=__name__, level=color.DEBUG)

# from test import test_color
# test_color.test()

# from wise_paas import monitor

# import datetime
# print('ddd ' + str(datetime.datetime.fromtimestamp(1691500620)))

# import numpy as np

# aa = ['1', '3']
# bb = ['1','2','3','4']
# logging.info(list(set(bb)-set(aa)))


import yaml
filename = 'configurations.yaml' 
with open(filename, 'r') as f:
  config = yaml.load(f, yaml.FullLoader)

print(config['WISE_PaaS']['DataHub']['apiUrl'])
print(config['WISE_PaaS']['DataHub']['ESP32_monitor']['nodeId'])
print(config['WISE_PaaS']['DataHub']['ESP32_monitor']['credentialKey'])

# for i in range(10):
#   if i == 7:
#     i='fff'
#   try:
#     logging.info(f'[{i}] {100/(5-i)=}')
#   except ZeroDivisionError as e:
#   # except Exception as e:
#     # logging.error('div by zero!', exc_info=e)
#     logging.error('div by zero!', )
#   except Exception as e:
#   # except Exception as e:
#     # logging.error('div by zero!', exc_info=e)
#     logging.error(color.bg_blue('?????!'))
#     logging.error(f"Unable to send entries, "
#                   f"retrying the next time (trial:{3})", )
                    