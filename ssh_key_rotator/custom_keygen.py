"Module for generating public/private SSH key pairs"
import os
import shutil
from Crypto.PublicKey import RSA

PRIVATE_KEY_NAME: str = "key"
PUBLIC_KEY_NAME: str = f"{PRIVATE_KEY_NAME}-cert.pub"

def generate_private_public_key_in_file(temp_dir: str):
    "Creates a private key and public key at the given paths"
    key = RSA.generate(1024)
    user_path = os.path.expanduser("~")
    user_path_components = user_path.split("/")
    user = user_path_components[len(user_path_components) - 1]

    # ssh_path = f"{user_path}/.ssh"
    private_key_path = f"{temp_dir}/key"
    public_key_path = f"{temp_dir}/key-cert.pub"

    private_key = key.export_key()

    with open(private_key_path, "wb") as private_out:
        private_out.write(private_key)

    shutil.chown(private_key_path, user=user, group=-1)
    os.chmod(private_key_path, 0o600)

    public_key = key.public_key().export_key(format="OpenSSH")
    with open(public_key_path, "wb") as public_out:
        public_out.write(public_key)
    return public_key
