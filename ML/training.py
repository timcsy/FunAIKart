from mlagents_envs.environment import UnityEnvironment

# This code is used to close an env that might not have been closed before
try:
  env.close()
except:
  pass

env = UnityEnvironment(file_name=None)

env.reset()

# We will only consider the first Behavior
behavior_name = list(env.behavior_specs)[0]
print(f"Name of the behavior : {behavior_name}")
spec = env.behavior_specs[behavior_name]