import logging
import sys
import threading

from config import ENV
import client
import server
import rforward

def main(id: str=None):

    if ENV.get('RUNNING_MODE') == 'CLIENT':
        # Online client
        client.run(id)
    elif ENV.get('RUNNING_MODE') == 'SERVER':
        # Online server
        threads = []
        # Remote port forwarding with SSH
        threads.append(threading.Thread(target=rforward.rforward, args=rforward.team_config()))
        # Run server
        threads.append(threading.Thread(target=server.serve))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
    else:
        # RUNNING_MODE has default value: OFFLINE
        # Offline server and clients
        threads = []
        threads.append(threading.Thread(target=server.serve))
        threads.append(threading.Thread(target=client.run, args=[id]))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

if __name__ == '__main__':
    id = ''
    if len(sys.argv) > 1:
        if sys.argv[1] == 'client':
            ENV.setdefault('RUNNING_MODE', 'CLIENT')
            if len(sys.argv) > 2 and sys.argv[2] == '-n' and len(sys.argv) > 3:
                id = sys.argv[3]
        elif sys.argv[1] == 'server':
            ENV.setdefault('RUNNING_MODE', 'SERVER')
        elif sys.argv[1] == 'offline':
            ENV.setdefault('RUNNING_MODE', 'OFFLINE')
    main(id)