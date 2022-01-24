# api_version: PAIAKart_1.0

import io
import logging
import os
from typing import List

import numpy as np
from PIL import Image

from mlagents_envs.base_env import BehaviorSpec, ActionTuple

from communication.generated import PAIA_pb2
import config

Event = PAIA_pb2.Event
State = PAIA_pb2.State
Command = PAIA_pb2.Command
Action = PAIA_pb2.Action
Step = PAIA_pb2.Step
Episode = PAIA_pb2.Episode
Demo = PAIA_pb2.Demo

def image_to_array(data: bytes) -> np.ndarray:
    """
    Convert bytes data field of protocol buffer to numpy array.
    :param data: bytes (with PNG, ... format).
    :return: Numpy array (range from 0 to 1).
    """
    with Image.open(io.BytesIO(data)) as image:
        array = np.array(image).astype(np.float32) / 255.0
        return array

def array_to_image(array: np.ndarray) -> bytes:
    """
    Convert numpy array to bytes data (can be used by the field of protocol buffer).
    :param array: Numpy array (range from 0 to 1).
    :return: bytes (PNG format).
    """
    image = Image.fromarray((255 * array).astype(np.uint8)) # Convert to PIL format
    imgByteArr = io.BytesIO()
    image.save(imgByteArr, format='PNG')
    return imgByteArr.getvalue()

def convert_state_to_object(behavior_spec: BehaviorSpec, obs_list: List[np.ndarray], event: Event, reward: float=0.0) -> State:
    state = State(api_version='PAIAKart_1.0')
    for index, obs_spec in enumerate(behavior_spec.observation_specs):
        # the first dimension is for batch (even if batch is not used)
        if obs_spec.name == 'RayPerceptionSensorFront':
            state.observation.rays.F.hit = not bool(obs_list[index][0, 0])
            state.observation.rays.F.distance = obs_list[index][0, 1]
            state.observation.rays.FR.hit = not bool(obs_list[index][0, 2])
            state.observation.rays.FR.distance = obs_list[index][0, 3]
            state.observation.rays.FL.hit = not bool(obs_list[index][0, 4])
            state.observation.rays.FL.distance = obs_list[index][0, 5]
            state.observation.rays.RF.hit = not bool(obs_list[index][0, 6])
            state.observation.rays.RF.distance = obs_list[index][0, 7]
            state.observation.rays.LF.hit = not bool(obs_list[index][0, 8])
            state.observation.rays.LF.distance = obs_list[index][0, 9]
            state.observation.rays.R.hit = not bool(obs_list[index][0, 10])
            state.observation.rays.R.distance = obs_list[index][0, 11]
            state.observation.rays.L.hit = not bool(obs_list[index][0, 12])
            state.observation.rays.L.distance = obs_list[index][0, 13]
        elif obs_spec.name == 'RayPerceptionSensorBack':
            state.observation.rays.B.hit = not bool(obs_list[index][0, 0])
            state.observation.rays.B.distance = obs_list[index][0, 1]
            state.observation.rays.BL.hit = not bool(obs_list[index][0, 2])
            state.observation.rays.BL.distance = obs_list[index][0, 3]
            state.observation.rays.BR.hit = not bool(obs_list[index][0, 4])
            state.observation.rays.BR.distance = obs_list[index][0, 5]
        elif obs_spec.name == 'CameraSensorFront':
            state.observation.images.front.data = array_to_image(obs_list[index][0, :, :, :])
            state.observation.images.front.height = obs_spec.shape[0]
            state.observation.images.front.width = obs_spec.shape[1]
            state.observation.images.front.channels = obs_spec.shape[2]
        elif obs_spec.name == 'CameraSensorBack':
            state.observation.images.back.data = array_to_image(obs_list[index][0, :, :, :])
            state.observation.images.back.height = obs_spec.shape[0]
            state.observation.images.back.width = obs_spec.shape[1]
            state.observation.images.back.channels = obs_spec.shape[2]
        elif obs_spec.name == 'progress':
            state.observation.progress = obs_list[index][0, 0]
        elif obs_spec.name == 'usedtime':
            state.observation.usedtime = obs_list[index][0, 0]
        elif obs_spec.name == 'velocity':
            state.observation.velocity = obs_list[index][0, 0]
        elif obs_spec.name == 'wheel':
            state.observation.refills.wheel.value = obs_list[index][0, 0]
        elif obs_spec.name == 'gas':
            state.observation.refills.gas.value = obs_list[index][0, 0]
        elif obs_spec.name == 'nitro':
            state.observation.effects.nitro.number = int(obs_list[index][0, 0])
        elif obs_spec.name == 'turtle':
            state.observation.effects.turtle.number = int(obs_list[index][0, 0])
        elif obs_spec.name == 'banana':
            state.observation.effects.banana.number = int(obs_list[index][0, 0])
        # TODO: Add the information from the event fields(like undrivable)
        elif obs_spec.name == 'win':
            if bool(obs_list[index][0, 0]):
                event = Event.EVENT_WIN
        elif obs_spec.name == 'timeout':
            if bool(obs_list[index][0, 0]):
                event = Event.EVENT_TIMEOUT
        elif obs_spec.name == 'undrivable':
            if bool(obs_list[index][0, 0]):
                event = Event.EVENT_UNDRIVABLE
    state.event = event
    state.reward = reward
    return state

def state_info(state: State, img_suffix: str) -> str:
    s = State()
    s.CopyFrom(state)
    if config.LOG_LEVEL <= logging.DEBUG:
        # Save the image to the disk
        if not os.path.exists(config.IMAGE_DIR):
            os.makedirs(config.IMAGE_DIR)
        
        filepath_front = config.IMAGE_DIR + '/img_front_' + str(img_suffix) + '.png'
        filepath_back = config.IMAGE_DIR + '/img_back_' + str(img_suffix) + '.png'

        with open(filepath_front, 'wb') as fout:
            fout.write(s.observation.images.front.data)
        with open(filepath_back, 'wb') as fout:
            fout.write(s.observation.images.back.data)
        
        s.observation.images.front.data = bytes(filepath_front, encoding='utf8')
        s.observation.images.back.data = bytes(filepath_back, encoding='utf8')
    else:
        # Not to save the image to the disk, just leave it in memory
        s.observation.images.front.data = b'PNG image data'
        s.observation.images.back.data = b'PNG image data'
    return str(s)

def init_action_object(id: str=None) -> Action:
    action = Action(
        api_version='PAIAKart_1.0',
        id=id,
        command=Command.COMMAND_START
    )
    return action

def create_action_object(id: str=None, acceleration: bool=False, brake: bool=False, steering: float=0.0, command: Command=Command.COMMAND_GENERAL) -> Action:
    action = Action(
        api_version='PAIAKart_1.0',
        id=id,
        command=command,
        acceleration=acceleration,
        brake=brake,
        steering=steering
    )
    return action

def convert_action_to_data(action: Action) -> ActionTuple:
    acceleration = action.acceleration
    brake = action.brake
    steering = action.steering
    discrete_actions = np.array([[acceleration, brake]], dtype=np.int32)
    continuous_actions = np.array([[steering]], dtype=np.float32)
    return ActionTuple(discrete=discrete_actions, continuous=continuous_actions)

def convert_action_to_object(data: ActionTuple, command: Command, id: str=None) -> Action:
    action = Action(
        api_version='PAIAKart_1.0',
        id=id,
        command=command,
        acceleration=data.discrete[0][0],
        brake=data.discrete[0][1],
        steering=data.continuous[0][0]
    )
    return action

def action_info(action: Action) -> str:
    a = Action()
    a.CopyFrom(action)
    return str(a)