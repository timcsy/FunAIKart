import sys

import config
from config import RunningMode
import client
import server
from utils import debug_print

def main(id: str=None):
    if config.RUNNING_MODE == RunningMode.CLIENT:
        # Online client
        client.run(id)
    elif config.RUNNING_MODE == RunningMode.SERVER:
        # Online server
        server.serve_online()
    elif config.RUNNING_MODE == RunningMode.OFFLINE:
        # Offline server and client
        server.serve_offline()
        client.run(id)

if __name__ == '__main__':
    id = ''
    if len(sys.argv) > 1:
        if sys.argv[1] == 'client':
            config.RUNNING_MODE = RunningMode.CLIENT
            if len(sys.argv) > 2 and sys.argv[2] == '-n' and len(sys.argv) > 3:
                id = sys.argv[3]
        elif sys.argv[1] == 'server':
            config.RUNNING_MODE = RunningMode.SERVER
        elif sys.argv[1] == 'offline':
            config.RUNNING_MODE = RunningMode.OFFLINE
    main(id)