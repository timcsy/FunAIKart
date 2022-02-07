import logging
import sys
import threading
import time

from config import ENV
import client
import game
import server
import rforward
import manual
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
    elif ENV.get('RUNNING_MODE') == 'MANUAL':
        # Play manually
        manual.manual()
    elif ENV.get('RUNNING_MODE') == 'GAME':
        # Competition
        game.competition()
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
        elif sys.argv[1] == 'manual':
            ENV['RUNNING_MODE'] = 'MANUAL'
            if len(sys.argv) > 2:
                if sys.argv[2].isnumeric():
                    ENV['MAX_EPISODES'] = sys.argv[2]
                    if len(sys.argv) > 3 and sys.argv[3] == '--pickups' or sys.argv[3] == '-P':
                        ENV['PLAY_PICKUPS'] = sys.argv[4] if len(sys.argv) > 4 else 'true'
                elif sys.argv[2] == '--pickups' or sys.argv[2] == '-P':
                    ENV['PLAY_PICKUPS'] = sys.argv[3] if len(sys.argv) > 3 else 'true'
        elif sys.argv[1] == 'game':
            ENV['RUNNING_MODE'] = 'GAME'
            if len(sys.argv) > 2:
                ENV['GAME_CONTINUE'] = sys.argv[2]
    main()