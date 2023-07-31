import pytest
from moto import mock_sts, mock_s3, mock_cloudwatch
from aws_profiles import ProfileManager
from switcheroo.base import Constants

_fake_credentials: tuple[str, str, str] = (
    "Fake access key",
    "Fake secret access key",
    "us-east-1",
)


@pytest.fixture(name="credentials")
def fixture_credentials() -> (  # pylint: disable=inconsistent-return-statements
    tuple[str, str, str]
):
    manager = ProfileManager(Constants.APP_DATA_DIR)
    selected_credentials = manager.current_profile
    if selected_credentials is None:
        return _fake_credentials
    return (
        selected_credentials.access_key,
        selected_credentials.secret_access_key,
        selected_credentials.region,
    )


@pytest.fixture(autouse=True)
def skip_by_require_credentials(request, credentials: tuple[str, str, str]):
    if "require_credentials" in request.keywords and credentials == _fake_credentials:
        pytest.skip("skipped this test because no credentials were configured")


@pytest.fixture(name="mock_inner_sts_client", autouse=True)
def fixture_mock_inner_sts_client(request):
    if "nomock" in request.keywords:
        yield
        return
    mock_sts_process = mock_sts()
    mock_sts_process.start()
    yield
    mock_sts_process.stop()


@pytest.fixture(name="mock_inner_s3_client", autouse=True)
def fixture_mock_inner_s3_client(request):
    if "nomock" in request.keywords:
        yield
        return
    mock_s3_process = mock_s3()
    mock_s3_process.start()
    yield
    mock_s3_process.stop()


@pytest.fixture(name="mock_inner_cloudwatch_client", autouse=True)
def fixture_mock_inner_cloudwatch_client(request):
    if "nomock" in request.keywords:
        yield
        return
    mock_cw_process = mock_cloudwatch()
    mock_cw_process.start()
    yield
    mock_cw_process.stop()
