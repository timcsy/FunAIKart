from datetime import datetime
import importlib
import logging
import os
import pickle
import sys

import grpc
import communication.generated.PAIA_pb2_grpc as PAIA_pb2_grpc

import PAIA
from config import ENV, bool_ENV, int_ENV
from utils import team_config

def run() -> None:
    id = ENV.get('PLAYER_ID', '')
    port = int_ENV('PAIA_ID', 50051)
    channel = grpc.insecure_channel(f'localhost:{port}')
    stub = PAIA_pb2_grpc.PAIAStub(channel)

    ml_play, pickle_path = load()
    brain = ml_play[0]
    is_restart = ml_play[1]
    action = PAIA.init_action_object(id)
    while True:
        try:
            state = stub.hook(action)
        except:
            state = PAIA.State(event=PAIA.Event.EVENT_FINISH)
            action = brain.decision(state)
            break

        if is_restart:
            state.event = PAIA.Event.EVENT_RESTART
            is_restart = False
        
        action = brain.decision(state)
        action.id = id

        if state.event != PAIA.Event.EVENT_NONE:
            if action.command == PAIA.Command.COMMAND_FINISH:
                # Terminate the process if want to finish
                try:
                    state = stub.hook(action)
                except:
                    state = PAIA.State(event=PAIA.Event.EVENT_FINISH)
                action = brain.decision(state)
                break
            elif action.command == PAIA.Command.COMMAND_RESTART or state.event == PAIA.Event.EVENT_RESTART:
                # If the user want to restart, then don't do extra things
                autosave(brain, pickle_path, True)
            else:
                # Force to finish when the user doesn't want to restart
                action.command = PAIA.Command.COMMAND_FINISH
                try:
                    state = stub.hook(action)
                except:
                    state = PAIA.State(event=PAIA.Event.EVENT_FINISH)
                action = brain.decision(state)
                break
        if action.command == PAIA.Command.COMMAND_RESTART:
            autosave(brain, pickle_path, True)
    logging.info('Finishing ...')

def import_brain(import_only=False):
    # Get the module (the definition of the MLPlay class) name
    script_path = ENV.get('PLAY_SCRIPT', 'ml/ml_play.py')
    if not os.path.isabs(script_path):
        script_path = os.path.abspath(script_path)
    
    sys.path.insert(0, os.path.dirname(script_path))
    
    module = os.path.basename(script_path)
    if module.endswith('.py'):
        module = module[:-3]

    ml_play = importlib.import_module(module)
    if not import_only:
        brain = ml_play.MLPlay()

        pickle_path = autosave(brain)
        return brain, pickle_path
    return None

def autosave(brain, pickle_path: str=None, is_restart: bool=False) -> str:
    autosave_enable = bool_ENV('PLAY_AUTOSAVE', True)
    if not autosave_enable:
        return None
    if pickle_path is None:
        prefix = ENV.get('PLAY_AUTOSAVE_PREFIX', 'ml_play')
        if prefix:
            prefix = prefix + '_'
        filename = f'{prefix}{datetime.now().strftime("%Y%m%d%H%M%S")}.pickle'
        autosave_dir = ENV.get('PLAY_AUTOSAVE_DIR', 'autosave')
        pickle_path = os.path.join(autosave_dir, filename)
    if not os.path.exists(os.path.dirname(pickle_path)):
        os.makedirs(os.path.dirname(pickle_path))
    
    with open(pickle_path, 'wb') as fout:
        # Call the autosave method in MLPlay
        brain_autosave = getattr(brain, 'autosave', None)
        if callable(brain_autosave):
            brain.autosave()
        pickle.dump([brain, is_restart], fout)
    
    return pickle_path

def load():
    is_continue = bool_ENV('PLAY_CONTINUE', False)
    autosave_dir = ENV.get('PLAY_AUTOSAVE_DIR', 'autosave')
    pickle_path = None
    if is_continue:
        use_newest = bool_ENV('PLAY_AUTOSAVE_USE_NEWEST', True)
        if not use_newest:
            pickle_path = ENV.get('PLAY_AUTOSAVE_PATH')
        if pickle_path is None and os.path.exists(autosave_dir):
            # Find the newest autosaved kart_timestamp.pickle
            prefix = ENV.get('PLAY_AUTOSAVE_PREFIX', 'ml_play')
            newest_time = 0
            for entry in os.scandir(autosave_dir):
                if entry.is_file():
                    has_prefix = False
                    if prefix:
                        prefix = prefix + '_'
                        has_prefix = True
                    if entry.name.startswith(prefix) and entry.name.endswith('.pickle'):
                        try:
                            time = int(entry.name[len(prefix):-7])
                            if time > newest_time:
                                newest_time = time
                                pickle_path = os.path.join(autosave_dir, entry.name)
                        except ValueError:
                            pass
                    if has_prefix:
                        prefix = prefix[:-1]
        if pickle_path is not None:
            with open(pickle_path, 'rb') as fin:
                import_brain(import_only=True)
                ml_play = pickle.load(fin)
                return ml_play, pickle_path
    
    # Create a new brain
    brain, pickle_path = import_brain()
    return [brain, False], pickle_path

if __name__ == '__main__':
    if 'PLAYER_ID' not in ENV:
        ENV['PLAYER_ID'] = ''
    if len(sys.argv) > 1:
        ENV['PLAYER_ID'] = sys.argv[1]
    if len(sys.argv) > 2:
        ENV['PLAY_SCRIPT'] = sys.argv[2]
    team_config()
    run()