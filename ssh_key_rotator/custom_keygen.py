"Module for generating public/private SSH key pairs"
from Crypto.PublicKey import RSA
import os
import shutil


def generate_private_public_key_in_file(private_key_path: str, public_key_path: str):
    "Creates a private key and public key at the given paths"
    key = RSA.generate(2048)
    user_path = os.path.expanduser("~")
    user_path_components = user_path.split("/")
    user = user_path_components[len(user_path_components) - 1]

    # ssh_path = f"{user_path}/.ssh"
    # private_key_path = f"{ssh_path}/key"
    # public_key_path = f"{ssh_path}/key.pub"

    private_key = key.export_key()

    with open(private_key_path, "wb") as private_out:
        private_out.write(private_key)

    shutil.chown(private_key_path, user=user, group=-1)
    os.chmod(private_key_path, 0o600)

    public_key = key.public_key().export_key(format="OpenSSH")
    with open(public_key_path, "wb") as public_out:
        public_out.write(public_key)

