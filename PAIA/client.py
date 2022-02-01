from datetime import datetime
import importlib
import logging
import os
import pickle
import sys

import grpc
import communication.generated.PAIA_pb2_grpc as PAIA_pb2_grpc

import PAIA
import config

def run(id: str='', script_path: str=None, pickle_path: str=None, is_continue: bool=False) -> None:
    channel = grpc.insecure_channel('localhost:50051')
    stub = PAIA_pb2_grpc.PAIAStub(channel)

    ml_play, pickle_path = load(script_path, pickle_path, is_continue)
    brain = ml_play[0]
    is_restart = ml_play[1]
    action = PAIA.init_action_object(id)
    while True:
        state = stub.hook(action)

        if is_restart:
            state.event = PAIA.Event.EVENT_RESTART
            is_restart = False
        
        action = brain.decision(state)
        action.id = id

        if state.event != PAIA.Event.EVENT_NONE:
            if action.command == PAIA.Command.COMMAND_FINISH:
                # Terminate the process if want to finish
                state = stub.hook(action)
                action = brain.decision(state)
                autosave(brain, pickle_path)
                break
            elif action.command == PAIA.Command.COMMAND_RESTART or state.event == PAIA.Event.EVENT_RESTART:
                # If the user want to restart, then don't do extra things
                autosave(brain, pickle_path, True)
            else:
                # Force to finish when the user doesn't want to restart
                action.command = PAIA.Command.COMMAND_FINISH
                state = stub.hook(action)
                action = brain.decision(state)
                autosave(brain, pickle_path)
                break
        if action.command == PAIA.Command.COMMAND_RESTART:
            autosave(brain, pickle_path, True)

def import_brain(script_path: str=None, pickle_path: str=None):
    # Get the module (the definition of the MLPlay class) name
    if script_path is None:
        script_path = 'ml/ml_play'
    if os.path.isabs(script_path):
        module = os.path.relpath(script_path, start=os.path.dirname(__file__))
    else:
        script_path = os.path.join(os.getcwd(), script_path)
        module = os.path.relpath(script_path, start=os.path.dirname(__file__))
    module = module.replace('../', '.')
    module = module.replace('/', '.')
    if module.endswith('.py'):
        module = module[:-3]

    ml_play = importlib.import_module(module)
    brain = ml_play.MLPlay()

    pickle_path = autosave(brain, pickle_path)
    return brain, pickle_path

def autosave(brain, pickle_path: str=None, is_restart: bool=False) -> str:
    if pickle_path is None:
        filename = 'ml_play_' + datetime.now().strftime('%Y%m%d%H%M%S') + '.pickle'
        pickle_path = os.path.join('autosave', filename)
    if not os.path.exists(os.path.dirname(pickle_path)):
        os.makedirs(os.path.dirname(pickle_path))
    
    with open(pickle_path, 'wb') as fout:
        # Call the autosave method in MLPlay
        brain_autosave = getattr(brain, 'autosave', None)
        if callable(brain_autosave):
            brain.autosave()
        pickle.dump([brain, is_restart], fout)
    
    return pickle_path

def load(script_path: str=None, pickle_path: str=None, is_continue: bool=False):
    if is_continue:
        if pickle_path is None and os.path.exists('autosave'):
            # Find the newest autosaved kart_timestamp.pickle
            newest_time = 0
            for entry in os.scandir('autosave'):
                if entry.is_file():
                    if entry.name.startswith('ml_play_') and entry.name.endswith('.pickle'):
                        try:
                            time = int(entry.name[8:-7])
                            if time > newest_time:
                                newest_time = time
                                pickle_path = os.path.join('autosave', entry.name)
                        except ValueError:
                            pass
        if pickle_path is not None:
            with open(pickle_path, 'rb') as fin:
                ml_play = pickle.load(fin)
                return ml_play, pickle_path
    
    # Create a new brain
    brain, pickle_path = import_brain(script_path, pickle_path)
    return [brain, False], pickle_path

if __name__ == '__main__':
    id = str(sys.argv[1]) if len(sys.argv) > 1 else ''
    script_path = str(sys.argv[2]) if len(sys.argv) > 2 else None
    logging.basicConfig(level=config.LOG_LEVEL, format='%(message)s')
    run(id, script_path)