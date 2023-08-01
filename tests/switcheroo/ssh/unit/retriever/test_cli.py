from hamcrest import assert_that, calling, raises, contains_string
import pytest
from switcheroo.ssh.scripts.retrieve import main


@pytest.mark.nomock
@pytest.mark.require_credentials
class TestCLI:
    def test_local_ds_with_bucket_flag(self, capsys, some_name: str):
        "Test that error is raised when the user inputs --bucket with local ds"
        user_input = [  # pylint: disable=duplicate-code
            "-ds",
            "local",
            "--bucket",
            "mybucket",
            f"{some_name}",
        ]
        assert_that(
            calling(main).with_args(user_input),  # type: ignore
            raises(SystemExit),
        )
        captured = capsys.readouterr()
        expected = 'Invalid argument "--bucket" when retrieving the keys locally'
        assert_that(captured.err, contains_string(expected))

    def test_s3_ds_with_no_bucket(self, capsys, some_name: str):
        "Test that erorr is raised when the user doesn't input --bucket with s3 ds"
        user_input = ["-ds", "s3", f"{some_name}"]
        assert_that(
            calling(main).with_args(user_input),  # type: ignore
            raises(SystemExit),
        )
        captured = capsys.readouterr()
        expected = "The s3 option requires a specified bucket name!"
        assert_that(captured.err, contains_string(expected))

    def test_no_user_exception(self, capsys):
        "Test that error is raised when no user is input"
        user_input = [
            "-ds",
            "local",
        ]
        assert_that(calling(main).with_args(user_input), raises(SystemExit))
        captured = capsys.readouterr()
        expected = "the following arguments are required: user"
        assert_that(captured.err, contains_string(expected))
