#!/usr/bin/env python

from deployer import __version__
from deployer.contrib.default_config import example_settings
from deployer.run.socket_client import list_sessions
from deployer.run.socket_client import start as start_client
from deployer.run.socket_server import start as start_server
from deployer.run.standalone_shell import start as start_standalone
from deployer.run.telnet_server import start as start_telnet_server

import docopt
import getopt
import getpass
import sys

__doc__ = \
"""Usage:
  client.py start [-s | --single-threaded | --socket SOCKET] [--path PATH] [--non-interactive] [--log LOGFILE]
  client.py listen [--log LOGFILE] [--non-interactive] [--socket SOCKET]
  client.py connect (--socket SOCKET) [--path PATH]
  client.py telnet-server [--port=PORT] [--log LOGFILE] [--non-interactive]
  client.py list-sessions
  client.py -h | --help
  client.py --version

Options:
  -h, --help             : Display this help text.
  -s, --single-threaded  : Single threaded mode.
  --path PATH            : Start the shell at this location.
  --non-interactive      : If possible, run script with as few interactions as
                           possible.  This will always choose the default
                           options when asked for questions.
  --log LOGFILE          : Write logging info to this file. (For debugging.)
  --socket SOCKET        : The path of the unix socket.
  --version              : Show version information.
"""

def start(root_service):
    """
    Client startup point.
    """
    a = docopt.docopt(__doc__, version=__version__)

    interactive = not a['--non-interactive']

    # Socket name variable
    # In case of integers, they map to /tmp/deployer.sock.username.X
    socket_name = a['--socket']

    if socket_name is not None and socket_name.isdigit():
        socket_name = '/tmp/deployer.sock.%s.%s' % (getpass.getuser(), socket_name)

    # List sessions
    if a['list-sessions']:
        list_sessions()

    # Telnet server
    elif a['telnet-server']:
        port = int(a['--port']) if a['--port'] is not None else None
        start_telnet_server(root_service, logfile=a['--log'], port=port)

    # Socket server
    elif a['listen']:
        socket_name = start_server(root_service, daemonized=False, shutdown_on_last_disconnect=False,
                    interactive=interactive, logfile=a['--log'], socket=a['--socket'])

    # Connect to socket
    elif a['connect']:
        start_client(socket_name, a['--path'])

    # Single threaded client
    elif a['--single-threaded']:
        start_standalone(root_service, interactive=interactive, cd_path=a['--path'], logfile=a['--log'])

    # Multithreaded
    else:
        # If no socket has been given. Start a daemonized server in the
        # background, and use that socket instead.
        if not socket_name:
            socket_name = start_server(root_service, daemonized=True, shutdown_on_last_disconnect=True,
                    interactive=interactive, logfile=a['--log'])

        start_client(socket_name, a['--path'])


if __name__ == '__main__':
    start(root_service=example_settings)
