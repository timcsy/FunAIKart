from enum import Enum
from datetime import datetime

# Type definitions ###############################################

class DebugMode(Enum):
    DISABLE = 0
    SIMPLE = 1
    DETAIL = 2

##################################################################

# Online or Offline
ONLINE: bool = True
# ONLINE: bool = False

# Which Debug mode?
# DEBUG: DebugMode = DebugMode.DISABLE
# DEBUG: DebugMode = DebugMode.SIMPLE
DEBUG: DebugMode = DebugMode.DETAIL

# Place to store the images (without the last / )
IMAGE_DIR: str = 'cameras/' + datetime.now().strftime('%Y%m%d_%H%M%S')

# Path to the Demo files (without the last / )
DEMO_DIR: str = 'Demo'
DEMO_FILE: str = 'demo.demo'

# Max Episodes for online
MAX_EPISODES: int = 10