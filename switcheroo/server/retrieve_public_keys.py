#!/usr/bin/env python3.11
import sys
import socket
import os
import boto3


def get_public_keys_local(connecting_user: str, ssh_home_dir: str) -> str:
    host_name = socket.getfqdn()
    key_dir = f"{ssh_home_dir}/{host_name}/{connecting_user}"
    key_path = f"{key_dir}/key-cert.pub"
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
        Bucket=bucket_name, Key=f"{host_name}/{connecting_user}/key-cert.pub"
    )
    ssh_key = response["Body"].read().decode()
    return ssh_key


if __name__ == "__main__":
    CONNECTING_USER = sys.argv[1]
    ORIGIN = sys.argv[2]
    if ORIGIN == "local":
        print(get_public_keys_local(CONNECTING_USER, sys.argv[3]))
    elif ORIGIN == "s3":
        print(get_public_keys_s3(CONNECTING_USER, sys.argv[3]))
