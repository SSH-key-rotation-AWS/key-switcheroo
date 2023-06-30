"SSH Server"
from typing import Callable
import os
import asyncio
import pathlib
import subprocess
from asyncio.subprocess import Process
from tempfile import NamedTemporaryFile
from ssh_key_rotator.server.data_stores import DataStore
from ssh_key_rotator.util import get_open_port
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
        python_executable = f"{os.getcwd()}/.venv/bin/python"
        target_script = "/ssh_key_switcheroo/retrieve_public_keys.py"
        ky_cmnd = f"{python_executable} {target_script} %u {self.data_store.get_sshd_config_line()}"
        python_executable = f"{os.getcwd()}/.venv/bin/python"
        target_script = "/ssh_key_switcheroo/retrieve_public_keys.py"
        ky_cmnd = f"{python_executable} {target_script} %u {self.data_store.get_sshd_config_line()}"
        config: list[str] = [
            "LogLevel DEBUG3",
            f"Port {self.port}",
            f"HostKey {user_path}/etc/ssh/ssh_host_rsa_key",
            f"PidFile {user_path}/var/run/sshd.pid",
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
        log_file = f"{get_user_path()}/ssh/sshd_log"
        os.remove(log_file)

    @property
    async def logs(self) -> list[str]:
        "Returns the sshd logs"
        log_file = f"{get_user_path()}/ssh/sshd_log"
        with open(log_file, mode="rt", encoding="utf-8") as logs:
            return logs.readlines()

    @staticmethod
    def __setup_host_keys():
        user_path = get_user_path()
        ssh_dir = f"{user_path}/etc/ssh"
        if not os.path.isdir(ssh_dir):
            os.mkdir(ssh_dir)
            subprocess.run("ssh-keygen -A -f ~", shell=True, check=True)

    @staticmethod
    def __setup_pid_file():
        user_path = get_user_path()
        run_dir = f"{user_path}/var/run"
        if not os.path.isdir(run_dir):
            os.mkdir(run_dir)

    def __setup_authorized_keys_script(self):
        parent_dir = pathlib.Path(__file__).parent.resolve()
        app_data_dir = "/ssh_key_switcheroo"
        python_retrieval_script_path = f"{parent_dir}/retrieve_public_keys.py"
        target_path = f"{app_data_dir}/retrieve_public_keys.py"
        if not os.path.exists(app_data_dir):
            subprocess.run(f"sudo mkdir {app_data_dir}", check=True, shell=True)
        subprocess.run(
            f"sudo cp {python_retrieval_script_path} {target_path}",
            shell=True,
            check=True,
        )
        subprocess.run(
            f"sudo chgrp 0 {python_retrieval_script_path}", check=True, shell=True
        )
        subprocess.run(
            f"sudo chmod 755 {python_retrieval_script_path}", check=True, shell=True
        )

    async def __aenter__(self):
        self.__setup_host_keys()
        self.__setup_pid_file()
        self.__setup_authorized_keys_script()
        self.__setup_authorized_keys_script()
        self.data_store.__enter__()
        await self.start()
        return self

    async def __aexit__(self, one, two, three):
        await self.stop()
        self.data_store.__exit__(None, None, None)
