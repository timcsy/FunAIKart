from enum import Enum
from datetime import datetime

# Type definitions ###############################################

class RunningMode(Enum):
  ONLINE = 0
  OFFLINE = 1
  HEURISTIC = 2

##################################################################

# Online or Offline
RUNNING_MODE: RunningMode = RunningMode.ONLINE
# RUNNING_MODE: RunningMode = RunningMode.OFFLINE
# RUNNING_MODE: RunningMode = RunningMode.HEURISTIC

# The depth of the log (< 0 if log all)
LOG: int = 2

# Place to store the images (without the last / )
IMAGE_DIR: str = 'cameras/' + datetime.now().strftime('%Y%m%d_%H%M%S')

# Path to the Demo files (without the last / )
DEMO_DIR: str = 'Demo'
DEMO_FILE: str = 'demo.demo'
DEMO_PATH: str = DEMO_DIR + '/' + DEMO_FILE

# Max Episodes for online
MAX_EPISODES: int = 10