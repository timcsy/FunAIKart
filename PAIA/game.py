import json
from typing import Any, Dict

from config import ENV

def play(player: Dict[str, Any]):
    ENV['PLAYER_ID'] = str(player.get('PLAYER_ID', ENV.get('PLAYER_ID', '')))
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

def competition():
    pass