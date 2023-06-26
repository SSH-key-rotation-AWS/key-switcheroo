from unittest import TestCase
from hamcrest import assert_that, contains_string
from ssh_key_rotator.publisher.key_publisher import LocalPublisher
from ssh_key_rotator.util import get_user_path


class LocalPublisherTests(TestCase):

    """Tests for local publisher class"""

    def test_local_publish(self):
        """Test for local publisher"""
        localpub = LocalPublisher("ExampleServer", "12345")
        _, public_key = localpub.publish_new_key()
        public_key_path = f"{get_user_path()}/.ssh/ExampleServer/12345"
        with open(public_key_path, encoding="utf-8") as public_key_file:
            file_contents = public_key_file.read()
            assert_that(file_contents, contains_string(public_key))
