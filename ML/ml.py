import config
from config import DebugMode
import utils

if config.TRAINING:
  # Load from demo
  if config.DEBUG != DebugMode.DISABLE:
    print('Load from demo:\n')
  utils.load_from_demo(config.DEMO_FILE)
  if config.DEBUG != DebugMode.DISABLE:
    print('--------------------------------')

if not config.TRAINING:
  env, behavior_name = utils.open_env()
  if config.DEBUG != DebugMode.DISABLE:
    print('--------------------------------')

  # Inferencing
  if config.DEBUG != DebugMode.DISABLE:
    print('Inferencing:\n')
  utils.inferencing(env, behavior_name)
  if config.DEBUG != DebugMode.DISABLE:
    print('--------------------------------')