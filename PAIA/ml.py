import config
from config import RunningMode
from demo import Demo
import utils
from utils import debug_print

if config.RUNNING_MODE == RunningMode.ONLINE:
    # Online
    env, behavior_name = utils.open_env()
    debug_print('--------------------------------')
    debug_print('Online:\n')
    utils.online(env, behavior_name)
    debug_print('--------------------------------')


if config.RUNNING_MODE == RunningMode.OFFLINE:
    # Load from demo
    debug_print('Offline:\n')
    # utils.load_from_demo(config.DEMO_FILE)
    demo = Demo(config.DEMO_PATH)
    debug_print('--------------------------------')


if config.RUNNING_MODE == RunningMode.HEURISTIC:
    # Online
    env, behavior_name = utils.open_env()
    debug_print('--------------------------------')
    debug_print('Heuristic:\n')
    utils.heuristic(env, behavior_name, config.DEMO_FILE)
    debug_print('--------------------------------')