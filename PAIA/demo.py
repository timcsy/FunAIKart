from typing import Dict, List, Optional

from mlagents.trainers import demo_loader
from mlagents.trainers.buffer import AgentBuffer, BufferKey, ObservationKeyPrefix, RewardSignalKeyPrefix
from mlagents_envs.base_env import ActionTuple, BehaviorSpec

import numpy as np

import PAIA
from utils import debug_print

class Demo:
    def __init__(self, path, id: str=None):
        self.behavior_spec, self.buffer = demo_loader.demo_to_buffer(path, sequence_length=None)
        self.load(id)
        self.index = 0

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
    
    def load(self, id: str=None) -> None:
        self.episodes = []
        steps = []

        for index in range(self.buffer.num_experiences):
            # Show the step information
            debug_print('Episode: ' + str(len(self.episodes)) + ', Step: ' + str(len(steps)))
            
            # Event
            event = PAIA.EventType.EVENT_NONE
            if self.buffer[BufferKey.DONE][index]:
                event = PAIA.EventType.EVENT_FINISH
            
            # Show the reward
            reward = Demo.get_rewards_from_buffer(self.buffer, index)
            debug_print('Reward: ' + str(reward))
            
            # Show observations
            obs_list = Demo.get_observations_from_buffer(self.buffer, self.behavior_spec, index)
            state = PAIA.convert_state_to_object(self.behavior_spec, obs_list, event, reward)
            debug_print('State:\n' + PAIA.state_info(state))

            # Action state
            action_state = PAIA.StateType.STATE_NONE
            if self.buffer[BufferKey.DONE][index]:
                action_state = PAIA.EventType.STATE_FINISH
            
            # Show actions
            actions = Demo.get_actions_from_buffer(self.buffer, index)
            action = PAIA.convert_action_to_object(actions, action_state, id)
            debug_print('Action:\n' + PAIA.action_info(action))

            steps.append({
                'state': state,
                'action': action
            })

            # To check whether episode is done, and show the summary
            if self.buffer[BufferKey.DONE][index]:
                debug_print()
                debug_print('Done, Episode: ' + str(len(self.episodes)) + ', Total Steps: ' + str(len(steps)))
                self.episodes.append(steps)
                steps = []
            
            # To check whether demo is finished, and show the summary
            if index == self.buffer.num_experiences - 1:
                self.episodes.append(steps)
                debug_print()
                debug_print('Finish, Episodes: ' + str(len(self.episodes)) + ', Total Steps: ' + str(len(steps)))
            
            debug_print()
    
    def get_step(self, episode: int, step: int) -> Optional[Dict]:
        if episode < len(self.episodes):
            if step < len(self.episodes[episode]):
                return self.episodes[episode][step]
        return None
    
    def get_steps(self, episode: int) -> Optional[List[Dict]]:
        if episode < len(self.episodes):
            return self.episodes[episode]
        return None
    
    def get_state(self, episode: int, step: int) -> Optional[PAIA.State]:
        if episode < len(self.episodes):
            if step < len(self.episodes[episode]):
                return self.episodes[episode][step]['state']
        return None
    
    def get_states(self, episode: int) -> Optional[List[PAIA.State]]:
        if episode < len(self.episodes):
            return [step['state'] for step in self.episodes[episode]]
        return None
    
    def get_action(self, episode: int, step: int) -> Optional[PAIA.Action]:
        if episode < len(self.episodes):
            if step < len(self.episodes[episode]):
                return self.episodes[episode][step]['action']
        return None
    
    def get_actions(self, episode: int) -> Optional[List[PAIA.Action]]:
        if episode < len(self.episodes):
            return [step['action'] for step in self.episodes[episode]]
        return None