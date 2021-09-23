from mlagents_envs.base_env import ActionTuple
from mlagents_envs.environment import UnityEnvironment
import numpy as np
import utils

# Place to store the images
image_dir = 'cameras'

# This code is used to close an env that might not have been closed before
try:
  env.close()
except:
  pass

print('Waiting for Unity side ...')
env = UnityEnvironment(file_name=None)
env.reset()
print('--------------------------------')

# Behavior infomation
print('Behaviors:\n')
print(dict(env.behavior_specs))
print("--------------------------------")

# We will only consider the first Behavior
behavior_name = list(env.behavior_specs)[0]
print(f'Name of the behavior : {behavior_name}')
spec = env.behavior_specs[behavior_name]
print('--------------------------------')

# Get infomation
print('Infomation:\n')
decision_steps, terminal_steps = env.get_steps(behavior_name)
# Show the step information
utils.print_observations(spec, decision_steps, image_dir, 0)

for step in range(1, 50):
  # Generate an action for all agents randomly
  # action = spec.action_spec.random_action(len(decision_steps))

  # Generate an action for all agents that only move forward
  continuous_actions = np.array([[0.0]], dtype=np.float32)
  discrete_actions = np.array([[1,0]], dtype=np.int32)
  action = ActionTuple(continuous=continuous_actions, discrete=discrete_actions)
  
  # Set the actions
  env.set_actions(behavior_name, action)

  # Move the simulation forward
  env.step()

  # Get the new simulation results
  decision_steps, terminal_steps = env.get_steps(behavior_name)
  # Show the step information
  utils.print_observations(spec, decision_steps, image_dir, step)
print('--------------------------------')