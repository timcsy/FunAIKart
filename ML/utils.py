import os
from typing import List, Optional

import numpy as np
import PIL

from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.base_env import BehaviorSpec, ActionTuple, ObservationSpec
from mlagents.trainers import demo_loader
from mlagents.trainers.buffer import AgentBuffer, BufferKey, ObservationKeyPrefix

import config
from config import DebugMode


def open_env():
  if config.DEBUG != DebugMode.DISABLE:
    print('Waiting for Unity side ...')
  env = UnityEnvironment(file_name=None)
  env.reset()
  if config.DEBUG != DebugMode.DISABLE:
    print('--------------------------------')

  # Behavior infomation
  if config.DEBUG == DebugMode.DETAIL:
    print('Behaviors:\n')
    print(dict(env.behavior_specs))
    print("--------------------------------")

  # We will only consider the first Behavior
  behavior_name = list(env.behavior_specs)[0]
  if config.DEBUG != DebugMode.DISABLE:
    print('Name of the behavior: ' + str(behavior_name))
    print('--------------------------------')
  return env, behavior_name


def show_observation(obs: np.ndarray, obs_spec: ObservationSpec, step_id):
  # Place to store the images
  if config.DEBUG == DebugMode.DETAIL:
    if not os.path.exists(config.IMAGE_DIR):
      os.makedirs(config.IMAGE_DIR)
  
  # 3-dimensional observation (Image)
  if len(obs_spec.shape) == 3:
    if config.DEBUG == DebugMode.DETAIL:
      # the first dimension is for batch (even if batch is not used)
      image_tensor = obs[0,:,:,2] # [N,H,W,C] = [Batch, Height, Width, Channel(RGB)]
      img = 255 * image_tensor # Scale from [0,1] to [0,255]
      img = PIL.Image.fromarray(img.astype(np.uint8)) # Convert to PIL format
      filepath = config.IMAGE_DIR + '/img_' + ('front' if obs_spec.name == 'CameraSensorFront' else 'back') + '_' + str(step_id) + '.png'
      print('Save image to ' + filepath)
      img.save(filepath)
    elif config.DEBUG == DebugMode.SIMPLE:
      print(('Front' if obs_spec.name == 'CameraSensorFront' else 'Back') + 'Camera View is processed')

  # 1-dimensional observation (Vector)
  if len(obs_spec.shape) == 1:
    if config.DEBUG != DebugMode.DISABLE:
      # the first dimension is for batch (even if batch is not used)
      ray_vector = obs[0,:]
      prefix = 'Front' if obs_spec.name == 'RayPerceptionSensorFront' else 'Back'
      print(prefix + ' Ray Perception: ' + str(ray_vector))

def show_observations(behavior_spec: BehaviorSpec, obs_list: List[np.ndarray], step_id) -> None:
  if config.DEBUG != DebugMode.DISABLE:
    print('Step ID: ' + str(step_id))
  
  for index, obs_spec in enumerate(behavior_spec.observation_specs):
    show_observation(obs_list[index], obs_spec, step_id)


def inferencing(env: UnityEnvironment, behavior_name: str, random: bool = False):
  # Get the Behavior Spec by name
  behavior_spec = env.behavior_specs[behavior_name]

  done = False # Flag to indicate whether the episode has done

  # Initial Step
  step_id = 0
  decision_steps, terminal_steps = env.get_steps(behavior_name)

  while not done:
    for agent_id in decision_steps:
      # Show the step information
      show_observations(behavior_spec, decision_steps.obs, step_id)

      # Generate an action for all agents randomly
      if random:
        action = behavior_spec.action_spec.random_action(len(decision_steps))

      # Generate an action for all agents that only move forward
      if not random:
        discrete_actions = np.array([[1,0]], dtype=np.int32)
        continuous_actions = np.array([[0.0]], dtype=np.float32)
        action = ActionTuple(discrete=discrete_actions, continuous=continuous_actions)
      
      # Set the actions
      env.set_action_for_agent(behavior_name, agent_id, action)

      # TODO: Show the reward

      # Move the simulation forward
      env.step()
      step_id += 1 # Actually, it should be increased by Decision Period, but for convenience, we just add one
      # Get the new simulation results
      decision_steps, terminal_steps = env.get_steps(behavior_name)
    
    for agent_id in terminal_steps:
      done = True
      # Show the step information
      show_observations(behavior_spec, terminal_steps.obs, step_id)
      if config.DEBUG != DebugMode.DISABLE:
        print()
        print('Done, Behavior: ' + str(behavior_name) + ', Agent: ' + str(agent_id) + ', Total Steps: ' + str(step_id))
    
    if config.DEBUG != DebugMode.DISABLE:
        print()
    
  env.close()


def get_observations_from_buffer(buffer: AgentBuffer, behavior_spec: BehaviorSpec, index: int) -> List[np.ndarray]:
  obs_list: List[np.ndarray] = []
  for i, _ in enumerate(behavior_spec.observation_specs):
    obs_single = buffer[(ObservationKeyPrefix.OBSERVATION, i)][index]
    # We need to add a dimention at the front (for batch size preserved, even if not using batch)
    # https://numpy.org/doc/stable/reference/generated/numpy.expand_dims.html
    obs_expand = np.expand_dims(obs_single, axis=0)
    obs_list.append(obs_expand)
  return obs_list

def get_discrete_action_from_buffer(buffer: AgentBuffer, index: int) -> np.ndarray:
  action_single = buffer[BufferKey.DISCRETE_ACTION][index]
  # We need to add a dimention at the front (for agent number)
  # https://numpy.org/doc/stable/reference/generated/numpy.expand_dims.html
  return np.expand_dims(action_single, axis=0)

def get_continuous_action_from_buffer(buffer: AgentBuffer, index: int) -> np.ndarray:
  action_single = buffer[BufferKey.CONTINUOUS_ACTION][index]
  # We need to add a dimention at the front (for agent number)
  # https://numpy.org/doc/stable/reference/generated/numpy.expand_dims.html
  return np.expand_dims(action_single, axis=0)

def load_from_demo(filename: Optional[str] = None) -> None:
  # A demo file is just for an agent, that means it will have only one behavior
  if filename == None:
    filename = config.DEMO_FILE
  filepath = config.DEMO_DIR + '/' + filename
  behavior_spec, buffer = demo_loader.demo_to_buffer(filepath, sequence_length=None)

  # We take one episode first

  for step_id in range(buffer.num_experiences):
    # Show the step information
    obs_list = get_observations_from_buffer(buffer, behavior_spec, step_id)
    show_observations(behavior_spec, obs_list, step_id)
    
    # Show discrete actions
    discrete_action = get_discrete_action_from_buffer(buffer, step_id)
    print('Discrete Actions: ' + str(discrete_action[0,:]))
    # Show continuous actions
    continuous_action = get_continuous_action_from_buffer(buffer, step_id)
    print('Continuous Actions: ' + str(continuous_action[0,:]))


    # TODO: Show the reward
    
    # To check whether it is done or finished
    if buffer[BufferKey.DONE] == True:
      if config.DEBUG != DebugMode.DISABLE:
        print()
        print('Done, Demo: ' + str(filename) + ', Total Steps: ' + str(step_id))
      break
    if step_id == buffer.num_experiences - 1:
      if config.DEBUG != DebugMode.DISABLE:
        print()
        print('Finish, Demo: ' + str(filename) + ', Total Steps: ' + str(step_id))
      break

    if config.DEBUG != DebugMode.DISABLE:
      print()