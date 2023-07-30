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
        serverdata_dir: Path,
        port: int | Callable[[], int] = get_open_port,
        authorized_key_command_executing_user: str | None = None,
    ):
        if callable(port):
            port = port()
        if authorized_key_command_executing_user is None:
            authorized_key_command_executing_user = getuser()
        self.port = port
        self.key_retriever = retriever
        self.authorized_key_command_executing_user = (
            authorized_key_command_executing_user
        )
        self.process: Process | None = None
        self._log_file = serverdata_dir / "sshd_log"
        self._hostkeys_dir = serverdata_dir / "etc" / "ssh"
        self._serverdata_dir = serverdata_dir

    async def start(self):
        # If host keys do not exist, create them
        self.__setup_host_keys()
        # Create log file
        self._log_file.parent.mkdir(parents=True, exist_ok=True)
        self._log_file.touch(exist_ok=True)
        # Create pid file
        pid_file = self._serverdata_dir / "sshd.pid"
        pid_file.parent.mkdir(parents=True, exist_ok=True)
        pid_file.touch(exist_ok=True)
        repo_dir = pathlib.Path(__file__).parent.parent.parent.parent.resolve()
        venv = repo_dir / ".venv"
        python_executable = venv / "bin" / "python"
        scripts_dir = repo_dir / "switcheroo" / "ssh" / "scripts"
        target_script = scripts_dir / "retrieve.py"
        ky_cmnd = f"{str(python_executable)} {str(target_script)} %u {self.key_retriever.command}"
        config: list[str] = [
            "LogLevel DEBUG3",
            f"Port {self.port}",
            f"HostKey {str(self._hostkeys_dir)}/ssh_host_rsa_key",
            f"PidFile {str(pid_file)}",
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
                f'/usr/sbin/sshd -f"{temp_config.name}" -E{str(self._log_file)}'
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
        self._log_file.unlink()

    @property
    async def logs(self) -> list[str]:
        "Returns the sshd logs"
        with open(self._log_file, mode="rt", encoding="utf-8") as logs:
            return logs.readlines()

    def __setup_host_keys(self):
        # user_path = Path.home()
        self._hostkeys_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            f"ssh-keygen -A -f {str(self._serverdata_dir)}", shell=True, check=True
        )

    # @staticmethod
    # def __setup_pid_file():
    #     user_path = Path.home()
    #     run_dir = user_path / "var" / "run"
    #     run_dir.mkdir(exist_ok=True, parents=True)

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, one, two, three):  # type: ignore
        await self.stop()
