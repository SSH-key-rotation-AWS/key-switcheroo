'''Utility functions'''
import os
from psutil import Process

def get_user_path()->str:
    "Returns the user"
    return os.path.expanduser('~')

def get_username()->str:
    "Returns the username on linux system (assuming running from somewhere inside the user path)"
    user_path = get_user_path()
    user_path_components = user_path.split("/")
    return user_path_components[len(user_path_components)-1]

def get_process_running_with_pid(pid: int)->str:
    process = Process(pid)
    return process.name()