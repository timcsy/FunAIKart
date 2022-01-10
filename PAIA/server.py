from concurrent import futures
import queue
import threading

import grpc
import communication.generated.PAIA_pb2_grpc as PAIA_pb2_grpc

from mlagents_envs.environment import UnityEnvironment

import PAIA
from utils import debug_print

class PAIAServicer(PAIA_pb2_grpc.PAIAServicer):
    """Provides methods that implement functionality of PAIA server."""

    def __init__(self):
        self.behavior_names = {} # Indexed by id, We let a behavior correspond to an unique agent (agent_id = 0)
        self.ids = {} # Indexed by behavior_name
        self.states = {} # Indexed by behavior_name
        self.actions = {} # Indexed by behavior_name
        self.behavior_name_queue = queue.Queue()
        self.id_queue = queue.Queue()
        self.env = False
        self.env_ready = False
        self.states_ready = False
        t = threading.Thread(target=self.open_env)
        t.start()
    
    def matching(self):
        '''
        Mapping behavior_name and id
        '''
        while not self.behavior_name_queue.empty() and not self.id_queue.empty():
            behavior_name = self.behavior_name_queue.get()
            id = self.id_queue.get()
            self.behavior_names[id] = behavior_name
            self.ids[behavior_name] = id
        if self.env and len(self.env.behavior_specs) == len(self.ids):
            # Get the first states
            self.get_states()
    
    def open_env(self) -> UnityEnvironment:
        debug_print('Waiting for Unity side ...', depth=1)
        self.env = UnityEnvironment(file_name=None)
        self.env.reset()
        debug_print('--------------------------------')

        # Behavior names
        debug_print('Behavior names:')
        debug_print(list(self.env.behavior_specs.keys()))

        # Behavior infomation
        debug_print('--------------------------------', depth=3)
        debug_print('Behavior informations:\n', depth=3)
        debug_print(dict(self.env.behavior_specs), depth=3)

        debug_print('--------------------------------')

        # Matching
        for behavior_name in self.env.behavior_specs.keys():
            self.behavior_name_queue.put(behavior_name)
        self.matching()

        return self.env
    
    def get_states(self):
        for behavior_name in self.behavior_names.values():
            # Get the new simulation results
            decision_steps, terminal_steps = self.env.get_steps(behavior_name)

            # We let a behavior correspond to an unique agent (agent_id = 0)
            for _ in decision_steps:
                behavior_spec = self.env.behavior_specs[behavior_name]
                state = PAIA.convert_state_to_object(
                    behavior_spec=behavior_spec,
                    obs_list=decision_steps.obs,
                    event=PAIA.Event.EVENT_NONE,
                    reward=decision_steps.reward
                )
            
            for _ in terminal_steps:
                behavior_spec = self.env.behavior_specs[behavior_name]
                state = PAIA.convert_state_to_object(
                    behavior_spec=behavior_spec,
                    obs_list=terminal_steps.obs,
                    event=PAIA.Event.EVENT_FINISH,
                    reward=terminal_steps.reward
                )

            self.states[behavior_name] = state
            self.states_ready = True
    
    def set_actions(self):
        for behavior_name in self.behavior_names.values():
            action = PAIA.convert_action_to_data(self.actions[behavior_name])
            self.env.set_action_for_agent(behavior_name, 0, action)

        self.env.step()

    def check_status(self):
        if len(self.actions) == len(self.behavior_names):
            restart = False
            for action in list(self.actions.values()):
                if action.command == PAIA.Command.COMMAND_FINISH:
                    self.remove(action.id)
                elif action.command == PAIA.Command.COMMAND_RESTART:
                    restart = True
            
            if restart:
                self.restart()
            elif len(self.actions) == 0:
                self.env.close()
            else:
                self.resume()
    
    def restart(self):
        self.env.reset()
        self.env.close()
        for id in self.ids.values():
            self.id_queue.put(id)
        self.ids = []
        self.open_env()

    def resume(self):
        self.states_ready = False
        self.set_actions()
        self.get_states()
    
    def remove(self, id):
        behavior_name = self.behavior_names[id]
        del self.behavior_names[id]
        del self.ids[behavior_name]
        del self.states[behavior_name]
        del self.actions[behavior_name]
        debug_print('Removed client:', id)

    def hook(self, action: PAIA.Action, context) -> PAIA.State:
        if action.command == PAIA.Command.COMMAND_START:
            self.id_queue.put(action.id)
            debug_print('New client:', action.id)
            self.matching()
        else:
            self.actions[self.behavior_names[action.id]] = action
            self.check_status()
        while not self.states_ready:
            pass
        if action.id in self.behavior_names:
            return self.states[self.behavior_names[action.id]]
        else:
            return PAIA.State(event=PAIA.Event.EVENT_FINISH)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    PAIA_pb2_grpc.add_PAIAServicer_to_server(PAIAServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()