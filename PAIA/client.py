import sys

import grpc
import communication.generated.PAIA_pb2_grpc as PAIA_pb2_grpc

import PAIA
from utils import debug_print

def run(id: str=None) -> None:
    channel = grpc.insecure_channel('localhost:50051')
    stub = PAIA_pb2_grpc.PAIAStub(channel)
    step = 0
    action = PAIA.init_action_object(id)
    while True:
        state = stub.hook(action)
        step += 1
        debug_print('Step:', step)
        # TODO: React to other events
        if state.event != PAIA.EventType.EVENT_NONE:
            break
        action = PAIA.decision(state, step)
        action.id = id

if __name__ == '__main__':
    run(sys.argv[1])