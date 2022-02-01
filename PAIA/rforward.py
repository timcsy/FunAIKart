from getpass import getpass
import os
import socket
import select
import sys
import threading

import paramiko


def handler(chan, host, port):
    sock = socket.socket()
    try:
        sock.connect((host, port))
    except Exception as e:
        print("Forwarding request to %s:%d failed: %r" % (host, port, e))
        return

    print(
        "Connected!  Tunnel open %r -> %r -> %r"
        % (chan.origin_addr, chan.getpeername(), (host, port))
    )
    while True:
        r, w, x = select.select([sock, chan], [], [])
        if sock in r:
            data = sock.recv(1024)
            if len(data) == 0:
                break
            chan.send(data)
        if chan in r:
            data = chan.recv(1024)
            if len(data) == 0:
                break
            sock.send(data)
    chan.close()
    sock.close()


def reverse_forward_tunnel(server_port, remote_host, remote_port, transport):
    transport.request_port_forward("", server_port)
    while True:
        chan = transport.accept(1000)
        if chan is None:
            continue
        thr = threading.Thread(
            target=handler, args=(chan, remote_host, remote_port)
        )
        thr.setDaemon(True)
        thr.start()


def rforward(remote_bind_port, forward_host, forward_port, ssh_host, ssh_port, ssh_user, ssh_pass):
    """
    ssh -R 4000:internal.example.com:80 public.example.com
    """
    # remote_bind_port: port on server to forward
    # forward_host: dest host to forward to
    # forward_port: dest port to forward to

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.WarningPolicy())

    try:
        client.connect(
            ssh_host,
            ssh_port,
            username=ssh_user,
            password=ssh_pass,
        )
    except Exception as e:
        print("*** Failed to connect to %s:%d: %r" % (ssh_host, ssh_port, e))
        sys.exit(1)

    print(
        "Now forwarding remote port %d to %s:%d ..."
        % (remote_bind_port, forward_host, forward_port)
    )

    try:
        reverse_forward_tunnel(
            remote_bind_port, forward_host, forward_port, client.get_transport()
        )
    except KeyboardInterrupt:
        print("C-c: Port forwarding stopped.")
        sys.exit(0)

def team_config():
    print('If you are using the environment variable, then just press ENTER in the following field!')
    print('You can set the environment variable by SET (Windows) or export (Other OS).')
    print('More information please check the README.')
    
    team_port = int(input('ID Number of your team (e.g. 50051): ') or os.getenv('PAIA_ID'))
    remote_bind_port = team_port
    forward_host='localhost'
    forward_port = team_port
    ssh_host = input('SSH IP of your team (e.g. 140.114.79.187): ') or os.getenv('PAIA_HOST')
    ssh_port = int(input('SSH port of your team (e.g. 9487): ') or os.getenv('PAIA_PORT'))
    ssh_user = input('SSH username: ') or os.getenv('PAIA_USERNAME')
    ssh_pass = getpass('SSH password: ') or os.getenv('PAIA_PASSWORD')
    return (remote_bind_port, forward_host, forward_port, ssh_host, ssh_port, ssh_user, ssh_pass)

if __name__ == "__main__":
    args = team_config()
    rforward(*args)


''' Environment variables example

Windows:

SET PAIA_ID=<your team ID> PAIA_HOST=<your ssh host IP> PAIA_PORT=<your ssh port> PAIA_USERNAME=<your ssh username> PAIA_PASSWORD=<your ssh password>

Unix-like:

export \
PAIA_ID=<your team ID> \
PAIA_HOST=<your ssh host IP> \
PAIA_PORT=<your ssh port> \
PAIA_USERNAME=<your ssh username> \
PAIA_PASSWORD=<your ssh password>
'''