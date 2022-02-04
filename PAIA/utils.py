from getpass import getpass

from config import ENV

def team_config():
    print('If you are using the environment variable, then just press ENTER in the following field!')
    print('You can set the environment variable in .env file or by SET (Windows) or export (Other OS).')
    print('More information please check the README.')
    
    team_port = int(input('ID Number of your team (e.g. 50051): ') or ENV.get('PAIA_ID') or 50051)
    ENV['PAIA_ID'] = str(team_port)
    return team_port

def server_config():
    team_port = team_config()
    remote_bind_port = team_port
    forward_host='localhost'
    forward_port = team_port
    ssh_host = input('SSH IP of your team (e.g. 140.114.79.187): ') or ENV.get('PAIA_HOST')
    ssh_port = int(input('SSH port of your team (e.g. 9487): ') or ENV.get('PAIA_PORT') or 22)
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