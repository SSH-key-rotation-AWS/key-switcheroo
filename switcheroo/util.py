"""Utility functions"""
from socket import getservbyport
from random import randint
import os
from pathlib import Path
from switcheroo.custom_keygen import KeyGen
from switcheroo.ssh.objects.key import KeyMetadata


def get_open_port() -> int:
    "Returns a random open port, starting at 1024"
    start_port = 1024
    all_primary_ports = list(range(start_port, start_port + 100))
    last_selectable_port = all_primary_ports[len(all_primary_ports) - 1]

    def select_new_port() -> int:
        nonlocal all_primary_ports
        if len(all_primary_ports) == 0:  # Out of ports
            nonlocal last_selectable_port
            # Create a new port range to choose from
            all_primary_ports = list(
                range(last_selectable_port + 1, last_selectable_port + 1001)
            )
            last_selectable_port += 100
        # Choose a new port
        new_port_index = randint(0, len(all_primary_ports) - 1)
        # Remove it from our options, so we dont choose it again
        del all_primary_ports[new_port_index]
        return all_primary_ports[new_port_index]

    # Select a new port until we find an open one
    while True:
        selected_port = select_new_port()
        try:
            getservbyport(selected_port)
        except OSError:
            return selected_port


def store_private_key(private_key: bytes, private_key_dir: Path):
    private_key_dir.mkdir(parents=True, exist_ok=True)
    private_key_path = private_key_dir / KeyGen.PRIVATE_KEY_NAME
    os.umask(0)

    # Opener to restrict permissions
    def open_restricted_permissions(path: str, flags: int):
        return os.open(path=str(path), flags=flags, mode=0o600)

    with open(
        str(private_key_path),
        mode="wt",
        encoding="utf-8",
        opener=open_restricted_permissions,
    ) as private_out:
        private_out.write(private_key.decode())


def store_public_key(public_key: bytes, public_key_dir: Path):
    public_key_dir.mkdir(parents=True, exist_ok=True)
    public_key_path = public_key_dir / KeyGen.PUBLIC_KEY_NAME
    with open(public_key_path, mode="wt", encoding="utf-8") as public_out:
        public_out.write(public_key.decode())


def generate_private_public_key_in_file(
    public_key_dir: Path, private_key_dir: Path | None = None
) -> tuple[bytes, bytes]:
    "Creates a private key and public key at the given paths"
    # If private key was not given a separate dir, use the same one as for public key
    if private_key_dir is None:
        private_key_dir = public_key_dir
    # Generate the keys
    private_key, public_key = KeyGen.generate_private_public_key()
    # Store them
    store_private_key(private_key, private_key_dir)
    store_public_key(public_key, public_key_dir)
    metadata = KeyMetadata.now_by_executing_user()
    with open(
        public_key_dir / KeyMetadata.FILE_NAME, mode="wt", encoding="utf-8"
    ) as metadata_file:
        metadata_file.write(metadata.serialize_to_string())
    return private_key, public_key
