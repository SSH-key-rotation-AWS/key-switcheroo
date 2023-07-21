import pytest
from moto import mock_sts, mock_s3, mock_cloudwatch


@pytest.fixture(autouse=True)
def try_this():
    return 1


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
