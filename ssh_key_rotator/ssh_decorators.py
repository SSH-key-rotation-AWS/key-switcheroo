"Miscellaneous utilities to be used in conjuction with the SSH service"
import asyncio
import functools
import os
import shutil
from random import randint
from socket import getservbyport
from tempfile import TemporaryDirectory
from paramiko import RSAKey
from ssh_key_rotator.connections import Server, Client
from ssh_key_rotator.util import get_username, get_user_path
from ssh_key_rotator.custom_keygen import (
    generate_private_public_key_in_file,
    PRIVATE_KEY_NAME,
)


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


def with_ssh_server(
    port: int = get_open_port(), ssh_home: str = f"{get_user_path()}/.ssh"
):
    "Runs the decorated function in the context of a fresh SSH server"

    def decorator_server(func):
        @functools.wraps(func)
        async def test_with_server(*args, **kwargs):
            async with Server(port, ssh_home=ssh_home):
                func(*args, **kwargs)

        return test_with_server

    return decorator_server


def with_ssh_server_and_client(port: int = get_open_port()):
    """Runs the decorated function in the context of a fresh SSH server and client.
    Fresh keys are stored in a tempfile"""

    def ssh_server_and_keys_decorator(func):
        @functools.wraps(func)
        async def generate_keys_wrapper_test(*args, **kwargs):
            with TemporaryDirectory(dir=get_user_path()) as ssh_home:
                shutil.chown(ssh_home, get_username(), get_username())
                os.chmod(ssh_home, 0o700)
                _, public_key = generate_private_public_key_in_file(ssh_home)
                log_path = f"{ssh_home}/logs"
                authorized_keys_path = f"{ssh_home}/authorized_keys"
                with open(authorized_keys_path, mode="wb") as authorized_keys_file:
                    authorized_keys_file.write(public_key)
                with open(log_path, mode="wb"):
                    pass
                shutil.chown(authorized_keys_path, get_username(), get_username())
                os.chmod(authorized_keys_path, mode=0o600)
                async with Server(port=port, ssh_home=ssh_home) as server:
                    client = Client("127.0.0.1", port, get_username())
                    client.connect_via_key(key_location=ssh_home)
                    desired_arguments = func.__code__.co_varnames
                    if "client" in desired_arguments:
                        kwargs["client"] = client
                    if "server" in desired_arguments:
                        kwargs["server"] = server
                    if "key" in desired_arguments:
                        private_key_file = f"{ssh_home}/{PRIVATE_KEY_NAME}"
                        kwargs["key"] = RSAKey.from_private_key_file(private_key_file)
                    if asyncio.iscoroutinefunction(func):
                        await func(*args, **kwargs)
                    else:
                        func(*args, **kwargs)

        return generate_keys_wrapper_test

    return ssh_server_and_keys_decorator


# DOES NOT WORK YET, DO NOT USE
# def SSHTestCase(port:int):
#     def class_decorator(cls):
#         methods_in_base_class = {func for func in dir(IsolatedAsyncioTestCase) if callable(func)}
#         this_class = {func for func in dir(cls) if callable(func) and not func.startsWith("__")}
#         test_methods = this_class.difference(methods_in_base_class)
#         @functools.wraps(cls)
#         def class_wrapper(*args, **kwargs):
#             print('At wrapper')
#             for base_class_method in methods_in_base_class:
#                 cls.setattr(cls, base_class_method, base_class_method)
#             for test_method in this_class:
#                 print(test_method)
#                 cls.setattr(cls, test_method, with_ssh_server(port)(test_method))
#             return cls(*args, **kwargs)
#         return class_wrapper
#     return class_decorator
