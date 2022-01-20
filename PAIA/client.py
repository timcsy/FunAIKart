import importlib
import logging
import os
import sys

import grpc
import communication.generated.PAIA_pb2_grpc as PAIA_pb2_grpc

import PAIA
import config

def run(id: str='', filepath: str='ml_play') -> None:
    channel = grpc.insecure_channel('localhost:50051')
    stub = PAIA_pb2_grpc.PAIAStub(channel)

    # Get the module (the definition of the MLPlay class) name
    if os.path.isabs(filepath):
        module = os.path.relpath(filepath, start=os.path.dirname(__file__))
    else:
        filepath = os.path.join(os.getcwd(), filepath)
        module = os.path.relpath(filepath, start=os.path.dirname(__file__))
    module = module.replace('../', '.')
    module = module.replace('/', '.')
    if module.endswith('.py'):
        module = module[:-3]

    ml_play = importlib.import_module(module)
    brain = ml_play.MLPlay()
    action = PAIA.init_action_object(id)
    while True:
        state = stub.hook(action)
        action = brain.decision(state)
        action.id = id
        if state.event != PAIA.Event.EVENT_NONE:
            if action.command == PAIA.Command.COMMAND_FINISH:
                # Terminate the process if want to finish
                state = stub.hook(action)
                action = brain.decision(state)
                break
            elif action.command == PAIA.Command.COMMAND_RESTART or state.event == PAIA.Event.EVENT_RESTART:
                # If the user want to restart, then don't do extra things
                pass
            else:
                # Force to finish when the user doesn't want to restart
                action.command = PAIA.Command.COMMAND_FINISH
                state = stub.hook(action)
                action = brain.decision(state)
                break

if __name__ == '__main__':
    id = str(sys.argv[1]) if len(sys.argv) > 1 else ''
    filepath = str(sys.argv[2]) if len(sys.argv) > 2 else None
    logging.basicConfig(level=config.LOG_LEVEL, format='%(message)s')
    run(id, filepath)