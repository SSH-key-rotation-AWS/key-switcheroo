"SSH Client/Server wrappers"
from asyncio.subprocess import Process
from tempfile import NamedTemporaryFile
import os
import asyncio
import paramiko
from paramiko import SSHClient, AutoAddPolicy
from .util import get_user_path, get_username

class Server:
    """Wrapper for server"""

    def __init__(self, port: int):
        self.port = port
        self.process: Process|None = None

    async def start(self):
        "Emulates ssh server with custom configuration"
        user_path = get_user_path()

        config: list[str] = [
            "LogLevel INFO",
            f"Port {self.port}",
            f"HostKey {user_path}/etc/ssh/ssh_host_rsa_key",
            f"PidFile {user_path}/var/run/sshd.pid",
            "UsePAM yes",
            f"AuthorizedKeysFile {user_path}/.ssh/authorized_keys",
            "PasswordAuthentication yes",
            "KbdInteractiveAuthentication yes",
            "PubkeyAuthentication yes"
        ]
        #Configuration is emitted as a temporary file to launch sshd
        with NamedTemporaryFile(mode="w+t") as fp:
            for option in config:
                fp.write(f"{option}\n")
            fp.file.flush()
            command: str = f"/usr/sbin/sshd -f\"{fp.name}\" -e"
            task:Process = await asyncio.create_subprocess_shell(command,
                                                                 user=get_username(),
                                                        stdout=asyncio.subprocess.PIPE,
                                                        stderr=asyncio.subprocess.PIPE)
            self.process = task
            await self.process.wait()

    async def stop(self):
        "Stops the server, completely closing the process such that the port can be used"
        #If process is still running
        if self.process.returncode is None:
            self.process.terminate()
            # See https://github.com/encode/httpx/issues/914
            await asyncio.sleep(1)
            await asyncio.create_subprocess_shell(f"fuser -k {self.port}/tcp")


class Client:
    "Wrapper for basic SSH Client"
    def __init__(self, host: str, port: int, username: str):
        self.ssh_host = host
        self.ssh_port = port
        self.ssh_username = username
        self.client = self.__create_client()

    def __create_client(self) -> SSHClient:
        client: SSHClient = paramiko.SSHClient()
        client.set_missing_host_key_policy(AutoAddPolicy())
        return client

    def connect_via_username(self, password: str):
        "Connect to the SSH server via passed in password"
        self.client.connect(hostname=self.ssh_host,
                            port=self.ssh_port,
                            username=self.ssh_username,
                            password=password)

    def connect_via_key(self):
        '''Connect to the SSH server via a private key. This key must be called key,
            and is located at ~/.ssh/key. The public key must be called ~/.ssh/key.pub
        '''
        user_path = os.path.expanduser("~")
        ssh_path = f"{user_path}/.ssh"
        ssh_private_key_path = f"{ssh_path}/key"
        ssh_private_key = paramiko.RSAKey.from_private_key_file(
            ssh_private_key_path)
        self.client.connect(hostname=self.ssh_host,
                            port=self.ssh_port,
                            username=self.ssh_username,
                            pkey=ssh_private_key)

    def execute_command(self, command: str):
        '''Executes a command in the host, assuming either 
        connect_via_key or connect_via_username was called first'''
        return self.client.exec_command(command=command)