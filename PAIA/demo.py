from typing import List, Optional
from pathlib import Path
import zlib

from mlagents.trainers import demo_loader
from mlagents.trainers.buffer import AgentBuffer, BufferKey, ObservationKeyPrefix
from mlagents_envs.base_env import ActionTuple, BehaviorSpec

import numpy as np

import PAIA
from utils import debug_print

class Demo:
    def __init__(self, path, id: str=None):
        if Path(path).suffix == '.demo':
            self.load_demo(path, id)
        elif Path(path).suffix == '.paia':
            self.load_paia(path)
        else:
            self.load_paia(path)
        self.show()

    def get_observations_from_buffer(buffer: AgentBuffer, behavior_spec: BehaviorSpec, index: int) -> List[np.ndarray]:
        obs_list: List[np.ndarray] = []
        for i, _ in enumerate(behavior_spec.observation_specs):
            obs_single = []
            if index < len(buffer[(ObservationKeyPrefix.OBSERVATION, i)]):
                obs_single = buffer[(ObservationKeyPrefix.OBSERVATION, i)][index]
            # We need to add a dimention at the front (for batch size preserved, even if not using batch)
            # https://numpy.org/doc/stable/reference/generated/numpy.expand_dims.html
            obs_expand = np.expand_dims(obs_single, axis=0)
            obs_list.append(obs_expand)
        return obs_list

    def get_actions_from_buffer(buffer: AgentBuffer, index: int) -> ActionTuple:
        # We need to add a dimention at the front (for agent number)
        # https://numpy.org/doc/stable/reference/generated/numpy.expand_dims.html
        discrete_actions_single = []
        if index < len(buffer[BufferKey.DISCRETE_ACTION]):
            discrete_actions_single = buffer[BufferKey.DISCRETE_ACTION][index]
        discrete_actions = np.expand_dims(discrete_actions_single, axis=0)
        continuous_actions_single = []
        if index < len(buffer[BufferKey.CONTINUOUS_ACTION]):
            continuous_actions_single = buffer[BufferKey.CONTINUOUS_ACTION][index]
        continuous_actions = np.expand_dims(continuous_actions_single, axis=0)
        return ActionTuple(discrete=discrete_actions, continuous=continuous_actions)
    
    def get_rewards_from_buffer(buffer: AgentBuffer, index: int) -> float:
        rewards = 0.0
        if index < len(buffer[BufferKey.ENVIRONMENT_REWARDS]):
            rewards = buffer[BufferKey.ENVIRONMENT_REWARDS][index]
        return rewards
    
    def load_demo(self, path, id: str=None) -> PAIA.Demo:
        behavior_spec, buffer = demo_loader.demo_to_buffer(path, sequence_length=None)

        episodes = []
        steps = []

        for index in range(buffer.num_experiences):
            # Event
            event = PAIA.Event.EVENT_NONE
            if buffer[BufferKey.DONE][index]:
                event = PAIA.Event.EVENT_FINISH
            
            # Reward
            reward = Demo.get_rewards_from_buffer(buffer, index)

            # Observations
            obs_list = Demo.get_observations_from_buffer(buffer, behavior_spec, index)
            state = PAIA.convert_state_to_object(behavior_spec, obs_list, event, reward)

            # Command
            command = PAIA.Command.COMMAND_GENERAL
            if buffer[BufferKey.DONE][index]:
                command = PAIA.Command.COMMAND_FINISH
            
            # Actions
            actions = Demo.get_actions_from_buffer(buffer, index)
            action = PAIA.convert_action_to_object(actions, command, id)

            # Step
            steps.append(PAIA.Step(state=state, action=action))

            # To check whether episode is done
            if buffer[BufferKey.DONE][index]:
                episode = PAIA.Episode(steps=steps)
                episodes.append(episode)
                steps = []
            
            # To check whether demo is finished
            if index == buffer.num_experiences - 1:
                episode = PAIA.Episode(steps=steps)
                if len(steps) > 0:
                    episodes.append(episode)
        
        self.demo = PAIA.Demo(episodes=episodes)
        return self.demo
    
    def load(self):
        # TODO: Add multi path support
        pass
    
    def load_paia(self, path: str):
        with open(path, "rb") as fin:
            decompressed = zlib.decompress(fin.read())
            self.demo = PAIA.Demo()
            self.demo.ParseFromString(decompressed)
    
    def show(self):
        for i in range(len(self.demo.episodes)):
            for j in range(len(self.demo.episodes[i].steps)):
                debug_print('Episode: ' + str(i) + ', Step: ' + str(j))
                debug_print('State:\n' + PAIA.state_info(self.demo.episodes[i].steps[j].state, str(i) + '_' + str(j)))
                debug_print('Action:\n' + PAIA.action_info(self.demo.episodes[i].steps[j].action))
            debug_print('Done, Episode: ' + str(i) + ', Total Steps: ' + str(len(self.demo.episodes[i].steps)) + '\n')
    
    def get_demo(self) -> PAIA.Demo:
        return self.demo
    
    def get_episode(self, episode: int) -> Optional[PAIA.Episode]:
        if episode < len(self.demo.episodes):
            return self.demo.episodes[episode]
        return None
    
    def get_episodes(self) -> List[PAIA.Episode]:
        return list(self.demo.episodes)
    
    def get_step(self, episode: int, step: int) -> Optional[PAIA.Step]:
        if episode < len(self.demo.episodes):
            if step < len(self.demo.episodes[episode].steps):
                return self.demo.episodes[episode].steps[step]
        return None
    
    def get_steps(self, episode: int) -> Optional[List[PAIA.Step]]:
        if episode < len(self.demo.episodes):
            return list(self.demo.episodes[episode].steps)
        return None
    
    def get_state(self, episode: int, step: int) -> Optional[PAIA.State]:
        if episode < len(self.demo.episodes):
            if step < len(self.demo.episodes[episode].steps):
                return self.demo.episodes[episode].steps[step].state
        return None
    
    def get_states(self, episode: int) -> Optional[List[PAIA.State]]:
        if episode < len(self.demo.episodes):
            return [step.state for step in self.demo.episodes[episode].steps]
        return None
    
    def get_action(self, episode: int, step: int) -> Optional[PAIA.Action]:
        if episode < len(self.demo.episodes):
            if step < len(self.demo.episodes[episode].steps):
                return self.demo.episodes[episode].steps[step].action
        return None
    
    def get_actions(self, episode: int) -> Optional[List[PAIA.Action]]:
        if episode < len(self.demo.episodes):
            return [step.action for step in self.demo.episodes[episode].steps]
        return None