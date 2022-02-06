from datetime import datetime
from getpass import getpass
import os

from config import ENV, bool_ENV

def get_dir_fileprefix(name, base_dir=None, use_dir=None, dir_prefix=None, dir_timestamp=None, file_prefix=None, file_timestamp=None, base_dir_default='.', use_dir_default=True):
    if base_dir is None:
        base_dir = ENV.get(name + '_BASE_DIR', base_dir_default)
    if use_dir is None:
        use_dir = bool_ENV(name + '_USE_DIR', use_dir_default)
    if dir_prefix is None:
        dir_prefix = ENV.get(name + '_DIR_PREFIX', '')
    if dir_timestamp is None:
        dir_timestamp = bool_ENV(name + '_DIR_TIMESTAMP')
        if dir_timestamp is None:
            dir_timestamp = ENV.get(name + '_DIR_TIMESTAMP')
        elif dir_timestamp is True:
            dir_timestamp = '%Y%m%d%H%M%S'
    if file_prefix is None:
        file_prefix = ENV.get(name + '_FILE_PREFIX', '')
    if file_timestamp is None:
        file_timestamp = bool_ENV(name + '_FILE_TIMESTAMP')
        if file_timestamp is None:
            file_timestamp = ENV.get(name + '_FILE_TIMESTAMP')
        elif file_timestamp is True:
            file_timestamp = '%Y%m%d%H%M%S'

    dirpath = base_dir
    if use_dir:
        if dir_timestamp:
            if dir_prefix:
                dirpath = os.path.join(dirpath, dir_prefix + '_' + datetime.now().strftime(dir_timestamp))
            else:
                dirpath = os.path.join(dirpath, datetime.now().strftime(dir_timestamp))
        else:
            dirpath = os.path.join(dirpath, dir_prefix)
    
    fileprefix = ''
    if file_timestamp:
        if file_prefix:
            fileprefix = file_prefix + '_' + datetime.now().strftime(file_timestamp)
        else:
            fileprefix = datetime.now().strftime(file_timestamp)
    else:
        fileprefix = file_prefix

    return dirpath, fileprefix

def team_config():
    print('If you are using the environment variable, then just press ENTER in the following field!')
    print('You can set the environment variable in .env file or by SET (Windows) or export (Other OS).')
    print('More information please check the README.')
    
    team_port = int(input('ID Number of your team (e.g. 50051): ') or ENV.get('PAIA_ID', 50051))
    ENV['PAIA_ID'] = str(team_port)
    return team_port

def server_config():
    team_port = team_config()
    remote_bind_port = team_port
    forward_host='localhost'
    forward_port = team_port
    ssh_host = input('SSH IP of your team (e.g. 140.114.79.187): ') or ENV.get('PAIA_HOST')
    ssh_port = int(input('SSH port of your team (e.g. 9487): ') or ENV.get('PAIA_PORT', 22))
    ssh_user = input('SSH username: ') or ENV.get('PAIA_USERNAME')
    ssh_pass = getpass('SSH password: ') or ENV.get('PAIA_PASSWORD')
    return [remote_bind_port, forward_host, forward_port, ssh_host, ssh_port, ssh_user, ssh_pass]


''' Environment variables example, or you can set environment variables in the .env file

Windows:

SET PAIA_ID=<your team ID>
SET PAIA_HOST=<your ssh host IP>
SET PAIA_PORT=<your ssh port>
SET PAIA_USERNAME=<your ssh username>
SET PAIA_PASSWORD=<your ssh password>

Unix-like:

export PAIA_ID=<your team ID>
export PAIA_HOST=<your ssh host IP>
export PAIA_PORT=<your ssh port>
export PAIA_USERNAME=<your ssh username>
export PAIA_PASSWORD=<your ssh password>
'''