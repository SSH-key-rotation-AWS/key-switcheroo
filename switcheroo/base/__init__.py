# pyright: reportUnusedImport=false
from pathlib import Path
from switcheroo.base.data_store import DataStore
from switcheroo.base.serializer import Serializer


class Constants:  # pylint: disable = too-few-public-methods
    APP_DATA_DIR: Path = Path.home() / ".switcheroo"
