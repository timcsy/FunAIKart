import ast
import logging
import os

from dotenv import load_dotenv

def recursive_load(path='.env', required_envs=[]):
    os.environ.pop('REQUIRE', None)
    path = os.path.abspath(path)
    load_dotenv(path)
    if 'REQUIRE' not in os.environ:
        return
    try:
        include_paths = ast.literal_eval(os.environ['REQUIRE'])
    except:
        include_paths = os.environ['REQUIRE']
    if isinstance(include_paths, str):
        if os.path.abspath(include_paths) not in required_envs:
            recursive_load(include_paths, required_envs + [path])
    for include_path in include_paths:
        if os.path.abspath(include_path) not in required_envs:
            recursive_load(include_path, required_envs + [path])

recursive_load()
ENV = os.environ # You can get and set the environment variable by ENV['VAR_NAME']
'''
Remember to import in every possible files:
from config import ENV

Just as common Dict:
You have to check if the key exists first: if 'KEY' in ENV
Access empty key will cause KeyError,
Or you can use ENV.get()
Or ENV.setdefault(key[,default]), this will set the value also
You can only insert the string value

You can use REQUIRE key to include .env files (in string or list format)
'''


# Logging Level
if ENV.get('LOG_LEVEL') == 'CRITICAL': log_level = logging.CRITICAL
elif ENV.get('LOG_LEVEL') == 'ERROR': log_level = logging.ERROR
elif ENV.get('LOG_LEVEL') == 'WARNING': log_level = logging.WARNING
elif ENV.get('LOG_LEVEL') == 'DEBUG': log_level = logging.DEBUG
elif ENV.get('LOG_LEVEL') == 'NOTEST': log_level = logging.NOTEST
else: log_level = logging.INFO
logging.basicConfig(level=log_level, format='%(message)s')