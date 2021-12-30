# api_version: PAIAKart_1.0
from communication.generated import PAIA_pb2

import numpy as np

from typing import List
from mlagents_envs.base_env import BehaviorSpec, ActionTuple

State = PAIA_pb2.State
StateType = PAIA_pb2.StateType
Action = PAIA_pb2.Action
EventType = PAIA_pb2.EventType

def convert_state_to_object(behavior_spec: BehaviorSpec, obs_list: List[np.ndarray], event: EventType, reward: float=0.0) -> State:
    state = State(api_version='PAIAKart_1.0')
    for index, obs_spec in enumerate(behavior_spec.observation_specs):
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
            state.observation.images.front.data = np.ndarray.tobytes(obs_list[index][0, :, :, :])
            state.observation.images.front.height = obs_spec.shape[0]
            state.observation.images.front.width = obs_spec.shape[1]
            state.observation.images.front.channels = obs_spec.shape[2]
        elif obs_spec.name == 'CameraSensorBack':
            state.observation.images.back.data = np.ndarray.tobytes(obs_list[index][0, :, :, :])
            state.observation.images.back.height = obs_spec.shape[0]
            state.observation.images.back.width = obs_spec.shape[1]
            state.observation.images.back.channels = obs_spec.shape[2]
        elif obs_spec.name == 'progress':
            state.observation.progress = obs_list[index][0, 0]
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
    state.event = event
    state.reward = reward
    return state

def state_info(state: State) -> str:
    # TODO: Save image and show file path if config.LOG > 1
    state.observation.images.front.data = b'image buffer'
    state.observation.images.back.data = b'image buffer'
    return str(state)

def init_action_object(id: str=None) -> Action:
    action = Action(
        api_version='PAIAKart_1.0',
        id=id,
        state=StateType.STATE_START
    )
    return action

def create_action_object(id: str=None, acceleration: bool=False, brake: bool=False, steering: float=0.0, state: StateType=StateType.STATE_NONE) -> Action:
    action = Action(
        api_version='PAIAKart_1.0',
        id=id,
        state=state,
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

def convert_action_to_object(data: ActionTuple, state: StateType, id: str=None) -> Action:
    action = Action(
        api_version='PAIAKart_1.0',
        id=id,
        state=state,
        acceleration=data.discrete[0][0],
        brake=data.discrete[0][1],
        steering=data.continuous[0][0]
    )
    return action

def action_info(action: Action) -> str:
    return str(action)

def hook(action: Action) -> State:
    # TODO: np.ndarray.tobytes(obs_list[index][0, :, :, :])
    # TODO: to PNG
    pass

def decision(state: State) -> Action:
    # Implement Your Algorithm
    action = create_action_object(id=state.id, acceleration=False, brake=False, steering=0.0)
    return action