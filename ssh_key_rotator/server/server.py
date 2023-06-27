"SSH Server"
from typing import Callable
import os
import asyncio
from asyncio.subprocess import Process
from tempfile import NamedTemporaryFile
from ssh_key_rotator.server.data_stores import DataStore
from ssh_key_rotator.ssh_decorators import get_open_port
from ssh_key_rotator.util import get_user_path, get_username


class Server:
    "Wrapper for SSH Server. Takes a DataStore to determine where to look for keys"

    def __init__(
        self,
        data_store: DataStore,
        port: int | Callable[[], int] = get_open_port,
        authorized_key_command_executing_user: str = get_username(),
    ):
        if callable(port):
            port = port()
        self.port = port
        self.data_store = data_store
        self.authorized_key_command_executing_user = (
            authorized_key_command_executing_user
        )
        self.process: Process | None = None

    async def start(self):
        user_path = get_user_path()
        # parent_dir = pathlib.Path(__file__).parent.resolve()
        bash_script_path = "/authorized_keys_cmd/retrieve_public_keys.sh"
        # activation_command = f"{os.getcwd()}/.venv/bin/activate"
        keys_cmnd = f"{bash_script_path} %u {self.data_store.get_sshd_config_line()}"
        config: list[str] = [
            "LogLevel DEBUG3",
            f"Port {self.port}",
            f"HostKey {user_path}/etc/ssh/ssh_host_rsa_key",
            f"PidFile {user_path}/var/run/sshd.pid",
            "UsePAM yes",
            "AuthorizedKeysFile none",
            f"AuthorizedKeysCommand {keys_cmnd}",
            f"AuthorizedKeysCommandUser {self.authorized_key_command_executing_user}",
            "PasswordAuthentication no",
            "KbdInteractiveAuthentication no",
            "PubkeyAuthentication yes",
            "StrictModes yes",
        ]
        # Configuration is emitted as a temporary file to launch sshd
        with NamedTemporaryFile(mode="w+t") as temp_config:
            for option in config:
                temp_config.write(f"{option}\n")
            temp_config.file.flush()
            command: str = (
                f'/usr/sbin/sshd -f"{temp_config.name}" -E{user_path}/ssh/sshd_log'
            )
            task: Process = await asyncio.create_subprocess_shell(
                command,
                user=get_username(),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            self.process = task
            await self.process.wait()

    async def stop(self):
        "Stops the server, completely closing the process such that the port can be used"
        # If process is still running
        if not self.process is None and self.process.returncode is None:
            self.process.terminate()
            # See https://github.com/encode/httpx/issues/914
            await asyncio.sleep(1)
        kill_task = await asyncio.create_subprocess_shell(
            f"fuser -k {self.port}/tcp",
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await kill_task.wait()

    @property
    async def logs(self) -> list[str]:
        "Returns the sshd logs"
        log_file = f"{get_user_path()}/ssh/sshd_log"
        with open(log_file, mode="rt", encoding="utf-8") as logs:
            return logs.readlines()

    @staticmethod
    async def __setup_host_keys():
        user_path = get_user_path()
        ssh_dir = f"{user_path}/etc/ssh"
        if not os.path.isdir(ssh_dir):
            os.mkdir(ssh_dir)
            create_host_keys_process = await asyncio.create_subprocess_shell(
                "ssh-keygen -A -f ~"
            )
            await create_host_keys_process.wait()

    @staticmethod
    async def __setup_pid_file():
        user_path = get_user_path()
        run_dir = f"{user_path}/var/run"
        if not os.path.isdir(run_dir):
            os.mkdir(run_dir)

    async def __aenter__(self):
        await self.__setup_host_keys()
        await self.__setup_pid_file()
        self.data_store.__enter__()
        await self.start()
        return self

    async def __aexit__(self, one, two, three):
        await self.stop()
        self.data_store.__exit__(None, None, None)
