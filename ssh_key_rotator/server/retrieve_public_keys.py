#!/usr/bin/env python3.11
import sys
import socket
import os
import boto3


def get_public_keys_local(connecting_user: str) -> str:
    host_name = socket.getfqdn()
    user_path = os.path.expanduser("~")
    key_dir = f"{user_path}/.ssh/{host_name}"
    key_path = f"{key_dir}/{connecting_user}-cert.pub"
    if not os.path.isdir(key_dir):
        os.makedirs(key_dir)
    if not os.path.exists(key_path):
        return ""
    with open(key_path, mode="rt", encoding="utf-8") as key_file:
        return key_file.read()


def get_public_keys_s3(connecting_user: str, bucket_name: str) -> str:
    host_name = socket.getfqdn()
    s3_client = boto3.client("s3")
    response = s3_client.get_object(
        Bucket=bucket_name, Key=f"{host_name}/{connecting_user}-cert.pub"
    )
    ssh_key = response["Body"].read().decode()
    return ssh_key


if __name__ == "__main__":
    CONNECTING_USER = sys.argv[1]
    ORIGIN = sys.argv[2]
    if ORIGIN == "local":
        print(get_public_keys_local(CONNECTING_USER))
    elif ORIGIN == "s3":
        print(get_public_keys_s3(CONNECTING_USER, sys.argv[3]))
