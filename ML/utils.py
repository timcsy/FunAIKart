from typing import List
from mlagents_envs.base_env import BehaviorSpec
import matplotlib.pyplot as plt
import os

from numpy import ndarray
import config

def show_observations(behavior_spec: BehaviorSpec, obs: List[ndarray], image_dir: str, id) -> str:
  # Place to store the images
  if not os.path.exists(image_dir):
    os.makedirs(image_dir)

  output_str = 'Step ID: ' + str(id) + '\n'
  
  for index, obs_spec in enumerate(behavior_spec.observation_specs):
    # 3-dimensional observation (Image)
    if len(obs_spec.shape) == 3:
      plt.imshow(obs[index][0,:,:,:])
      filepath = image_dir + '/img_' + ('front' if obs_spec.name == 'CameraSensorFront' else 'back') + '_' + str(id) + '.png'
      output_str += 'Save image to ' + filepath + '\n'
      plt.savefig(filepath)

  for index, obs_spec in enumerate(behavior_spec.observation_specs):
    # 1-dimensional observation (Vector)
    if len(obs_spec.shape) == 1:
      if (obs_spec.name == 'RayPerceptionSensorFront'):
        output_str += 'Front Ray Perception: ' + str(obs[index][0,:]) + '\n'
      if (obs_spec.name == 'RayPerceptionSensorBack'):
        output_str += 'Back Ray Perception: ' + str(obs[index][0,:]) + '\n'
  
  return output_str

def print_observations(behavior_spec: BehaviorSpec, obs: List[ndarray], image_dir: str, id) -> None:
  if config.DEBUG == True:
    print(show_observations(behavior_spec, obs, image_dir, id))
  else:
    show_observations(behavior_spec, obs, image_dir, id)