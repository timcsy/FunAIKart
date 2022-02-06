import glob
import json
import os
import random
import time
from typing import Any, Dict

from config import ENV, bool_ENV, int_ENV
from utils import get_dir_fileprefix
from video import rank_video

def play(player: Dict[str, Any], index: int, video_basepath: str):
    ENV['PLAYER_ID'] = str(player.get('PLAYER_ID', ENV.get('PLAYER_ID', '')))
    ENV['RECORDING_FILE_PREFIX'] = f'{index}_{ENV["PLAYER_ID"]}'

    if 'PLAY_SCRIPT' in player:
        # Offline
        ENV['PLAY_SCRIPT'] = player['PLAY_SCRIPT']
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
    
    dirname, file_prefix = get_dir_fileprefix('RECORDING', base_dir_default='records')
    base_path = os.path.join(dirname, file_prefix + '_0') # path without extension

    with open(video_basepath + '.rec', 'a') as fout:
        fout.write(f'{ENV["PLAYER_ID"]}\n{base_path}\n')

def read_rec(video_basepath):
    video_prefix = None
    pickup_seed = None
    players = []
    if os.path.exists(video_basepath + '.rec'):
        with open(video_basepath + '.rec', 'r') as fin:
            lines = fin.readlines()
            i = 0
            player = {}
            for line in lines:
                if i == 0:
                    video_prefix = line
                elif i == 1:
                    pickup_seed = line
                elif i % 2 == 0:
                    player['id'] = line
                elif i % 2 == 1:
                    player['video_path'] = line
                    players.append(player)
                    player = {}
                i += 1
    return video_prefix, pickup_seed, players

def competition(is_continue=True):
    players_path = ENV.get('GAME_PLAYERS', 'game/players.json')
    game_players = json.load(players_path)
    video_dir, video_prefix = get_dir_fileprefix('VIDEO', use_dir=False, base_dir_default='video')
    pickup_seed = None
    player_index = 0

    if is_continue:
        paths = glob.glob(f'{video_dir}/*.rec')
        paths.sort(key=lambda p: time.ctime(os.path.getmtime(p)))
        if len(paths) > 0:
            video_prefix = os.path.splitext(os.path.basename(paths[-1]))
            video_basepath = os.path.join(video_dir, video_prefix)
            video_prefix, pickup_seed, players = read_rec(video_basepath)
            player_index = len(players)

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
        with open(video_basepath + '.rec', 'w') as fout:
            fout.write(f'{video_prefix}\n{pickup_seed}\n')

    while player_index < range(len(game_players)):
        play(game_players[player_index], player_index, video_basepath)
        player_index += 1

    ENV['RECORDING_RESULT_SECONDS'] = str(result_time)
    _, _, rank_players = read_rec(video_basepath)
    rank_video(rank_players, video_basepath + '.mp4')