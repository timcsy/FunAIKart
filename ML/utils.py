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

def get_img(behavior_spec: BehaviorSpec, obs_list: List[np.ndarray]):
  for index, obs_spec in enumerate(behavior_spec.observation_specs):
    obs = obs_list[index]
    # 3-dimensional observation (Image)
    if len(obs_spec.shape) == 3:
      if config.DEBUG == DebugMode.DETAIL:
        # the first dimension is for batch (even if batch is not used)
        image_tensor = obs[0,:,:,:] # [N,H,W,C] = [Batch, Height, Width, Channel(RGB)]
        img = 255 * image_tensor # Scale from [0,1] to [0,255]
        img = PIL.Image.fromarray(img.astype(np.uint8)) # Convert to PIL format
        return img
  pass

def show_observation(obs: np.ndarray, obs_spec: ObservationSpec, img_id) -> None:
  # Place to store the images
  if config.DEBUG == DebugMode.DETAIL:
    if not os.path.exists(config.IMAGE_DIR):
      os.makedirs(config.IMAGE_DIR)
  
  # 3-dimensional observation (Image)
  if len(obs_spec.shape) == 3:
    if config.DEBUG == DebugMode.DETAIL:
      # the first dimension is for batch (even if batch is not used)
      image_tensor = obs[0,:,:,:] # [N,H,W,C] = [Batch, Height, Width, Channel(RGB)]
      img = 255 * image_tensor # Scale from [0,1] to [0,255]
      img = PIL.Image.fromarray(img.astype(np.uint8)) # Convert to PIL format
      filepath = config.IMAGE_DIR + '/img_' + ('front' if obs_spec.name == 'CameraSensorFront' else 'back') + '_' + str(img_id) + '.png'
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

def show_observations(behavior_spec: BehaviorSpec, obs_list: List[np.ndarray], img_id) -> None:
  for index, obs_spec in enumerate(behavior_spec.observation_specs):
    show_observation(obs_list[index], obs_spec, img_id)

def front_ray_vector_to_reward(ray_vector) -> float:
  reward = 0
  for i in range(0, 7):
    if ray_vector[2 * i + 0] != 1: 
      dist = ray_vector[2 * i + 1]
      reward += dist
      # if dist < 0.025:
      #   reward -= 100 # big penalty when too close to wall
      # else: reward += dist
  return reward
def back_ray_vector_to_reward(ray_vector) -> float:
  reward = 0
  for i in range(0, 3):
    if ray_vector[2 * i + 0] != 1: 
      dist = ray_vector[2 * i + 1]
      reward += dist
      # if dist < 0.025:
      #   reward -= 100 # big penalty when too close to wall
      # else: reward += dist
  return reward

def observation_to_reward(obs: np.ndarray, obs_spec: ObservationSpec) -> float:
  # Place to store the images
  #if config.DEBUG == DebugMode.DETAIL:
  #  if not os.path.exists(config.IMAGE_DIR):
  #    os.makedirs(config.IMAGE_DIR)
  
  # 3-dimensional observation (Image)
  if len(obs_spec.shape) == 3:
    #if config.DEBUG == DebugMode.DETAIL:
    # the first dimension is for batch (even if batch is not used)
    #image_tensor = obs[0,:,:,:] # [N,H,W,C] = [Batch, Height, Width, Channel(RGB)]
    #img = 255 * image_tensor # Scale from [0,1] to [0,255]
    #img = PIL.Image.fromarray(img.astype(np.uint8)) # Convert to PIL format
    #filepath = config.IMAGE_DIR + '/img_' + ('front' if obs_spec.name == 'CameraSensorFront' else 'back') + '_' + str(img_id) + '.png'
    #print('Save image to ' + filepath)
    #img.save(filepath)
    pass
  # 1-dimensional observation (Vector)
  reward = 0
  if len(obs_spec.shape) == 1:
    #if config.DEBUG != DebugMode.DISABLE:
    # the first dimension is for batch (even if batch is not used)
    ray_vector = obs[0,:]
    prefix = 'Front' if obs_spec.name == 'RayPerceptionSensorFront' else 'Back'
    #print(prefix + ' Ray Perception: ' + str(ray_vector))
    if prefix == 'Front':
      reward += front_ray_vector_to_reward(ray_vector)
    else:
      reward += back_ray_vector_to_reward(ray_vector)
  return reward

def observations_to_rewards(behavior_spec:BehaviorSpec, obs_list:List[np.ndarray]) -> float:
  reward = 0
  for index, obs_spec in enumerate(behavior_spec.observation_specs):
    reward += observation_to_reward(obs_list[index], obs_spec)
  return reward

def show_actions(actions: ActionTuple) -> None:
  if config.DEBUG != DebugMode.DISABLE:
    print('Discrete Actions: ' + str(actions.discrete[0,:]))
    print('Continuous Actions: ' + str(actions.continuous[0,:]))

def open_env() -> None:
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

def online(env: UnityEnvironment, behavior_name: str, random: bool = False) -> None:
  # Get the Behavior Spec by name
  behavior_spec = env.behavior_specs[behavior_name]

  # The following code only concern one agent

  total_steps = 0 # Total number of steps for all episodes
  max_steps_per_episode = 10000
  img_size = (112, 252)

  for episode in range(1, config.MAX_EPISODES + 1):
    done = False # Flag to indicate whether the episode has done
    step_num = 0  # The number of steps in an episode
    while not done:

      # Actually, it should be increased by Decision Period, but for convenience, we just add one
      total_steps += 1
      step_num += 1
      # Get the new simulation results
      decision_steps, terminal_steps = env.get_steps(behavior_name)
      reward = 0
      # Show the step information
      if config.DEBUG != DebugMode.DISABLE:
        print('Episode: ' + str(episode) + ', Step: ' + str(step_num))
      # state = get_img(behavior_spec, decision_steps.obs)
      for agent_id in decision_steps:
        # Show observations
        show_observations(behavior_spec, decision_steps.obs, str(episode) + '_' + str(step_num))
        reward += observations_to_rewards(behavior_spec, decision_steps.obs)
        # Generate an action for all agents randomly
        #if random:
          #actions = behavior_spec.action_spec.random_action(len(decision_steps))
        # Generate an action for all agents that only move forward
        #if not random:
          #discrete_actions = np.array([[1,0]], dtype=np.int32)
        continuous_actions = np.array([[0.0]], dtype=np.float32)
          #actions = ActionTuple(discrete=discrete_actions, continuous=continuous_actions)
        # TODO: Send image (state) to DQN, and get continuous actions (turning) back.
        discrete_actions = np.array([[1,0]], dtype=np.int32)
        #continuous_actions = agent.choose_action(state, 0)
        actions = ActionTuple(discrete=discrete_actions, continuous=continuous_actions)
        # actions = ...
  
        # Set actions
        env.set_action_for_agent(behavior_name, agent_id, actions)
        # Show actions
        show_actions(actions)

        # TODO: Show the reward
      print(f"Reward: {reward}")
      # if reward < 0: # Early termination on negative reward
      #   done = True
      
      for agent_id in terminal_steps:
        done = True
        # Show observations
        show_observations(behavior_spec, terminal_steps.obs, str(episode) + '_' + str(step_num))

        # TODO: Show the reward

        # Show the summary
        if config.DEBUG != DebugMode.DISABLE:
          print()
          print('Done, Behavior: ' + str(behavior_name) + ', Agent: ' + str(agent_id) + ', Episode: ' + str(episode) + ', Total Steps: ' + str(step_num))
        
        step_num = 0
      if max_steps_per_episode <= step_num:
        done = True

      if config.DEBUG != DebugMode.DISABLE:
        print()
      
      # Move the simulation forward
      env.step()
    # env.reset()
    print('Finish, Behavior: ' + str(behavior_name) + ', Agent: ' + str(agent_id) + ', Episodes: ' + str(episode) + ', Total Steps: ' + str(total_steps))

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

def get_actions_from_buffer(buffer: AgentBuffer, index: int) -> ActionTuple:
  # We need to add a dimention at the front (for agent number)
  # https://numpy.org/doc/stable/reference/generated/numpy.expand_dims.html
  discrete_actions_single = buffer[BufferKey.DISCRETE_ACTION][index]
  discrete_actions = np.expand_dims(discrete_actions_single, axis=0)
  continuous_actions_single = buffer[BufferKey.CONTINUOUS_ACTION][index]
  continuous_actions = np.expand_dims(continuous_actions_single, axis=0)
  return ActionTuple(discrete=discrete_actions, continuous=continuous_actions)


def load_from_demo(filename: Optional[str] = None) -> None:
  # A demo file is just for an agent, that means it will have only one behavior
  if filename == None:
    filename = config.DEMO_FILE
  filepath = config.DEMO_DIR + '/' + filename
  behavior_spec, buffer = demo_loader.demo_to_buffer(filepath, sequence_length=None)

  episode = 1
  step_num = 0 # The number of steps in an episode

  for index in range(buffer.num_experiences):
    step_num += 1

    # Show the step information
    if config.DEBUG != DebugMode.DISABLE:
      print('Episode: ' + str(episode) + ', Step: ' + str(step_num))
    
    # Show observations
    obs_list = get_observations_from_buffer(buffer, behavior_spec, index)
    show_observations(behavior_spec, obs_list, str(episode) + '_' + str(step_num))
    
    # Show actions
    actions = get_actions_from_buffer(buffer, index)
    show_actions(actions)

    # TODO: Show the reward

    
    # To check whether episode is done, and show the summary
    if buffer[BufferKey.DONE][index]:
      if config.DEBUG != DebugMode.DISABLE:
        print()
        print('Done, Demo: ' + str(filename) + ', Episode: ' + str(episode) + ', Total Steps: ' + str(step_num))
      episode += 1
      step_num = 0
    
    # To check whether demo is finished, and show the summary
    if index == buffer.num_experiences - 1:
      if config.DEBUG != DebugMode.DISABLE:
        print()
        print('Finish, Demo: ' + str(filename) + ', Episodes: ' + str(episode) + ', Total Steps: ' + str(index))
      

    if config.DEBUG != DebugMode.DISABLE:
      print()


def heuristic(env: UnityEnvironment, behavior_name: str, filename: Optional[str] = None) -> None:
  # A demo file is just for an agent, that means it will have only one behavior
  if filename == None:
    filename = config.DEMO_FILE
  filepath = config.DEMO_DIR + '/' + filename
  _, buffer = demo_loader.demo_to_buffer(filepath, sequence_length=None)

  # Get the Behavior Spec by name
  behavior_spec = env.behavior_specs[behavior_name]

  # The following code only concern one agent

  done = False
  total_steps = 0 # Total number of steps for all episodes

  while not done:
    # Actually, it should be increased by Decision Period, but for convenience, we just add one
    total_steps += 1
    # Get the new simulation results
    decision_steps, terminal_steps = env.get_steps(behavior_name)

    # Show the step information
    if config.DEBUG != DebugMode.DISABLE:
      print('Step: ' + str(total_steps))
    
    for agent_id in decision_steps:
      # Show observations
      show_observations(behavior_spec, decision_steps.obs, str(total_steps))

      # Generate an action from demo
      actions = get_actions_from_buffer(buffer, total_steps)
      
      # Set actions
      env.set_action_for_agent(behavior_name, agent_id, actions)
      # Show actions
      show_actions(actions)

      # TODO: Show the reward

    
    for agent_id in terminal_steps:
      done = True
      # Show observations
      show_observations(behavior_spec, terminal_steps.obs, str(total_steps))

      # TODO: Show the reward

      # Show the summary
      
    if config.DEBUG != DebugMode.DISABLE:
      print()
      print('Finish, Behavior: ' + str(behavior_name) + ', Agent: ' + str(agent_id) + ', Total Steps: ' + str(total_steps))
    
    # Move the simulation forward
    env.step()
    
  env.close()