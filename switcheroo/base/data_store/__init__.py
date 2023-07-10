import os
from typing import Any, TypeVar
from dataclasses import dataclass
from pathlib import Path
from abc import ABC, abstractmethod
from switcheroo.base.serializer import Serializer
from switcheroo.base.data_store import util

T = TypeVar("T")


class DataStore(ABC):
    def __init__(self):
        self._serializers: dict[str, Serializer[Any]] = dict[str, Serializer[Any]]()

    def _get_serializer_for(self, clas: type[T]) -> Serializer[T]:
        class_identifier = util.get_class_identifier(clas)
        serializer: Serializer[T] | None = self._serializers.get(
            class_identifier
        )  # type: ignore
        if serializer is None:
            raise LookupError(f"Serializer not found for class {class_identifier}")
        return serializer

    def serialize(self, item: Any) -> str:
        serializer: Serializer[Any] = self._get_serializer_for(item.__class__)
        serialized_data = serializer.serialize(item)
        return serialized_data

    def deserialize(self, serialized_data: str, storable_type: type[T]) -> T:
        serializer = self._get_serializer_for(storable_type)
        deserialized_storable = serializer.deserialize(serialized_data)
        return deserialized_storable

    @abstractmethod
    def publish(self, item: Any, location: Path):
        pass

    @abstractmethod
    def retrieve(self, location: Path, clas: type[T]) -> T:
        pass

    def register_serializer(self, clas: type[T], serializer: Serializer[T]):
        self._serializers[util.get_class_identifier(clas)] = serializer


class FileDataStore(DataStore):
    @dataclass(frozen=True)
    class FilePermissions:
        mode: int

    def __init__(self, root: Path):
        super().__init__()
        self._root = root
        self._file_permission_settings: dict[str, FileDataStore.FilePermissions]

    def register_file_permissions(self, clas: type, perms: FilePermissions):
        self._file_permission_settings[util.get_class_identifier(clas)] = perms

    def _write(self, unserialized_item: Any, data: str, relative_loc: Path):
        os.umask(0)
        file_perms = self._file_permission_settings.get(
            util.get_class_identifier(unserialized_item.__class__)
        )

        # 511 is the default value of os.open
        target_mode = 511 if file_perms is None else file_perms.mode

        # Opener to restrict permissions
        def open_restricted_permissions(path: str, flags: int):
            return os.open(path=str(path), flags=flags, mode=target_mode)

        with open(
            str(self._root / relative_loc),
            mode="wt",
            opener=open_restricted_permissions,
            encoding="utf-8",
        ) as out:
            out.write(data)

    def publish(self, item: Any, location: Path):
        serialized_data = super().serialize(item)
        self._write(item, serialized_data, location)

    def retrieve(self, location: Path, clas: type[T]) -> T:
        with open(str(self._root / location), mode="rt", encoding="utf-8") as data_file:
            data: str = data_file.read()
            return super().deserialize(data, clas)
