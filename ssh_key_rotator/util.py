"""Utility functions"""
import os
from socket import getservbyport
from random import randint
from psutil import Process


def get_open_port() -> int:
    "Returns a random open port, starting at 1024"
    start_port = 1024
    all_primary_ports = list(range(start_port, start_port + 100))
    last_selectable_port = all_primary_ports[len(all_primary_ports) - 1]

    def select_new_port() -> int:
        nonlocal all_primary_ports
        if len(all_primary_ports) == 0:  # Out of ports
            nonlocal last_selectable_port
            # Create a new port range to choose from
            all_primary_ports = list(
                range(last_selectable_port + 1, last_selectable_port + 1001)
            )
            last_selectable_port += 100
        # Choose a new port
        new_port_index = randint(0, len(all_primary_ports) - 1)
        # Remove it from our options, so we dont choose it again
        del all_primary_ports[new_port_index]
        return all_primary_ports[new_port_index]

    # Select a new port until we find an open one
    while True:
        selected_port = select_new_port()
        try:
            getservbyport(selected_port)
        except OSError:
            return selected_port


def get_default_authorized_keys_path() -> str:
    "Returns the default authorized keys path - ~/.ssh/authorized_keys"
    return f"{get_username()}/.ssh/authorized_keys"


def get_user_path() -> str:
    "Returns the user"
    return os.path.expanduser("~")


def get_username() -> str:
    "Returns the username on linux system (assuming running from somewhere inside the user path)"
    user_path = get_user_path()
    user_path_components = user_path.split("/")
    return user_path_components[len(user_path_components) - 1]


def get_process_running_with_pid(pid: int) -> str:
    "Returns the name of the process running with the given process id"
    process = Process(pid)
    return process.name()
