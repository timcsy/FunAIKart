import ast
import glob
import json
import logging
import os
import random
import sys
import threading
import time
from typing import Any, Dict, List
import urllib
import shutil
import hashlib
import zipfile
math_round = round

from config import ENV, bool_ENV, int_ENV
import client
import server
import rforward
from utils import get_dir_fileprefix, server_config
from video import rank_video, poster, live

def play(player: Dict[str, Any], index: int):
    ENV['PLAYER_ID'] = str(player.get('PLAYER_ID', ENV.get('PLAYER_ID', '')))
    ENV['PAIA_USERNAME'] = str(player.get('username', ENV.get('PAIA_USERNAME', '')))
    ENV['RECORDING_FILE_PREFIX'] = f'{index}_{ENV["PLAYER_ID"]}'

    if 'PLAY_SCRIPT' in player:
        # Offline
        ENV['PLAY_SCRIPT'] = player['PLAY_SCRIPT']

        # Offline server and clients
        threads = []
        threads.append(threading.Thread(target=server.serve))
        threads.append(threading.Thread(target=client.run))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
    
    else:
        # Online
        if 'PAIA_ID' in ENV:
            ENV['PAIA_ID'] = str(player['PAIA_ID'])
        if 'PAIA_HOST' in ENV:
            ENV['PAIA_HOST'] = str(player['PAIA_HOST'])
        if 'PAIA_PORT' in ENV:
            ENV['PAIA_PORT'] = str(player['PAIA_PORT'])
        if 'PAIA_USERNAME' in ENV:
            ENV['PAIA_USERNAME'] = str(player['PAIA_USERNAME'])
        if 'PAIA_PASSWORD' in ENV:
            ENV['PAIA_PASSWORD'] = str(player['PAIA_PASSWORD'])
        
        params = server_config()
        # Online server
        threads = []
        # Run server
        threads.append(threading.Thread(target=server.serve))
        # Remote port forwarding with SSH
        threads.append(threading.Thread(target=rforward.rforward, args=params))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
    
    dirname, file_prefix = get_dir_fileprefix('RECORDING', base_dir_default='records')
    recording_base_path = os.path.join(dirname, file_prefix + '_0') # path without extension
    
    time.sleep(60)
    return recording_base_path

def read_rec(video_basepath):
    video_prefix = None
    pickup_seed = None
    processing = None
    players = []
    if os.path.exists(video_basepath + '.json'):
        with open(video_basepath + '.json', 'r', encoding="utf-8") as fin:
            rec: Dict[str, Any] = json.load(fin)
            video_prefix = rec.get('video_prefix')
            pickup_seed = rec.get('pickup_seed')
            processing = rec.get('processing')
            if 'players' in rec and isinstance(rec['players'], list):
                players = rec['players']
    return video_prefix, pickup_seed, players, processing

def competition(is_continue: bool=None):
    if is_continue is None:
        is_continue = bool_ENV('GAME_CONTINUE', True)
    players_path = ENV.get('GAME_PLAYERS', 'game/players.json')
    game_players = [] # { "PLAYER_ID", "PLAY_SCRIPT" (or using SSH), "username" }
    with open(players_path, 'r', encoding="utf-8") as fin:
        game_players = json.load(fin)
    video_dir, video_prefix = get_dir_fileprefix('VIDEO', use_dir=False, base_dir_default='video')
    pickup_seed = None
    players = []
    player_index = 0

    if is_continue:
        paths = glob.glob(f'{video_dir}/*.json')
        paths.sort(key=lambda p: time.ctime(os.path.getmtime(p)))
        if len(paths) > 0:
            video_prefix = os.path.splitext(os.path.basename(paths[-1]))[0]
            video_basepath = os.path.join(video_dir, video_prefix)
            _video_prefix, _pickup_seed, _players, _processing = read_rec(video_basepath)
            if not _processing:
                is_continue = False
            else:
                player_index = len(_players)
                if _video_prefix is None:
                    _video_prefix = os.path.splitext(os.path.basename(paths[-1]))[0]
                if _video_prefix is None or _pickup_seed is None:
                    is_continue = False
                else:
                    video_prefix, pickup_seed, players = _video_prefix, _pickup_seed, _players
        else:
            is_continue = False

    print(video_dir, video_prefix)
    video_basepath = os.path.join(video_dir, video_prefix)
    if pickup_seed is None:
        # pickup_seed is not set before
        pickup_seed = int_ENV('PLAY_PICKUPS')
        if pickup_seed is None:
            pickup_seed = bool_ENV('PLAY_PICKUPS', True)
        if pickup_seed is True:
            pickup_seed = random.randint(0, 65536)
    ENV['PLAY_PICKUPS'] = str(pickup_seed)
    ENV['PLAY_CONTINUE'] = 'false'
    ENV['PLAY_AUTOSAVE'] = 'false'
    ENV['MAX_EPISODES'] = '1'
    ENV['DEMO_ENABLE'] = 'false'
    ENV['IMAGE_ENABLE'] = 'false'
    ENV['RECORDING_ENABLE'] = 'true'
    ENV['RECORDING_USE_DIR'] = 'true'
    ENV['RECORDING_DIR_PREFIX'] = video_prefix
    ENV['RECORDING_DIR_TIMESTAMP'] = 'false'
    ENV['RECORDING_FILE_TIMESTAMP'] = 'false'
    ENV['RECORDING_SAVE_REC'] = 'true'
    ENV['RECORDING_PERIOD'] = '1'
    if not 'VIDEO_PRESERVE_SECONDS' in ENV:
        ENV['VIDEO_PRESERVE_SECONDS'] = '75'
    result_time = int_ENV('RECORDING_RESULT_SECONDS', 10) # temporary store the original result time for later use
    ENV['RECORDING_RESULT_SECONDS'] = ENV['VIDEO_PRESERVE_SECONDS']

    if not is_continue:
        if not os.path.exists(video_dir):
            os.makedirs(video_dir)
        with open(video_basepath + '.json', 'w') as fout:
            rec = {
                'processing': True,
                'video_prefix': video_prefix,
                'pickup_seed': pickup_seed
            }
            json.dump(rec, fout, indent=4)

    while player_index < len(game_players):
        recording_base_path = play(game_players[player_index], player_index)
        players.append({
            'id': ENV["PLAYER_ID"],
            'recording_base_path': recording_base_path,
            'username': ENV["PAIA_USERNAME"]
        })
        with open(video_basepath + '.json', 'w') as fout:
            rec = {
                'video_prefix': video_prefix,
                'pickup_seed': pickup_seed,
                'players': players
            }
            json.dump(rec, fout, indent=4)
        player_index += 1


    ENV['RECORDING_RESULT_SECONDS'] = str(result_time)
    _, _, players, _ = read_rec(video_basepath)
    rank_players = []
    for i in range(len(players)):
        with open(players[i]['recording_base_path'] + '.json', 'r', encoding="utf-8") as fin:
            p = json.load(fin) # Already has id, usedtime, progress, username
            p['video_path'] = players[i]['recording_base_path'] + '.mp4'
            p['index'] = i
            rank_players.append(p)

    # sort the players
    rank_players.sort(key=lambda p: (-int(round(p['progress'] * 100, 0)), round(p['usedtime'], 2)))
    for i in range(len(rank_players)):
        rank_players[i]['rank'] = i + 1
    rank_players.sort(key=lambda p: p['index'])
    rank_video(rank_players, video_basepath + '.mp4')
    poster(video_basepath)
    live(video_basepath)
    rank_players.sort(key=lambda p: p['rank'])
    
    paths = glob.glob(video_basepath + '*')
    zf = zipfile.ZipFile(video_basepath + '.zip', 'w', zipfile.ZIP_DEFLATED)
    for path in paths:
        zf.write(path)
        os.remove(path)
    
    return rank_players, video_basepath


def download(usernames: List[str]):
    host = ENV.get('GAME_HOST', 'http://localhost:49550')
    dirname = ENV.get('GAME_MODEL_DIR', 'models')
    players_path = ENV.get('GAME_PLAYERS', 'game/players.json')
    players = []

    for username in usernames:
        id = None
        try:
            team = hashlib.md5(username.encode()).hexdigest()
            with urllib.request.urlopen(f'{host}/api/models/{team}') as response:
                filename = response.info().get_filename()
                if not os.path.exists(dirname):
                    os.makedirs(dirname)
                filepath = os.path.join(dirname, filename)
                inferencing = response.info()['inferencing']
                id = ast.literal_eval(response.info()['player'])
                with open(filepath, 'wb') as fout:
                    shutil.copyfileobj(response, fout)
                import zipfile
                with zipfile.ZipFile(filepath, 'r') as zip_ref:
                    targetdir = os.path.join(dirname, username)
                    if os.path.exists(targetdir):
                        shutil.rmtree(targetdir)
                    zip_ref.extractall(targetdir)
                os.remove(filepath)

                script_path = glob.glob(f'{targetdir}/{inferencing}')
                if len(script_path) == 0:
                    script_path = os.path.abspath(glob.glob(f'{targetdir}/**/{inferencing}')[0])
                else:
                    script_path = script_path[0]
                script_path = os.path.abspath(script_path)
                if os.path.exists(script_path):
                    to_cpu(script_path)

            players.append({
                'PLAYER_ID': id,
                'PLAY_SCRIPT': script_path,
                'username': username
            })
        except Exception as e:
            print(e)
            logging.info(username + ' is using the default no action script.')
            if id is None:
                id = username
            players.append({
                'PLAYER_ID': id,
                'PLAY_SCRIPT': 'no_action.py',
                'username': username
            })
            pass
    if not os.path.exists(os.path.dirname(players_path)):
        os.makedirs(os.path.dirname(players_path))
    with open(players_path, 'w') as fout:
        fout.write(json.dumps(players, indent=4))

def get_teamname(username, game_nodes):
    teamnames = [node['game'] for node in game_nodes if node.get('player') == username]
    if len(teamnames) > 0:
        return teamnames[0]
    else:
        return None

def recursive_competition(parent, game_nodes):
    children = [node for node in game_nodes if node.get('next') == parent['game']]
    usernames = []
    for child in children:
        if 'player' in child:
            usernames.append(child['player'])
        else:
            usernames.append(recursive_competition(child, game_nodes))
    download(usernames)
    round = 0
    points = { username: 0 for username in usernames }
    while True:
        round += 1
        round_text = f'{parent["game"]}'
        print(f'{round_text}：', usernames)
        rank_players, video_basepath  = competition()
        rank = [p.get('username') for p in rank_players]
        for i in range(len(rank)):
            print(rank)
            print(points)
            points[rank[i]] += 3 - i
            rank_players[i]['points'] = points[rank[i]]
        with open(video_basepath + '.json', 'w') as fout:
            info = {
                'game': os.path.basename(video_basepath),
                'round': round_text,
                'result': {
                    get_teamname(rank_players[i]['username'], game_nodes): {
                        '名次': i + 1,
                        '積分': rank_players[i]['points'],
                        '玩家名稱': rank_players[i]['id'],
                        '花費時間（秒）': math_round(rank_players[i]['usedtime'], 2),
                        '完成進度（%）': int(math_round(rank_players[i]['progress'] * 100, 0))
                    }
                    for i in range(len(rank_players))
                }
            }
            json.dump(info, fout, indent=4)
        # argmax = [k for k in points.keys() if points[k] == max(points.values())]
        # if round >= 3:
        #     if len(argmax) > 1:
        #         download(argmax)
        #         usernames = argmax
        #     else:
        #         break
        return usernames[0]
    return usernames[0]

def to_cpu(inferencing):
    #read input file
    fin = open(inferencing, "r")
    #read file contents to string
    data = fin.read()
    #replace all occurrences of the required string
    data = data.replace("self.device = 'cuda'", "self.device = 'cpu'")
    #close the input file
    fin.close()
    #open the input file in write mode
    fin = open(inferencing, "w")
    #overrite the input file with the resulting data
    fin.write(data)
    #close the file
    fin.close()

def schedule():
    schedule = ENV.get('GAME_SCHEDULE', 'game/schedule.json')
    game_nodes = []
    with open(schedule, 'r', encoding="utf-8") as fin:
        game_nodes = json.load(fin)
    
    root = [node for node in game_nodes if not 'next' in node][0]
    recursive_competition(root, game_nodes)

if __name__ == '__main__':
    if len(sys.argv) > 2:
        ENV['GAME_CONTINUE'] = sys.argv[2]
    # competition()
    # download(['funai0305', 'funai0101'])
    schedule()