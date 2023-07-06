import os
from unittest import TestCase
from hamcrest import assert_that, contains_string
from switcheroo.publisher.key_publisher import LocalPublisher
from switcheroo.custom_keygen import KeyGen
from switcheroo.util import get_user_path


class LocalPublisherTests(TestCase):

    """Tests for local publisher class"""

    def test_local_publish(self):
        """Test for local publisher"""
        localpub = LocalPublisher("ExampleServer", "1234567")
        public_key = localpub.publish_new_key()
        public_key_path = (
            f"{get_user_path()}/.ssh/ExampleServer/1234567/{KeyGen.PUBLIC_KEY_NAME}"
        )
        private_key_path = (
            f"{get_user_path()}/.ssh/ExampleServer/1234567/{KeyGen.PRIVATE_KEY_NAME}"
        )
        with open(public_key_path, encoding="utf-8") as public_key_file:
            file_contents = public_key_file.read()
            assert_that(file_contents, contains_string(public_key))
        os.remove(public_key_path)
        os.remove(private_key_path)
