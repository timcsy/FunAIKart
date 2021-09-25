import config
from config import DebugMode
import utils

if not config.ONLINE:
  # Load from demo
  if config.DEBUG != DebugMode.DISABLE:
    print('Offline:\n')
  
  utils.load_from_demo(config.DEMO_FILE)

  if config.DEBUG != DebugMode.DISABLE:
    print('--------------------------------')


if config.ONLINE:
  env, behavior_name = utils.open_env()

  if config.DEBUG != DebugMode.DISABLE:
    print('--------------------------------')

  # Online
  if config.DEBUG != DebugMode.DISABLE:
    print('Online:\n')

  utils.online(env, behavior_name)

  if config.DEBUG != DebugMode.DISABLE:
    print('--------------------------------')