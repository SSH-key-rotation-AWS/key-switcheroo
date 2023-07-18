import os
from typing import Any, TypeVar
from dataclasses import dataclass
from pathlib import Path
from abc import ABC, abstractmethod
from switcheroo.base.serializer import Serializer

T = TypeVar("T")


def _get_class_identifier(clas: type) -> str:
    return clas.__module__ + clas.__qualname__


class DataStore(ABC):
    """An abstraction over some location where data is stored/retrieved"""

    def __init__(self):
        self._serializers: dict[str, Serializer[Any]] = {}

    def _get_serializer_for(self, clas: type[T]) -> Serializer[T]:
        class_identifier = _get_class_identifier(clas)
        serializer: Serializer[T] | None = self._serializers.get(
            class_identifier
        )  # type: ignore
        if serializer is None:
            raise LookupError(f"Serializer not found for class {class_identifier}")
        return serializer

    def serialize(self, item: Any) -> str:
        """Uses the serializer from the register_serializer method to serialize an object

        Args:
            item (Any): The object to serialize

        Returns:
            str: The serialized object

        Raises:
            LookupError: If the serializer for the type of this object has not been registered
        """
        serializer: Serializer[Any] = self._get_serializer_for(item.__class__)
        serialized_data = serializer.serialize(item)
        return serialized_data

    def deserialize(self, serialized_data: str, storable_type: type[T]) -> T:
        """Uses the serializer from the register_serializer method to deserialize an object \
        from a string

        Args:
            serialized_data (str): The data to deserialize
            storable_type (type[T]): The type of the desired object

        Returns:
            T: The deserialized object
        
        Raises:
            LookupError: If the serializer for the type of this object has not been registered
        """
        serializer = self._get_serializer_for(storable_type)
        deserialized_storable = serializer.deserialize(serialized_data)
        return deserialized_storable

    @abstractmethod
    def publish(self, item: Any, location: Path):
        """Stores the item in some locaton. Subclasses are expected to use the serialize \
        method to transform the item into a string, and then store the item

        Args:
            item (Any): The item to store
            location (Path): The location to store the item at.
        """

    @abstractmethod
    def retrieve(self, location: Path, clas: type[T]) -> T | None:
        """Retrieves the item from some location. Subclasses are expected to use the deserialize \
        method to parse the object from a retrieved string.

        Args:
            location (Path): the location of the item to retrieve
            clas (type[T]): The type of the desired item

        Returns:
            T | None: The deserialized item, or None if no item is found at that location
        """

    def register_serializer(self, clas: type[T], serializer: Serializer[T]):
        self._serializers[_get_class_identifier(clas)] = serializer


class FileDataStore(DataStore):
    """An abstraction over a file system data store.
    All items are stored relative to some root which is provided at instance creation, \
    and store/publish methods use locations *relative* to that root.
    """

    @dataclass(frozen=True)
    class FilePermissions:
        """What permissions a file used for storage should have for a particular type"""

        mode: int

    @dataclass(frozen=True)
    class RootInfo:
        """Information about where the root of the store is"""

        location: Path
        mode: int = 511

    def __init__(self, root: RootInfo):
        super().__init__()
        self._root = root.location
        # If root folder does not exist, create it
        root.location.mkdir(exist_ok=True, mode=root.mode)
        self._file_permission_settings: dict[str, FileDataStore.FilePermissions] = {}

    def register_file_permissions(self, clas: type, perms: FilePermissions):
        """Register some file permissions for some type - when an object of this type \
        is stored, it will be stored in a file with the given permissions

        Args:
            clas (type): The type which will use these custom file permissions
            perms (FilePermissions): The permissions the files storing objects of this type \
            will have
        """
        self._file_permission_settings[_get_class_identifier(clas)] = perms

    def _write(self, unserialized_item: Any, data: str, relative_loc: Path):
        absolute_location = self._root / relative_loc
        # Create enclosing dir if it does not already exist
        absolute_location.parent.mkdir(parents=True, exist_ok=True)

        os.umask(0)
        file_perms = self._file_permission_settings.get(
            _get_class_identifier(unserialized_item.__class__)
        )

        # 511 is the default value of os.open
        target_mode = 511 if file_perms is None else file_perms.mode

        # Opener to restrict permissions
        def open_restricted_permissions(path: str, flags: int):
            return os.open(path=str(path), flags=flags, mode=target_mode)

        # Write to the file
        with open(
            str(absolute_location),
            mode="wt",
            opener=open_restricted_permissions,
            encoding="utf-8",
        ) as out:
            out.write(data)

    def publish(self, item: Any, location: Path):
        """See base class. Stores objects in files.

        Args:
            item (Any): The item to store
            location (Path): The location of this object *relative* to the root of this datastore
        """
        serialized_data = super().serialize(item)
        self._write(item, serialized_data, location)

    def retrieve(self, location: Path, clas: type[T]) -> T | None:
        """See base class"""
        try:
            with open(
                str(self._root / location), mode="rt", encoding="utf-8"
            ) as data_file:
                data: str = data_file.read()
                return super().deserialize(data, clas)
        except FileNotFoundError:
            return None
