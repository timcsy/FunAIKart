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

ENV[key] = value can set the value

You can use REQUIRE key to include .env files (in string or list format)
'''

def to_bool(value, default=None):
    if isinstance(value, str):
        if value == '0': return False
        elif value.upper() == 'FALSE': return False
        elif value == '1': return True
        elif value.upper() == 'TRUE': return True
    return default

def bool_ENV(key, default: bool=None):
    return to_bool(ENV.get(key), default)

def to_int(value, default: int=None):
    if default is None:
        return None
    else:
        try:
            return int(value or 0)
        except ValueError:
            return None

def int_ENV(key, default: int=None):
    return to_int(ENV.get(key), default)

def to_float(value, default: int=None):
    if default is None:
        return None
    else:
        try:
            return float(value or 0.0)
        except ValueError:
            return None

def float_ENV(key, default: float=None):
    return to_float(ENV.get(key), default)

# Logging Level
if ENV.get('LOG_LEVEL') == 'CRITICAL': log_level = logging.CRITICAL
elif ENV.get('LOG_LEVEL') == 'ERROR': log_level = logging.ERROR
elif ENV.get('LOG_LEVEL') == 'WARNING': log_level = logging.WARNING
elif ENV.get('LOG_LEVEL') == 'DEBUG': log_level = logging.DEBUG
elif ENV.get('LOG_LEVEL') == 'NOTEST': log_level = logging.NOTEST
else: log_level = logging.INFO
logging.basicConfig(level=log_level, format='%(message)s')