"SSH Client/Server wrappers"
from asyncio.subprocess import Process
from tempfile import NamedTemporaryFile
import asyncio
import paramiko
from paramiko import SSHClient, AutoAddPolicy, RSAKey
from ssh_key_rotator.util import get_user_path, get_username, get_default_authorized_keys_path
from ssh_key_rotator.custom_keygen import PRIVATE_KEY_NAME

class Server:
    """Wrapper for server"""

    def __init__(self, port: int, ssh_home: str|None = None):
        self.port = port
        self.process: Process|None = None
        if ssh_home is None:
            self.authorized_keys_file = get_default_authorized_keys_path()
        else:
            self.authorized_keys_file = f"{ssh_home}/authorized_keys"
        self.log_file = None if ssh_home is None else f"{ssh_home}/logs"

    async def start(self):
        "Emulates ssh server with custom configuration"
        user_path = get_user_path()
        config: list[str] = [
            "LogLevel VERBOSE",
            f"Port {self.port}",
            f"HostKey {user_path}/etc/ssh/ssh_host_rsa_key",
            f"PidFile {user_path}/var/run/sshd.pid",
            "UsePAM yes",
            f"AuthorizedKeysFile {self.authorized_keys_file}",
            "PasswordAuthentication yes",
            "KbdInteractiveAuthentication yes",
            "PubkeyAuthentication yes",
            "StrictModes no"
        ]
        #Configuration is emitted as a temporary file to launch sshd
        with NamedTemporaryFile(mode="w+t") as temp_config:
            for option in config:
                temp_config.write(f"{option}\n")
            temp_config.file.flush()
            command: str = f"/usr/sbin/sshd -f\"{temp_config.name}\""
            if not self.log_file is None:
                command += f" -E{self.log_file}"
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
        kill_task = await asyncio.create_subprocess_shell(f"fuser -k {self.port}/tcp",
                                                          stdout=asyncio.subprocess.DEVNULL,
                                                          stderr=asyncio.subprocess.DEVNULL)
        await kill_task.wait()

    async def get_logs(self):
        "Get the logs of the server, returns a list[str] of the lines of the logs"
        if self.log_file is None:
            raise RuntimeError("Cannot get logs if no ssh home path was specified")
        with open(self.log_file, mode="rt", encoding="utf-8") as logs:
            return logs.readlines()

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_t, exc_v, exc_tb):
        await self.stop()



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
        client.load_system_host_keys()
        return client

    def connect_via_username(self, password: str):
        "Connect to the SSH server via passed in password"
        self.client.connect(hostname=self.ssh_host,
                            port=self.ssh_port,
                            username=self.ssh_username,
                            password=password)

    def connect_via_key(self, key_location: str):
        '''Connect to the SSH server via a private key. This key must be called key,
            and is located at ~/.ssh/key. The public key must be called ~/.ssh/key.pub
        '''
        #user_path = os.path.expanduser("~")
        #ssh_path = f"{user_path}/.ssh"
        ssh_private_key_path = f"{key_location}/{PRIVATE_KEY_NAME}"
        #ssh_public_key_path = f"{key_location}/{PUBLIC_KEY_NAME}"

        self.client.connect(hostname=self.ssh_host,
                            port=self.ssh_port,
                            username=self.ssh_username,
                            pkey=RSAKey.from_private_key_file(ssh_private_key_path))

    def execute_command(self, command: str):
        '''Executes a command in the host, assuming either 
        connect_via_key or connect_via_username was called first'''
        return self.client.exec_command(command=command)
