from unittest import TestCase
from hamcrest import assert_that, contains_string
from ssh_key_rotator.publisher.key_publisher import LocalPublisher, S3Publisher
from ssh_key_rotator.util import get_user_path


class PublisherTests(TestCase):

    """Tests for publisher class"""

    def test_local_publish(self):
        """Test for local publisher"""
        localpub = LocalPublisher()
        public_key = localpub.publish_new_key()
        authorized_keys_path = f"{get_user_path()}/.ssh/authorized_keys"
        with open(authorized_keys_path, encoding="utf-8") as authorized_keys_file:
            file_contents = authorized_keys_file.read()
            assert_that(file_contents, contains_string(public_key))

    def test_s3_publish(self):
        """Test for S3 publisher"""
        s3_publisher = S3Publisher()  # pylint: disable=unused-variable
