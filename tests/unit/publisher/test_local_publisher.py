from pathlib import Path
from unittest import TestCase
from hamcrest import assert_that, contains_string
from switcheroo.ssh.data_org.publisher import FileKeyPublisher
from switcheroo import paths
from tests.util import SSHDirCleanup


class LocalPublisherTests(TestCase):

    """Tests for local publisher class"""

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.publisher: FileKeyPublisher | None = None
        self.temp_dir: Path | None = None

    def setUp(self) -> None:
        self.temp_dir = self.enterContext(SSHDirCleanup())
        self.publisher = FileKeyPublisher(self.temp_dir)

    def test_local_publish(self):
        """Test for local publisher"""
        host = "ExampleServer"
        user_id = "1234567"
        assert self.publisher is not None
        key, _ = self.publisher.publish_key(host, user_id)
        public_key_path = paths.local_public_key_loc(host, user_id, self.temp_dir)
        with open(public_key_path, encoding="utf-8") as public_key_file:
            file_contents = public_key_file.read()
            assert_that(
                file_contents, contains_string(key.public_key.byte_data.decode())
            )
