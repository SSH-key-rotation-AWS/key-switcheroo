from hamcrest import assert_that, calling, raises
from switcheroo.ssh.scripts.retrieve import main
from switcheroo.ssh.scripts.custom_argument_exceptions import (
    InvalidArgumentError,
    MissingArgumentError,
)


def test_local_ds_with_bucket_flag_exception(some_name):
    "Test that exception is thrown when the user inputs --bucket with local ds"
    user_input = [
        "-ds",
        "local",
        "--bucket",
        "mybucket",
        f"{some_name}",
    ]
    assert_that(calling(main).with_args(user_input), raises(InvalidArgumentError))


def test_s3_ds_with_no_bucket_exception(some_name):
    "Test that exception is thrown when the user doesn't input --bucket with s3 ds"
    user_input = ["-ds", "s3", f"{some_name}"]
    assert_that(calling(main).with_args(user_input), raises(MissingArgumentError))


def test_no_user_exception():
    "Test that exception is thrown when no user is input"
    user_input = [
        "-ds",
        "local",
    ]
    assert_that(calling(main).with_args(user_input), raises(SystemExit))
