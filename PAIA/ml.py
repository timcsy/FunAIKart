import logging
import sys
import threading
import time

from config import ENV
import client
import server
import rforward
from utils import team_config, server_config

def main():
    if ENV.get('RUNNING_MODE') == 'PLAY':
        # Online client
        team_config()
        client.run()
    elif ENV.get('RUNNING_MODE') == 'ONLINE':
        params = server_config()
        # Online server
        threads = []
        # Run server
        threads.append(threading.Thread(target=server.serve))
        # Remote port forwarding with SSH
        threads.append(threading.Thread(target=rforward.rforward, args=params))
        for thread in threads:
            thread.start()
            time.sleep(1)
        for thread in threads:
            thread.join()
    else:
        # RUNNING_MODE has default value: OFFLINE
        # Offline server and clients
        threads = []
        threads.append(threading.Thread(target=server.serve))
        threads.append(threading.Thread(target=client.run))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

if __name__ == '__main__':
    if 'PLAYER_ID' not in ENV:
        ENV['PLAYER_ID'] = ''
    if len(sys.argv) > 1:
        if sys.argv[1] == 'play':
            ENV['RUNNING_MODE'] = 'PLAY'
            if len(sys.argv) > 2:
                ENV['PLAYER_ID'] = sys.argv[2]
        elif sys.argv[1] == 'online':
            ENV['RUNNING_MODE'] = 'ONLINE'
        elif sys.argv[1] == 'offline':
            ENV['RUNNING_MODE'] = 'OFFLINE'
    main()