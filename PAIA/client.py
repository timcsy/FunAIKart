import sys

import grpc
import communication.generated.PAIA_pb2_grpc as PAIA_pb2_grpc

import PAIA

def run(id: str=None) -> None:
    channel = grpc.insecure_channel('localhost:50051')
    stub = PAIA_pb2_grpc.PAIAStub(channel)
    action = PAIA.init_action_object(id)
    while True:
        if state.event != PAIA.EventType.EVENT_NONE:
            break
        state = stub.hook(action)
        # TODO: Convert the image data using np.frombuffer(image, dtype=np.float32)
        action = PAIA.decision(state)

if __name__ == '__main__':
    run(sys.argv[1])