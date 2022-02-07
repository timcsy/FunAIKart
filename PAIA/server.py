from concurrent import futures
from datetime import datetime
import logging
import queue
import sys
import threading

import grpc
import communication.generated.PAIA_pb2_grpc as PAIA_pb2_grpc

from mlagents_envs.environment import UnityEnvironment

import demo
import PAIA
import video
import unity
from config import ENV, bool_ENV, int_ENV

server = None

class PAIAServicer(PAIA_pb2_grpc.PAIAServicer):
    """Provides methods that implement functionality of PAIA server."""

    def __init__(self):
        self.behavior_names = {} # Indexed by id, We let a behavior correspond to an unique agent
        self.ids = {} # Indexed by behavior_name
        self.agent_ids = {} # Indexed by id, an unique agent of a behavior
        self.states = {} # Indexed by behavior_name
        self.actions = {} # Indexed by behavior_name
        self.behavior_name_queue = queue.Queue()
        self.id_queue = queue.Queue()
        self.episode = -1
        self.tmp_dir = None
        self.recording_dir = None
        self.output_video_path = None
        self.current_id = ''
        self.current_usedtime = 0
        self.current_progress = 0
        self.has_demo = False
        self.demo_purename = datetime.now().strftime("%Y%m%d%H%M%S")
        self.env_filepath = unity.get_unity_app()
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
        self.episode += 1
        if self.recording_dir is None:
            self.tmp_dir, self.recording_dir, self.output_video_path = unity.prepare_recording(episode=self.episode)
        else:
            self.tmp_dir, _, self.output_video_path = unity.prepare_recording(episode=self.episode, recording_dir=self.recording_dir)
        if not unity.prepare_demo(episode=self.episode, purename=self.demo_purename) is None:
            self.has_demo = True
        pickups = int_ENV('PLAY_PICKUPS', 0)
        if pickups is None:
            pickups = bool_ENV('PLAY_PICKUPS', True)
        unity.set_config('PickUps', pickups)
        
        logging.info('Waiting for Unity side ...')
        logging.info("Check this file if the game doesn't open:")
        logging.info(self.env_filepath)
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
            self.set_current()
            # end is the server side checking that if reach the max episode
            MAX_EPISODES = int_ENV('MAX_EPISODES', -1)
            end = MAX_EPISODES >= 0 and self.episode >= MAX_EPISODES
            restart = False

            for action in list(self.actions.values()):
                if action.command == PAIA.Command.COMMAND_FINISH or end:
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
                self.finish()
            elif not self.settting_actions:
                self.settting_actions = True # Using spin lock
                self.resume()
    
    def set_current(self):
        try:
            behavior_name = next(iter(self.ids))
            self.current_id = self.ids[behavior_name]
            self.current_usedtime = self.states[behavior_name].observation.usedtime
            self.current_progress = self.states[behavior_name].observation.progress
        except:
            pass
    
    def post_processing(self, is_last=False):
        if not self.tmp_dir is None and not self.output_video_path is None:
            video.generate_video(
                video_dir=self.tmp_dir,
                output_path=self.output_video_path,
                id=self.current_id,
                usedtime=self.current_usedtime,
                progress=self.current_progress
            )
        if is_last and self.has_demo:
            demo.demo_to_paia(purename=self.demo_purename)
        unity.set_config('Records', False)
        unity.set_config('Screen', False)
        unity.set_config('Demo', False)
        unity.set_config('PickUps', False)
    
    def restart(self):
        if self.env_ready:
            self.env_ready = False # Using spin lock
            self.env.close()
            for id in self.ids.values():
                self.id_queue.put(id)
            self.ids = {}
            self.post_processing(is_last=False)
            self.open_env()

    def resume(self):
        self.states_ready = False # Using spin lock
        self.set_actions()
        self.get_states()
    
    def finish(self):
        global server
        print("Game Finished")
        self.states_ready = True
        server.stop(grace=None)
        self.post_processing(is_last=True)
    
    def remove(self, id):
        behavior_name = self.behavior_names[id]
        del self.behavior_names[id]
        del self.ids[behavior_name]
        del self.states[behavior_name]
        del self.actions[behavior_name]
        logging.info(f'Removed player: {id}')

    def hook(self, action: PAIA.Action, context) -> PAIA.State:
        if action.command == PAIA.Command.COMMAND_START:
            self.id_queue.put(action.id)
            logging.info(f'New player: {action.id}')
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

def serve():
    global server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    PAIA_pb2_grpc.add_PAIAServicer_to_server(PAIAServicer(), server)
    port = int_ENV('PAIA_ID', 50051)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '--editor':
            ENV['UNITY_USE_EDITOR'] = 'true'
        else:
            ENV['UNITY_USE_EDITOR'] = 'false'
            ENV['UNITY_APP_AUTO'] = 'false'
            ENV['UNITY_APP_OTHER'] = sys.argv[1]
    serve()