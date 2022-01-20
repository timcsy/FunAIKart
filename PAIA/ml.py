import logging
import sys
import threading

import config
from config import RunningMode
import client
import server

def main(id: str=None):
    if config.RUNNING_MODE == RunningMode.CLIENT:
        # Online client
        client.run(id)
    elif config.RUNNING_MODE == RunningMode.SERVER:
        # Online server
        server.serve()
    elif config.RUNNING_MODE == RunningMode.OFFLINE:
        # Offline server and clients
        threads = []
        threads.append(threading.Thread(target=server.serve))
        threads.append(threading.Thread(target=client.run, args = (id)))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

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
    logging.basicConfig(level=config.LOG_LEVEL, format='%(message)s')
    main(id)