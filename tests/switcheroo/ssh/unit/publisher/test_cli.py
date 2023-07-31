import pytest
from hamcrest import assert_that, calling, raises
from switcheroo.ssh.scripts.publish import main
from switcheroo.ssh.scripts.custom_argument_exceptions import (
    InvalidArgumentError,
    MissingArgumentError,
)


# The main script assumes that we are loading in credentials - cannot mock
@pytest.mark.nomock
@pytest.mark.require_credentials
class TestPublishCLI:
    def test_local_ds_with_bucket_flag_exception(self, some_host: str, some_name: str):
        "Test that exception is thrown when the user inputs --bucket with local ds"
        user_input = [  # pylint: disable=duplicate-code
            "-ds",
            "local",
            "--bucket",
            "mybucket",
            f"{some_host}",
            f"{some_name}",
        ]
        assert_that(
            calling(main).with_args(user_input),  # type: ignore
            raises(InvalidArgumentError),
        )

    def test_s3_ds_with_no_bucket_exception(self, some_host: str, some_name: str):
        "Test that exception is thrown when the user doesn't input --bucket with s3 ds"
        user_input = ["-ds", "s3", f"{some_host}", f"{some_name}"]
        assert_that(
            calling(main).with_args(user_input),  # type: ignore
            raises(MissingArgumentError),
        )

    # def test_no_user_exception(self, some_host: str):
    #     "Test that exception is thrown when no user is input"
    #     user_input = [
    #         "-ds",
    #         "local",
    #         f"{some_host}",
    #     ]
    #     assert_that(calling(main).with_args(user_input),
    #     raises(UnconfiguredAWSException)) #type: ignore
