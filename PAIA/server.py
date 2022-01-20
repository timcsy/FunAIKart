from concurrent import futures
import logging
import queue
import sys
import threading

import grpc
import communication.generated.PAIA_pb2_grpc as PAIA_pb2_grpc

from mlagents_envs.environment import UnityEnvironment

import PAIA
import config

class PAIAServicer(PAIA_pb2_grpc.PAIAServicer):
    """Provides methods that implement functionality of PAIA server."""

    def __init__(self, env_filepath=None):
        self.behavior_names = {} # Indexed by id, We let a behavior correspond to an unique agent
        self.ids = {} # Indexed by behavior_name
        self.agent_ids = {} # Indexed by id, an unique agent of a behavior
        self.states = {} # Indexed by behavior_name
        self.actions = {} # Indexed by behavior_name
        self.behavior_name_queue = queue.Queue()
        self.id_queue = queue.Queue()
        self.env_filepath = env_filepath
        self.env = False
        self.env_ready = False
        self.states_ready = False
        self.settting_actions = False
        self.restarting = False
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
        logging.info('Waiting for Unity side ...')
        self.env = UnityEnvironment(file_name=self.env_filepath)
        self.env.reset()
        logging.info('--------------------------------')

        # Behavior names
        logging.info('Behavior names:')
        logging.info(list(self.env.behavior_specs.keys()))

        # Behavior infomation
        logging.debug(0, '--------------------------------')
        logging.debug(0, 'Behavior informations:\n')
        logging.debug(0, dict(self.env.behavior_specs))

        logging.info('--------------------------------')

        # Matching
        for behavior_name in self.env.behavior_specs.keys():
            self.behavior_name_queue.put(behavior_name)
        self.matching()

        self.env_ready = True # Release spin lock

        return self.env
    
    def get_states(self):
        for behavior_name in self.behavior_names.values():
            # Get the new simulation results
            decision_steps, terminal_steps = self.env.get_steps(behavior_name)

            state = None

            # We let a behavior correspond to an unique agent (agent_id = 0)
            for agent_id in decision_steps:
                self.agent_ids[self.ids[behavior_name]] = int(agent_id)
                behavior_spec = self.env.behavior_specs[behavior_name]
                state = PAIA.convert_state_to_object(
                    behavior_spec=behavior_spec,
                    obs_list=decision_steps.obs,
                    event=PAIA.Event.EVENT_RESTART if self.restarting else PAIA.Event.EVENT_NONE,
                    reward=decision_steps.reward
                )
            
            for agent_id in terminal_steps:
                self.agent_ids[self.ids[behavior_name]] = int(agent_id)
                behavior_spec = self.env.behavior_specs[behavior_name]
                state = PAIA.convert_state_to_object(
                    behavior_spec=behavior_spec,
                    obs_list=terminal_steps.obs,
                    event=PAIA.Event.EVENT_FINISH,
                    reward=terminal_steps.reward
                )

            if state is not None:
                self.states[behavior_name] = state
            else: # Occurs when some of the other agents terminate
                self.states[behavior_name].event = PAIA.Event.EVENT_FINISH
        self.states_ready = True # Release spin lock
        self.restarting = False
    
    def set_actions(self):
        self.settting_actions = True
        for behavior_name in self.behavior_names.values():
            action = PAIA.convert_action_to_data(self.actions[behavior_name])
            self.env.set_action_for_agent(behavior_name, self.agent_ids[self.ids[behavior_name]], action)

        self.env.step()

        self.actions = {}
        self.settting_actions = False # Release spin lock

    def check_status(self):
        # Check if we can do the following actions: restart, finish and resume
        if len(self.actions) == len(self.behavior_names) and self.env_ready:
            restart = False
            for action in list(self.actions.values()):
                if action.command == PAIA.Command.COMMAND_FINISH:
                    self.remove(action.id)
                elif action.command == PAIA.Command.COMMAND_RESTART:
                    restart = True
            
            if restart:
                # Finish when an agent want to restart
                self.restarting = True
                self.restart()
            elif len(self.actions) == 0 and self.env_ready:
                # Finish when everyone want to finish
                self.env_ready = False # Using spin lock
                self.env.close()
            elif not self.settting_actions:
                self.settting_actions = True # Using spin lock
                self.resume()
    
    def restart(self):
        if self.env_ready:
            self.env_ready = False # Using spin lock
            self.env.close()
            for id in self.ids.values():
                self.id_queue.put(id)
            self.ids = {}
            self.open_env()

    def resume(self):
        self.states_ready = False # Using spin lock
        self.set_actions()
        self.get_states()
    
    def remove(self, id):
        behavior_name = self.behavior_names[id]
        del self.behavior_names[id]
        del self.ids[behavior_name]
        del self.states[behavior_name]
        del self.actions[behavior_name]
        logging.info('Removed client: ' + str(id))

    def hook(self, action: PAIA.Action, context) -> PAIA.State:
        logging.info(PAIA.action_info(action))
        if action.command == PAIA.Command.COMMAND_START:
            self.id_queue.put(action.id)
            logging.info('New client: ' + str(action.id))
            self.matching()
        else:
            self.actions[self.behavior_names[action.id]] = action
            self.check_status()
        while not self.states_ready or not self.env_ready:
            if self.states_ready and not self.env_ready and len(self.actions) == 0: # Leave infinite loop if finished
                break
        if action.id in self.behavior_names:
            return self.states[self.behavior_names[action.id]]
        else:
            return PAIA.State(event=PAIA.Event.EVENT_FINISH)

def serve(env_filepath=None):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    PAIA_pb2_grpc.add_PAIAServicer_to_server(PAIAServicer(env_filepath), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    env_filepath = None
    if len(sys.argv) > 1:
        env_filepath = sys.argv[1]
    logging.basicConfig(level=config.LOG_LEVEL, format='%(message)s')
    serve(env_filepath)