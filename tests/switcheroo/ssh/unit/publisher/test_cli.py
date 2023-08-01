import pytest
from hamcrest import assert_that, calling, raises, contains_string
from switcheroo.ssh.scripts.publish import main


# The main script assumes that we are loading in credentials - cannot mock
@pytest.mark.nomock
@pytest.mark.require_credentials
class TestPublishCLI:
    def test_local_ds_with_bucket_flag(self, capsys, some_host: str, some_name: str):
        "Test that error is raised when the user inputs --bucket with local ds"
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
            raises(SystemExit),
        )
        captured = capsys.readouterr()
        expected = 'Invalid argument "--bucket" when storing the keys locally'
        assert_that(captured.err, contains_string(expected))

    def test_s3_ds_with_no_bucket(self, capsys, some_host: str, some_name: str):
        "Test that error is raised when the user doesn't input --bucket with s3 ds"
        user_input = ["-ds", "s3", f"{some_host}", f"{some_name}"]
        assert_that(
            calling(main).with_args(user_input),  # type: ignore
            raises(SystemExit),
        )
        captured = capsys.readouterr()
        expected = "The s3 option requires a bucket name!"
        assert_that(captured.err, contains_string(expected))

    def test_metricpath_with_aws_metrics(self, capsys, some_host: str, some_name: str):
        "Test that error is raised when the user inputs --metricpath with aws metric publisher"
        user_input = [  # pylint: disable=duplicate-code
            "-ds",
            "local",
            "-m",
            "aws",
            "--metricpath",
            f"/{some_name}/switcheroo/metrics",
            f"{some_host}",
            f"{some_name}",
        ]
        assert_that(
            calling(main).with_args(user_input),  # type: ignore
            raises(SystemExit),
        )
        captured = capsys.readouterr()
        expected = 'Invalid argument "--metricpath" when storing the metrics on AWS'
        assert_that(captured.err, contains_string(expected))
