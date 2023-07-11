from tempfile import TemporaryDirectory
from pathlib import Path
from switcheroo import paths


def ssh_temp_dir():
    return TemporaryDirectory(dir=paths.local_ssh_home(), prefix="switcheroo-test-")


class SSHDirCleanup:
    def __init__(self) -> None:
        self._dir = ssh_temp_dir()

    def __enter__(self):
        self._dir.__enter__()
        return Path(self._dir.name)

    def __exit__(self, one, two, three):  # type: ignore
        self._dir.__exit__(None, None, None)
