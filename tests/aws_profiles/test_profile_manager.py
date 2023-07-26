# pylint: disable = line-too-long
from pathlib import Path
import json
from typing import Any
from hamcrest import assert_that, none, equal_to, raises, calling, is_not, has_length  # type: ignore
import pytest
from moto import mock_sts  # type: ignore
from aws_profiles import Profile, ProfileManager
from aws_profiles.exceptions import (
    InvalidProfileFormatException,
    InvalidCredentialsException,
)
from tests.aws_profiles.conftest import ManagerGenerator


# The moto docs reccomend creating a mocked client as a fixture and providing that to the tests.
# However, the client takes the credentials, which is what we are testing - it would be weird to pass
# this to the ProfileManager instance. Therefore, this fixture is doing the job instead
@pytest.fixture(name="mock_inner_sts_client")
def fixture_mock_inner_sts_client():
    mock = mock_sts()
    mock.start()
    yield
    mock.stop()


@pytest.mark.usefixtures("mock_inner_sts_client")
class TestMockingCredentialTests:  # pylint: disable=too-many-public-methods
    # Misc
    def test_default_profile_is_none(self, profile_manager: ProfileManager):
        assert_that(profile_manager.current_profile, none())

    def test_profiles_is_copy(
        self, populated_profile_manager: ProfileManager, sample_profile_one: Profile
    ):
        profiles = populated_profile_manager.profiles
        # If the profiles object is in essence mutable, ensure it is copied
        if hasattr(profiles, "__delitem__"):
            del profiles[0]  # type: ignore
        assert_that(populated_profile_manager.profiles, equal_to([sample_profile_one]))

    # Test add
    def test_adding_a_profile_adds_correctly(
        self, populated_profile_manager: ProfileManager, sample_profile_one: Profile
    ):
        assert_that(populated_profile_manager.profiles[0], equal_to(sample_profile_one))

    def test_adding_a_profile_sets_default(
        self, populated_profile_manager: ProfileManager, sample_profile_one: Profile
    ):
        assert_that(
            populated_profile_manager.current_profile, equal_to(sample_profile_one)
        )

    # Test selections
    def test_first_profile_is_default(
        self,
        doubly_populated_profile_manager: ProfileManager,
        sample_profile_one: Profile,
    ):
        assert_that(
            doubly_populated_profile_manager.current_profile,
            equal_to(sample_profile_one),
        )

    def test_select_a_profile_selects_away_from_current_selection(
        self,
        doubly_populated_profile_manager: ProfileManager,
        sample_profile_two: Profile,
    ):
        doubly_populated_profile_manager.select(1)
        assert_that(
            doubly_populated_profile_manager.current_profile,
            equal_to(sample_profile_two),
        )

    def test_selecting_outofbounds_raises_key_error(
        self,
        populated_profile_manager: ProfileManager,
    ):
        assert_that(calling(populated_profile_manager.select).with_args(5), raises(KeyError))  # type: ignore

    # Test profile deletion
    def test_can_delete_profile(
        self,
        sample_profile_one: Profile,
        doubly_populated_profile_manager: ProfileManager,
    ):
        doubly_populated_profile_manager.remove(1)
        assert_that(
            doubly_populated_profile_manager.profiles, equal_to([sample_profile_one])
        )

    def test_deleting_current_profile_sets_to_0(
        self, manager_generator: ManagerGenerator
    ):
        large_profile_manager = manager_generator(10)
        large_profile_manager.select(6)
        large_profile_manager.remove(6)
        assert_that(
            large_profile_manager.current_profile,
            equal_to(large_profile_manager.profiles[0]),
        )

    def test_deleting_only_profile_leaves_no_selection(
        self,
        populated_profile_manager: ProfileManager,
    ):
        populated_profile_manager.remove(0)
        assert_that(populated_profile_manager.current_profile, none())

    def test_deleting_lower_profile_decrements_current_profile_for_consistency(
        self, manager_generator: ManagerGenerator
    ):
        large_profile_manager = manager_generator(10)
        large_profile_manager.select(5)
        profile_withid_4 = large_profile_manager.profiles[4]
        assert_that(
            large_profile_manager.current_profile, is_not(equal_to(profile_withid_4))
        )
        large_profile_manager.remove(3)
        profile_withid_4 = large_profile_manager.profiles[4]
        assert_that(large_profile_manager.current_profile, equal_to(profile_withid_4))

    def test_deleting_profile_changes_id_of_higher_ones(
        self, manager_generator: ManagerGenerator
    ):
        large_profile_manager = manager_generator(10)
        large_profile_manager.remove(6)
        expected_ids = list(range(0, 9))
        actual_ids = list(
            map(lambda profile: profile.id_number, large_profile_manager.profiles)
        )
        assert_that(actual_ids, equal_to(expected_ids))

    def test_deleting_last_changes_selected_profile(
        self,
        sample_profile_one: Profile,
        doubly_populated_profile_manager: ProfileManager,
    ):
        doubly_populated_profile_manager.select(1)
        doubly_populated_profile_manager.remove(1)
        assert_that(
            doubly_populated_profile_manager.current_profile,
            equal_to(sample_profile_one),
        )

    def test_deleting_outofbounds_raises_key_error(
        self,
        populated_profile_manager: ProfileManager,
    ):
        assert_that(calling(populated_profile_manager.remove).with_args(5), raises(KeyError))  # type: ignore

    # Test equals
    def test_manager_equals_works(self, manager_generator: ManagerGenerator):
        manager_one = manager_generator(2)
        manager_two = manager_generator(2)
        assert_that(manager_one, equal_to(manager_two))

    def test_manager_equals_fails_if_diff_selected_index(
        self,
        manager_generator: ManagerGenerator,
    ):
        manager_one = manager_generator(2)
        manager_two = manager_generator(2)
        manager_one.select(1)
        assert_that(manager_one, is_not(equal_to(manager_two)))

    def test_manager_equals_fails_if_different_profile_amounts(
        self,
        manager_generator: ManagerGenerator,
    ):
        manager_one = manager_generator(2)
        manager_two = manager_generator(2)
        manager_one.remove(1)
        assert_that(manager_one, is_not(equal_to(manager_two)))

    def test_manager_equals_fails_if_diff_profile_details(
        self,
        manager_generator: ManagerGenerator,
    ):
        manager_one = manager_generator(1)
        manager_two = manager_generator(1)
        access_key = "Some access key"
        secret_access_key = "Some secret access key"
        region = "us-east-1"
        manager_one.add(access_key, secret_access_key, region)
        manager_two.add(f"{access_key}change!", secret_access_key, region)
        assert_that(manager_two, is_not(equal_to(manager_one)))

    # Test save/load
    def test_save_load(
        self, temp_dir_pathlib: Path, populated_profile_manager: ProfileManager
    ):
        populated_profile_manager.save()
        loaded_profile_manager = ProfileManager(temp_dir_pathlib)
        assert_that(loaded_profile_manager, equal_to(populated_profile_manager))

    def test_saving_with_nothing_loads_back_in(
        self, temp_dir_pathlib: Path, profile_manager: ProfileManager
    ):
        profile_manager.save()
        new_profile_manager = ProfileManager(temp_dir_pathlib)
        assert_that(new_profile_manager.profiles, has_length(0))

    def test_loading_missing_selected_profile_raises_error(
        self,
        populated_profile_manager: ProfileManager,
        temp_dir_pathlib: Path,
        expected_json_file: Path,
    ):
        populated_profile_manager.save()
        with open(expected_json_file, mode="rt", encoding="utf-8") as profiles_out:
            json_obj = json.load(profiles_out)
        selected_profile_value = json_obj["selected_profile"]
        del json_obj["selected_profile"]
        json_obj["wrong key name"] = selected_profile_value
        with open(expected_json_file, mode="wt", encoding="utf-8") as profiles_in:
            json.dump(json_obj, profiles_in)
        assert_that(calling(ProfileManager).with_args(temp_dir_pathlib), raises(InvalidProfileFormatException))  # type: ignore

    def test_loading_selected_profile_wrong_type_raises_error(
        self,
        populated_profile_manager: ProfileManager,
        temp_dir_pathlib: Path,
        expected_json_file: Path,
    ):
        populated_profile_manager.save()
        with open(expected_json_file, mode="rt", encoding="utf-8") as profiles_out:
            json_obj = json.load(profiles_out)
        json_obj["selected_profile"] = "Not an integer, that's for sure"
        with open(expected_json_file, mode="wt", encoding="utf-8") as profiles_in:
            json.dump(json_obj, profiles_in)
        assert_that(calling(ProfileManager).with_args(temp_dir_pathlib), raises(InvalidProfileFormatException))  # type: ignore

    @pytest.mark.parametrize(
        "key,bad_type_value",
        [
            ("id_number", "Not an integer"),
            ("access_key", 5),
            ("secret_access_key", 5),
            ("region", 5),
        ],
    )
    def test_loading_profile_with_wrong_type_value_raises_error(  # pylint: disable=too-many-arguments
        self,
        populated_profile_manager: ProfileManager,
        expected_json_file: Path,
        temp_dir_pathlib: Path,
        key: str,
        bad_type_value: Any,
    ):
        populated_profile_manager.save()
        with open(expected_json_file, mode="rt", encoding="utf-8") as profiles_in:
            json_obj = json.load(profiles_in)
        profile = json_obj["profiles"][0]
        profile[key] = bad_type_value
        with open(expected_json_file, mode="wt", encoding="utf-8") as profiles_out:
            json.dump(json_obj, profiles_out)
        assert_that(calling(ProfileManager).with_args(temp_dir_pathlib), raises(InvalidProfileFormatException))  # type: ignore

    def test_error_if_target_is_not_a_dir(self, temp_dir_pathlib: Path):
        new_dir = temp_dir_pathlib / "not_a_dir"
        new_dir.touch()
        assert_that(calling(ProfileManager).with_args(new_dir), raises(NotADirectoryError))  # type: ignore

    def test_stored_at_aws_profiles_json(
        self, temp_dir_pathlib: Path, populated_profile_manager: ProfileManager
    ):
        populated_profile_manager.save()
        expected_data_file = temp_dir_pathlib / "aws_profiles.json"
        assert_that(expected_data_file.exists())


# The following tests test credential validation, so we are not mocking sts


def test_profile_validation_on_add(profile_manager: ProfileManager):
    assert_that(
        calling(profile_manager.add).with_args("Not an access key", "Not a secret access key", "us-east-1"),  # type: ignore
        raises(InvalidCredentialsException),
    )


def test_loading_validates_credentials(
    temp_dir_pathlib: Path, manager_generator: ManagerGenerator
):
    with mock_sts():  # we want to allow the first manager to be created
        profile_manager_one = manager_generator(3)
        profile_manager_one.save()
    # Remove mock, and try loading
    unmocked_profile_manager = ProfileManager(temp_dir_pathlib)
    # We should remove all invalid profiles
    assert_that(unmocked_profile_manager.profiles, has_length(0))
