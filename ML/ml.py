import config
from config import DebugMode, RunningMode
import utils

if config.RUNNING_MODE == RunningMode.ONLINE:
  env, behavior_name = utils.open_env()

  if config.DEBUG != DebugMode.DISABLE:
    print('--------------------------------')

  # Online
  if config.DEBUG != DebugMode.DISABLE:
    print('Online:\n')

  utils.online(env, behavior_name)

  if config.DEBUG != DebugMode.DISABLE:
    print('--------------------------------')


if config.RUNNING_MODE == RunningMode.OFFLINE:
  # Load from demo
  if config.DEBUG != DebugMode.DISABLE:
    print('Offline:\n')
  
  utils.load_from_demo(config.DEMO_FILE)

  if config.DEBUG != DebugMode.DISABLE:
    print('--------------------------------')


if config.RUNNING_MODE == RunningMode.HEURISTIC:
  env, behavior_name = utils.open_env()

  if config.DEBUG != DebugMode.DISABLE:
    print('--------------------------------')

  # Online
  if config.DEBUG != DebugMode.DISABLE:
    print('Heuristic:\n')

  utils.heuristic(env, behavior_name, config.DEMO_FILE)

  if config.DEBUG != DebugMode.DISABLE:
    print('--------------------------------')