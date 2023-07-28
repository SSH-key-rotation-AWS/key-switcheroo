"SSH Server"
from typing import Callable
import asyncio
import pathlib
from pathlib import Path
import subprocess
from asyncio.subprocess import Process
from getpass import getuser
from tempfile import NamedTemporaryFile
from switcheroo.ssh.data_org.retriever import KeyRetriever
from switcheroo.util import get_open_port


class Server:
    "Wrapper for SSH Server. Takes a DataStore to determine where to look for keys"

    def __init__(
        self,
        retriever: KeyRetriever,
        port: int | Callable[[], int] = get_open_port,
        authorized_key_command_executing_user: str = getuser(),
    ):
        if callable(port):
            port = port()
        self.port = port
        self.key_retriever = retriever
        self.authorized_key_command_executing_user = (
            authorized_key_command_executing_user
        )
        self.process: Process | None = None
        self.log_file = Path.home() / "ssh" / "sshd_log"

    async def start(self):
        user_path = Path.home()
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.log_file.touch(exist_ok=True)
        repo_dir = pathlib.Path(__file__).parent.parent.parent.parent.resolve()
        venv = repo_dir / ".venv"
        python_executable = venv / "bin" / "python"
        scripts_dir = repo_dir / "switcheroo" / "ssh" / "scripts"
        target_script = scripts_dir / "retrieve.py"
        ky_cmnd = f"{str(python_executable)} {str(target_script)} %u {self.key_retriever.command}"
        config: list[str] = [
            "LogLevel DEBUG3",
            f"Port {self.port}",
            f"HostKey {str(user_path)}/etc/ssh/ssh_host_rsa_key",
            f"PidFile {str(user_path)}/var/run/sshd.pid",
            "UsePAM yes",
            "AuthorizedKeysFile none",
            f"AuthorizedKeysCommand {ky_cmnd}",
            f"AuthorizedKeysCommand {ky_cmnd}",
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
                f'/usr/sbin/sshd -f"{temp_config.name}" -E{str(self.log_file)}'
            )
            task: Process = await asyncio.create_subprocess_shell(
                command,
                user=getuser(),
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
        self.log_file.unlink()

    @property
    async def logs(self) -> list[str]:
        "Returns the sshd logs"
        with open(self.log_file, mode="rt", encoding="utf-8") as logs:
            return logs.readlines()

    @staticmethod
    def __setup_host_keys():
        user_path = Path.home()
        ssh_dir = user_path / "etc" / "ssh"
        ssh_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run(f"ssh-keygen -A -f {str(user_path)}", shell=True, check=True)

    @staticmethod
    def __setup_pid_file():
        user_path = Path.home()
        run_dir = user_path / "var" / "run"
        run_dir.mkdir(exist_ok=True, parents=True)

    async def __aenter__(self):
        self.__setup_host_keys()
        self.__setup_pid_file()
        await self.start()
        return self

    async def __aexit__(self, one, two, three):  # type: ignore
        await self.stop()
