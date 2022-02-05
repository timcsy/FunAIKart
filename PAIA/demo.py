from __future__ import annotations
import glob
import logging
import os
import time
from typing import List, Optional, Union
from pathlib import Path
import zlib

from mlagents.trainers import demo_loader
from mlagents.trainers.buffer import AgentBuffer, BufferKey, ObservationKeyPrefix
from mlagents_envs.base_env import ActionTuple, BehaviorSpec

import numpy as np

from config import ENV, to_bool
import PAIA
from utils import get_dir_fileprefix
import unity

class Demo:
    def __init__(self, paths: Union[List[str], str, None]=None, id: str=None, img_dir: str=None):
        if paths is not None:
            self.load(paths, id)
            self.show(img_dir)
        else:
            self.demo = PAIA.Demo()
        self.index = -1

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
            if buffer[BufferKey.DONE][index] or state.event != PAIA.Event.EVENT_NONE:
                command = PAIA.Command.COMMAND_FINISH
            
            # Actions
            actions = Demo.get_actions_from_buffer(buffer, index)
            action = PAIA.convert_action_to_object(actions, command, id)

            # Step
            steps.append(PAIA.Step(state=state, action=action))

            # To check whether episode is done
            if command == PAIA.Command.COMMAND_FINISH:
                episode = PAIA.Episode(steps=steps)
                episodes.append(episode)
                steps = []
            
            # To check whether demo is finished
            if index == buffer.num_experiences - 1:
                episode = PAIA.Episode(steps=steps)
                if len(steps) > 0:
                    episodes.append(episode)
        
        demo = PAIA.Demo(episodes=episodes)
        return demo
    
    def load_paia(self, path: str) -> PAIA.Demo:
        with open(path, "rb") as fin:
            decompressed = zlib.decompress(fin.read())
            demo = PAIA.Demo()
            demo.ParseFromString(decompressed)
            return demo
    
    def load(self, paths: Union[List[str], str, None], id: str=None) -> PAIA.Demo:
        if paths is None:
            paths = []
        elif type(paths) is str:
            paths = [paths]
        
        self.demo = PAIA.Demo()
        for path in paths:
            demo = PAIA.Demo()
            if Path(path).suffix == '.demo':
                demo = self.load_demo(path, id)
            elif Path(path).suffix == '.paia':
                demo = self.load_paia(path)
            else:
                demo = self.load_paia(path)
            self.demo.episodes.extend(demo.episodes)
        
        return self.demo
    
    def export(self, path: str='kart.paia') -> None:
        with open(path, "wb") as fout:
            compressed = zlib.compress(self.demo.SerializeToString())
            fout.write(compressed)
    
    def show(self, img_dir: str=None) -> None:
        for i in range(len(self.demo.episodes)):
            for j in range(len(self.demo.episodes[i].steps)):
                logging.debug(f'Episode: {i}, Step: {j}')
                logging.debug(f'State:\n{PAIA.state_info(self.demo.episodes[i].steps[j].state)}', f'{i}_{j}', img_dir)
                logging.debug(f'Action:\n{PAIA.action_info(self.demo.episodes[i].steps[j].action)}')
            logging.debug(f'Done, Episode: {i}, Total Steps: {len(self.demo.episodes[i].steps)}\n')
    
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
    
    def create_demo() -> Demo:
        demo = Demo()
        demo.create_episode()
        return demo

    def create_episode(self) -> None:
        self.demo.episodes.add()
        self.index += 1
    
    def create_step(self, state: PAIA.State, action: PAIA.Action) -> None:
        self.add_step(PAIA.Step(state=state, action=action))
    
    def add_step(self, step: PAIA.Step, episode: int=-1) -> None:
        if episode != -1:
            self.demo.episodes[episode].steps.append(step)
        else:
            self.demo.episodes[self.index].steps.append(step)
    
    def add_steps(self, steps: List[PAIA.Step], episode: int=-1) -> None:
        if episode != -1:
            self.demo.episodes[episode].steps.extend(steps)
        else:
            self.demo.episodes[self.index].steps.extend(steps)
    
    def add_episode(self, episode: PAIA.Episode) -> None:
        self.demo.episodes.append(episode)
    
    def add_episodes(self, episodes: List[PAIA.Episode]) -> None:
        self.demo.episodes.extend(episodes)

def demo_to_paia(purename, paia_dir=None, paia_prefix=None, all_in_one: bool=None, remove_original: bool=True):
    if all_in_one is None:
        all_in_one = to_bool(ENV.get('DEMO_ALL_IN_ONE'), True)
    
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
        demo = Demo()
        demo.load(path)
        if all_in_one:
            demo_all.add_episode(demo.get_episode(0))
        else:
            demo_filename = os.path.basename(path)
            demo_filename = demo_filename[demo_filename.startswith(purename) and len(purename):-5]
            demo_filename = paia_prefix + demo_filename + '.paia'
            demo_once = Demo()
            demo_once.add_episode(demo.get_episode(0))
            os.path.join(paia_dir, demo_filename)
            demo_once.export(os.path.join(paia_dir, demo_filename))
        if remove_original:
            os.remove(path)

    if all_in_one:
        demo_all.export(os.path.join(paia_dir, paia_prefix) + '.paia')