from pathlib import Path
from hamcrest import assert_that, contains_string
from switcheroo.ssh.data_org.publisher import FileKeyPublisher
from switcheroo import paths


def test_local_publish(ssh_temp_path: Path, file_pub: FileKeyPublisher):
    """Test for local publisher"""
    host = "ExampleServer"
    user_id = "1234567"
    key, _ = file_pub.publish_key(host, user_id)
    public_key_path = paths.local_public_key_loc(host, user_id, ssh_temp_path)
    with open(public_key_path, encoding="utf-8") as public_key_file:
        file_contents = public_key_file.read()
        assert_that(file_contents, contains_string(key.public_key.byte_data.decode()))
