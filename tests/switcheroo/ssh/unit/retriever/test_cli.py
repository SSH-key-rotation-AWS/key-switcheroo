from hamcrest import assert_that, calling, raises
import pytest
from switcheroo.ssh.scripts.retrieve import main
from switcheroo.ssh.scripts.custom_argument_exceptions import (
    InvalidArgumentError,
    MissingArgumentError,
)


@pytest.mark.nomock
@pytest.mark.require_credentials
class TestCLI:
    def test_local_ds_with_bucket_flag_exception(self, some_name: str):
        "Test that exception is thrown when the user inputs --bucket with local ds"
        user_input = [  # pylint: disable=duplicate-code
            "-ds",
            "local",
            "--bucket",
            "mybucket",
            f"{some_name}",
        ]
        assert_that(
            calling(main).with_args(user_input),  # type: ignore
            raises(InvalidArgumentError),
        )

    def test_s3_ds_with_no_bucket_exception(self, some_name: str):
        "Test that exception is thrown when the user doesn't input --bucket with s3 ds"
        user_input = ["-ds", "s3", f"{some_name}"]
        assert_that(
            calling(main).with_args(user_input),  # type: ignore
            raises(MissingArgumentError),
        )

    # def test_no_user_exception(self):
    #     "Test that exception is thrown when no user is input"
    #     user_input = [
    #         "-ds",
    #         "local",
    #     ]
    #     assert_that(calling(main).with_args(user_input), raises(SystemExit))
