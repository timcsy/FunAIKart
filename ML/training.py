from mlagents_envs.base_env import ActionTuple
from mlagents_envs.environment import UnityEnvironment
import numpy as np
import utils
import config

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

done = False

# Initial Step
step = 0
decision_steps, terminal_steps = env.get_steps(behavior_name)

while not done:
  for agent_id in decision_steps:
    # Show the step information
    utils.print_observations(spec, decision_steps.obs, config.image_dir, step)

    # Generate an action for all agents randomly
    # action = spec.action_spec.random_action(len(decision_steps))

    # Generate an action for all agents that only move forward
    continuous_actions = np.array([[0.0]], dtype=np.float32)
    discrete_actions = np.array([[1,0]], dtype=np.int32)
    action = ActionTuple(continuous=continuous_actions, discrete=discrete_actions)
    
    # Set the actions
    env.set_action_for_agent(behavior_name, agent_id, action)

    # Move the simulation forward
    env.step()
    step += 1 # Actually, it should be increased by Decision Period, but for convenience, we just add one
    # Get the new simulation results
    decision_steps, terminal_steps = env.get_steps(behavior_name)
  
  for agent_id in terminal_steps:
    done = True
    # Show the step information
    utils.print_observations(spec, terminal_steps.obs, config.image_dir, step)
    print()
    print('Done, Behavior: ' + str(behavior_name) + ', Agent: ' + str(agent_id) + ', Total Steps: ' + str(step))
    print()
print('--------------------------------')