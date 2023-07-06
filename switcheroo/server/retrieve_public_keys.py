#!/usr/bin/env python3.11
import sys
import socket
from pathlib import Path
from switcheroo.data_store import DataStore, FileSystemDataStore
from switcheroo.data_store.s3 import S3DataStore

if __name__ == "__main__":
    CONNECTING_USER = sys.argv[1]
    ORIGIN = sys.argv[2]
    data_store: DataStore | None = None
    if ORIGIN == "local":
        data_store = FileSystemDataStore(ssh_home=Path(sys.argv[3]))
    elif ORIGIN == "s3":
        data_store = S3DataStore(sys.argv[3])
    assert data_store is not None
    public_key = data_store.retrieve(socket.getfqdn(), CONNECTING_USER)
    print(public_key)
