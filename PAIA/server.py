from concurrent import futures
import queue

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
        self.states_ready = False
        self.open_env()
    
    def matching(self):
        while not self.behavior_name_queue.empty() and not self.id_queue.empty():
            behavior_name = self.behavior_name_queue.get()
            id = self.id_queue.get()
            self.behavior_names[id] = behavior_name
            self.ids[behavior_name] = id
        if len(self.env.behavior_specs) == len(self.ids):
            # Get the first states
            self.get_states()
    
    def open_env(self) -> UnityEnvironment:
        debug_print('Waiting for Unity side ...', depth=1)
        self.env = UnityEnvironment(file_name=None)
        self.env.reset()
        debug_print('--------------------------------')

        # Behavior names
        debug_print('Behavior names:\n')
        debug_print(list(self.env.behavior_specs.keys()))

        # Behavior infomation
        debug_print('--------------------------------', depth=3)
        debug_print('Behavior informations:\n', depth=3)
        debug_print(dict(self.env.behavior_specs), depth=3)

        # Matching
        debug_print('--------------------------------')
        debug_print('Online:\n')
        debug_print('--------------------------------')
        # mapping behavior_name and id
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
                    event=PAIA.EventType.EVENT_NONE,
                    reward=decision_steps.reward
                )
            
            for _ in terminal_steps:
                behavior_spec = self.env.behavior_specs[behavior_name]
                state = PAIA.convert_state_to_object(
                    behavior_spec=behavior_spec,
                    obs_list=terminal_steps.obs,
                    event=PAIA.EventType.EVENT_FINISH,
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
            tmp_actions = self.actions
            for action in tmp_actions:
                if action is PAIA.StateType.STATE_FINISH:
                    self.remove(action.id)
                elif action is PAIA.StateType.STATE_RESTART:
                    restart = True
            
            if restart:
                self.env.reset()
            elif len(self.actions) == 0:
                self.env.close()
            else:
                self.resume()
    
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

    def hook(self, action: PAIA.Action, context) -> PAIA.State:
        if action.state == PAIA.StateType.STATE_START:
            self.id_queue.put(action.id)
            self.matching()
        else:
            self.actions[self.behavior_names[action.id]] = action
            self.check_status()
        while not self.states_ready:
            pass
        return self.states[self.behavior_names[action.id]]

def serve() -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    PAIA_pb2_grpc.add_PAIAServicer_to_server(PAIAServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()