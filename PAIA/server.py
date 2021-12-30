from concurrent import futures

import grpc
import communication.generated.PAIA_pb2_grpc as PAIA_pb2_grpc

from mlagents_envs.environment import UnityEnvironment

import PAIA
from utils import debug_print

class PAIAServicer(PAIA_pb2_grpc.PAIAServicer):
    """Provides methods that implement functionality of PAIA server."""

    def __init__(self):
        self.online()
    
    def open_env(self) -> UnityEnvironment:
        debug_print('Waiting for Unity side ...', depth=1)
        self.env = UnityEnvironment(file_name=None)
        self.env.reset()
        debug_print('--------------------------------')

        # Behavior names
        debug_print('Behavior names:\n')
        debug_print(self.env.behavior_specs.keys())

        # Behavior infomation
        debug_print('--------------------------------', depth=3)
        debug_print('Behavior informations:\n', depth=3)
        debug_print(dict(self.env.behavior_specs), depth=3)

        return self.env
    
    def online(self):
        # Online
        self.open_env()
        for behavior_name in self.env.behavior_specs.keys():
            pass
        debug_print('--------------------------------')
        debug_print('Online:\n')
        debug_print('--------------------------------')

    def hook(self, action: PAIA.Action, context) -> PAIA.State:
        return PAIA.hook(action)

def serve() -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    PAIA_pb2_grpc.add_PAIAServicer_to_server(PAIAServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()