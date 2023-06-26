"Testing SSH connection using ssh_key_rotator.connections Client & Server"
from unittest import IsolatedAsyncioTestCase
import os
import asyncio
from hamcrest import assert_that, equal_to, contains_string, has_length
from paramiko import RSAKey
from ssh_key_rotator.connections import Client, Server
from ssh_key_rotator.ssh_decorators import with_ssh_server_and_client


class TestClientConnection(IsolatedAsyncioTestCase):
    "Connects the client to the server and runs a couple of commands"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        def __get_username() -> str:
            user_path = os.path.expanduser("~")
            user_path_components = user_path.split("/")
            return user_path_components[len(user_path_components) - 1]

        self.server: Server | None = None
        self.port = 2500
        self.username = __get_username()
        self.ip_address = "127.0.0.1"

    async def asyncSetUp(self):
        asyncio.get_running_loop().set_debug(False)

    @with_ssh_server_and_client()
    def test_echo_command(self, client: Client):
        "Can the client connect and call echo?"
        command = "echo Hello"
        __stdin, stdout, __stderr = client.execute_command(command)
        actual_output = stdout.read().decode()
        expected_output = "Hello\n"
        assert_that(actual_output, equal_to(expected_output))

    @with_ssh_server_and_client()
    def test_ls_la(self, client: Client):
        "Can the client connect and call ls -la?"
        command = "ls -la"
        __stdin, stdout, __stderr = client.execute_command(command)
        actual_output = stdout.read().decode()
        assert_that(actual_output, contains_string("var"))

    @with_ssh_server_and_client()
    async def test_server_side(self, server: Server, key: RSAKey):
        "Connect the client and ensure the key used matches the one we generated"
        logs = await server.get_logs()
        line_with_fingerprint_filtered = list(
            filter(lambda line: line.startswith("Accepted key RSA"), logs)
        )
        assert_that(line_with_fingerprint_filtered, has_length(1))
        line_with_fingerprint: str = line_with_fingerprint_filtered[0]
        actual_fingerprint = key.fingerprint  # type: ignore
        assert_that(line_with_fingerprint, contains_string(actual_fingerprint))
