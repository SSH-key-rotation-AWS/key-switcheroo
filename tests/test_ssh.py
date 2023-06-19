"Testing SSH connection using ssh_key_rotator.connections Client & Server"
import unittest
from unittest import IsolatedAsyncioTestCase
import os
from hamcrest import assert_that, equal_to, contains_string
from ssh_key_rotator.connections import Client, Server
from tests.ssh_utils import with_ssh_server
import asyncio

class TestClientConnection(IsolatedAsyncioTestCase):
    "Connects the client to the server and runs a couple of commands"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        def __get_username()->str:
            user_path = os.path.expanduser("~")
            user_path_components = user_path.split("/")
            return user_path_components[len(user_path_components)-1]
        self.server : Server|None = None
        self.port = 2500
        self.username = __get_username()
        self.ip_address = "127.0.0.1"

    async def asyncSetUp(self):
        asyncio.get_running_loop().set_debug(False)
    
    @with_ssh_server(port=2500)
    def test_echo_command(self):
        "Can the client connect and call echo?"
        client = self.__connect_client_via_key()
        command = "echo Hello"
        __stdin, stdout, __stderr = client.execute_command(command)
        actual_output = stdout.read().decode()
        expected_output = "Hello\n"
        assert_that(actual_output, equal_to(expected_output))

    @with_ssh_server(port=2500)
    def test_ls_la(self):
        "Can the client connect and call ls -la?"
        client = self.__connect_client_via_key()
        command = "ls -la"
        __stdin, stdout, __stderr = client.execute_command(command)
        actual_output = stdout.read().decode()
        assert_that(actual_output, contains_string("var"))

    def __connect_client_via_key(self)->Client:
        client: Client = Client(self.ip_address, self.port, self.username)
        client.connect_via_key()
        return client