from tempfile import TemporaryDirectory
from pathlib import Path
from typing import Generator, Callable, TypeAlias
import pytest
from aws_profiles import ProfileManager, Profile


@pytest.fixture(name="temp_dir_pathlib")
def fixture_temp_dir_pathlib() -> Generator[Path, None, None]:
    temp_dir = TemporaryDirectory()
    with temp_dir:
        yield Path(temp_dir.name)


@pytest.fixture
def expected_json_file(temp_dir_pathlib: Path):
    return temp_dir_pathlib / "aws_profiles.json"


ManagerGenerator: TypeAlias = Callable[[int], ProfileManager]


@pytest.fixture(name="manager_generator")
def fixture_manager_generator(temp_dir_pathlib: Path) -> ManagerGenerator:
    def _generate_manager(populate_amount: int) -> ProfileManager:
        manager = ProfileManager(temp_dir_pathlib)
        for i in range(1, populate_amount + 1):
            manager.add(f"access-key-{i}", f"secret-access-key-{i}", f"us-east-{i%2+1}")
        return manager

    return _generate_manager


@pytest.fixture(name="profile_manager")
def fixture_profile_manager(manager_generator: ManagerGenerator) -> ProfileManager:
    return manager_generator(0)


@pytest.fixture(name="sample_profile_one", scope="session")
def fixture_sample_profile_one() -> Profile:
    return Profile(0, "access-key-one", "secret-access-key-1", "us-east-1")


@pytest.fixture(name="sample_profile_two", scope="session")
def fixture_sample_profile_two() -> Profile:
    return Profile(1, "access-key-2", "secret-access-key-2", "us-east-2")


@pytest.fixture(name="populated_profile_manager")
def fixture_populated_profile_manager(
    profile_manager: ProfileManager, sample_profile_one: Profile
) -> ProfileManager:
    profile_manager.add(
        sample_profile_one.access_key,
        sample_profile_one.secret_access_key,
        sample_profile_one.region,
    )
    return profile_manager


@pytest.fixture
def doubly_populated_profile_manager(
    populated_profile_manager: ProfileManager, sample_profile_two: Profile
) -> ProfileManager:
    populated_profile_manager.add(
        sample_profile_two.access_key,
        sample_profile_two.secret_access_key,
        sample_profile_two.region,
    )
    return populated_profile_manager
