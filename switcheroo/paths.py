from pathlib import Path
from switcheroo.ssh.objects.key import KeyMetadata, KeyGen


def local_ssh_home() -> Path:
    """Path to the .ssh dir"""
    return Path.home() / ".ssh"


def local_key_dir(host: str, user: str, home_dir: Path | None = None) -> Path:
    """Path to where local keys are stored for a host/user"""
    if home_dir is None:
        home_dir = local_ssh_home()
    return home_dir / host / user


def local_public_key_loc(host: str, user: str, home_dir: Path | None) -> Path:
    """Path to the public key (if stored locally) for a host/user"""
    return local_key_dir(host, user, home_dir=home_dir) / KeyGen.PUBLIC_KEY_NAME


def local_relative_public_key_loc(host: str, user: str) -> Path:
    return Path(host) / user / KeyGen.PUBLIC_KEY_NAME


def local_relative_private_key_loc(host: str, user: str) -> Path:
    return Path(host) / user / KeyGen.PRIVATE_KEY_NAME


def local_private_key_loc(host: str, user: str, home_dir: Path | None) -> Path:
    """Path to the private key for a host/user"""
    return local_key_dir(host, user, home_dir=home_dir) / KeyGen.PRIVATE_KEY_NAME


def local_metadata_loc(host: str, user: str, home_dir: Path | None) -> Path:
    return local_key_dir(host, user, home_dir=home_dir) / KeyMetadata.FILE_NAME


def local_relative_metadata_loc(host: str, user: str) -> Path:
    return Path(host) / user / KeyMetadata.FILE_NAME


def cloud_key_dir(host: str, user: str) -> Path:
    return Path(host) / user


def cloud_public_key_loc(host: str, user: str) -> Path:
    """Path to the public key (if stored in the cloud) for a host/user"""
    return cloud_key_dir(host, user) / KeyGen.PUBLIC_KEY_NAME


def cloud_metadata_loc(host: str, user: str) -> Path:
    return cloud_key_dir(host, user) / KeyMetadata.FILE_NAME

def local_metrics_dir() -> Path:
    metrics_dir = Path.home() / "metrics"
    metrics_dir.mkdir(exist_ok=True)
    return metrics_dir
