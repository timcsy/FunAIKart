from __future__ import annotations
import glob
import logging
import os
import time
from typing import List, Union
from pathlib import Path
import zlib

import numpy as np

from mlagents.trainers import demo_loader
from mlagents.trainers.buffer import AgentBuffer, BufferKey, ObservationKeyPrefix
from mlagents_envs.base_env import ActionTuple, BehaviorSpec

from config import bool_ENV
import PAIA
from utils import get_dir_fileprefix
import unity

class Demo:
    def __init__(self, paths: Union[List[str], str]=None, show=False, id: str=None):
        self._episodes: List[List[PAIA.Step]] = []
        self._index = -1
        if paths is not None:
            self.load(paths, id)
            if show:
                self.show()
    
    def load(self, paths: Union[List[str], str]=None, id: str=None) -> List[List[PAIA.Step]]:
        if paths is None:
            paths = []
        elif type(paths) is str:
            paths = [paths]
        
        self._episodes = []
        for path in paths:
            episodes = None
            if Path(path).suffix == '.demo':
                episodes = self.__load_demo(path, id)
            elif Path(path).suffix == '.paia':
                episodes = self.__load_paia(path)
            else:
                episodes = self.__load_paia(path)
            if not episodes is None:
                self._episodes.extend(episodes)
        self._index += len(self._episodes)

        return self._episodes
    
    def export(self, path: str='kart.paia') -> None:
        with open(path, "wb") as fout:
            demo = PAIA.Demo()
            for steps in self._episodes:
                episode = PAIA.Episode()
                for step in steps:
                    episode.steps.append(step)
                demo.episodes.append(episode)
            compressed = zlib.compress(demo.SerializeToString())
            fout.write(compressed)
    
    def create_demo() -> Demo:
        demo = Demo()
        demo.create_episode()
        return demo

    def create_episode(self) -> None:
        self._episodes.append([])
        self._index += 1
    
    def create_step(self, state: PAIA.State, action: PAIA.Action) -> None:
        self.add_step(PAIA.Step(state=state, action=action))
    
    def add_step(self, step: PAIA.Step, episode_index: int=None) -> None:
        if episode_index is None:
            self._episodes[self._index].append(step)
        else:
            self._episodes[episode_index].append(step)
    
    def add_steps(self, steps: List[PAIA.Step], episode_index: int=None) -> None:
        if episode_index is None:
            self._episodes[self._index].extend(steps)
        else:
            self._episodes[episode_index].extend(steps)
    
    def show(self) -> None:
        episodes = self.__call__()
        for i in range(len(episodes)):
            for j in range(len(episodes)):
                logging.debug(f'Episode: {i}, Step: {j}')
                logging.debug(f'State:\n{episodes[i][j].state}')
                logging.debug(f'Action:\n{episodes[i][j].action}')
            logging.debug(f'Done, Episode: {i}, Total Steps: {len(episodes)}\n')
    

    # The following methods are same as list methods, feel free to use Demo object instance as list!

    def append(self, episode: PAIA.Episode):
        self._episodes.append(episode)
        self._index += 1
    
    def extend(self, episodes: List[PAIA.Episode]):
        self._episodes.extend(episodes)
        self._index += len(episodes)
    
    def insert(self, index: int, episode: PAIA.Episode):
        self._episodes.insert(index, episode)
        self._index += 1

    def pop(self, index: int=-1):
        self._index -= 1
        return self._episodes.pop(index)
    
    def clear(self):
        self._episodes.clear()
        self._index = -1
    
    def index(self, episode: PAIA.Episode, *args, **kwargs):
        return self._episodes.index(episode, *args, **kwargs)
    
    def count(self, episode: PAIA.Episode):
        return self._episodes.count(episode)
    
    def sort(self, *args, **kwargs):
        self._episodes.sort(*args, **kwargs)
    
    def reverse(self):
        self._episodes.reverse()
    
    def copy(self):
        return self._episodes.copy()
    
    def __getitem__(self, key):
        return self._episodes[key]

    def __setitem__(self, key, value):
        self._episodes[key] = value
    
    def __delitem__(self, key):
        self._index -= 1
        del self._episodes[key]
    
    def __missing__(self, key):
        return None
    
    def __contains__(self, key):
        return key in self._episodes
    
    def __iter__(self):
        return iter(self._episodes)
    
    def __len__(self):
        return len(self._episodes)
    
    def __repr__(self):
        return repr(self._episodes)
    
    def __reverse__(self):
        return reversed(self._episodes)
    
    def __str__(self):
        return str(self.__call__())

    # Using demo_instance(episode_indices, step_indices) to get demo with image enabled or not
    def __call__(self, episode_indices=None, step_indices=None):
        if isinstance(episode_indices, int):
            return self.__get_steps(self._episodes[episode_indices], episode_indices, step_indices)
        elif isinstance(episode_indices, list):
            return [
                self.__get_steps(self._episodes[episode_index], episode_index, step_indices)
                for episode_index in episode_indices
            ]
        elif episode_indices is None:
            return [
                self.__get_steps(self._episodes[episode_index], episode_index, step_indices)
                for episode_index in range(len(self._episodes))
            ]
    

    # The following methods are private

    def __get_steps(self, episode, episode_index, step_indices):
        if isinstance(step_indices, int):
            return PAIA.Step(
                state=PAIA.state_info(episode[step_indices].state, f'{episode_index}_{step_indices}'),
                action=PAIA.action_info(episode[step_indices].action)
            )
        elif isinstance(step_indices, list):
            return [
                PAIA.Step(
                    state=PAIA.state_info(episode[step_index].state, f'{episode_index}_{step_index}'),
                    action=PAIA.action_info(episode[step_index].action)
                )
                for step_index in step_indices
            ]
        elif step_indices is None:
            return [
                PAIA.Step(
                    state=PAIA.state_info(episode[step_index].state, f'{episode_index}_{step_index}'),
                    action=PAIA.action_info(episode[step_index].action)
                )
                for step_index in range(len(episode))
            ]
    
    def __get_observations_from_buffer(buffer: AgentBuffer, behavior_spec: BehaviorSpec, index: int) -> List[np.ndarray]:
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

    def __get_actions_from_buffer(buffer: AgentBuffer, index: int) -> ActionTuple:
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
    
    def __get_rewards_from_buffer(buffer: AgentBuffer, index: int) -> float:
        rewards = 0.0
        if index < len(buffer[BufferKey.ENVIRONMENT_REWARDS]):
            rewards = buffer[BufferKey.ENVIRONMENT_REWARDS][index]
        return rewards
    
    def __load_demo(self, path, id: str=None) -> List[List[PAIA.Step]]:
        behavior_spec, buffer = demo_loader.demo_to_buffer(path, sequence_length=None)

        episodes = []
        steps = []

        for index in range(buffer.num_experiences):
            # Event
            event = PAIA.Event.EVENT_NONE
            if buffer[BufferKey.DONE][index]:
                event = PAIA.Event.EVENT_FINISH
            
            # Reward
            reward = Demo.__get_rewards_from_buffer(buffer, index)

            # Observations
            obs_list = Demo.__get_observations_from_buffer(buffer, behavior_spec, index)
            state = PAIA.convert_state_to_object(behavior_spec, obs_list, event, reward)

            # Command
            command = PAIA.Command.COMMAND_GENERAL
            if buffer[BufferKey.DONE][index] or state.event != PAIA.Event.EVENT_NONE:
                command = PAIA.Command.COMMAND_FINISH
            
            # Actions
            actions = Demo.__get_actions_from_buffer(buffer, index)
            action = PAIA.convert_action_to_object(actions, command, id)

            # Step
            steps.append(PAIA.Step(state=state, action=action))

            # To check whether episode is done
            if command == PAIA.Command.COMMAND_FINISH:
                episodes.append(steps)
                steps = []
            
            # To check whether demo is finished
            if index == buffer.num_experiences - 1:
                if len(steps) > 0:
                    episodes.append(steps)
        
        return episodes
    
    def __load_paia(self, path: str) -> List[List[PAIA.Step]]:
        with open(path, "rb") as fin:
            decompressed = zlib.decompress(fin.read())
            demo = PAIA.Demo()
            demo.ParseFromString(decompressed)
            episodes = [[step for step in episode.steps] for episode in demo.episodes]
            return episodes


# The following are demo utils

def demo_to_paia(purename, paia_dir=None, paia_prefix=None, all_in_one: bool=None, remove_original: bool=True):
    if all_in_one is None:
        all_in_one = bool_ENV('DEMO_ALL_IN_ONE', True)
    
    dirname, file_prefix = get_dir_fileprefix('DEMO', base_dir_default='demo', use_dir_default=not all_in_one)
    if paia_dir is None:
        paia_dir = dirname
    if not os.path.isabs(paia_dir):
        paia_dir = os.path.join(os.getcwd(), paia_dir)
    
    if not os.path.exists(paia_dir):
        os.makedirs(paia_dir)
    
    if paia_prefix is None:
        paia_prefix = file_prefix
    
    if all_in_one:
        demo_all = Demo()
    
    tmp_dir = os.path.join(unity.get_unity_dir(), 'Demo')
    paths = glob.glob(f'{os.path.join(tmp_dir, purename)}*.demo')
    paths.sort(key=lambda p: time.ctime(os.path.getmtime(p)))

    for path in paths:
        demo = Demo(path)
        if all_in_one:
            demo_all.append(demo[0])
        else:
            demo_filename = os.path.basename(path)
            demo_filename = demo_filename[demo_filename.startswith(purename) and len(purename):-5]
            demo_filename = paia_prefix + '_' + demo_filename + '.paia'
            demo_once = Demo()
            demo_once.append(demo[0])
            os.path.join(paia_dir, demo_filename)
            demo_once.export(os.path.join(paia_dir, demo_filename))
        if remove_original:
            os.remove(path)

    if all_in_one:
        demo_all.export(os.path.join(paia_dir, paia_prefix) + '.paia')

def get_info(demo_name):
    path = None
    if not demo_name is None:
        tmp_dir = os.path.join(unity.get_unity_dir(), 'Demo')
        path = os.path.join(tmp_dir, demo_name + '.demo')
    usedtime = -1
    progress = -1
    if path and os.path.exists(path):
        demo = Demo(path)
        step = demo[0][-1]
        if step:
            usedtime = step.state.observation.usedtime
            progress = step.state.observation.progress
    return usedtime, progress