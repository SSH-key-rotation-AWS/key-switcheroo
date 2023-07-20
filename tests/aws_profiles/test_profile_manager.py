# pylint: disable = line-too-long
from pathlib import Path
import json
from typing import Any
from hamcrest import assert_that, none, equal_to, raises, calling, is_not  # type: ignore
import pytest
from aws_profiles import Profile, ProfileManager
from aws_profiles.exceptions import InvalidProfileFormatException
from tests.aws_profiles.conftest import ManagerGenerator


# Misc
def test_default_profile_is_none(profile_manager: ProfileManager):
    assert_that(profile_manager.current_profile, none())


def test_profiles_is_copy(
    populated_profile_manager: ProfileManager, sample_profile_one: Profile
):
    profiles = populated_profile_manager.profiles
    # If the profiles object is in essence mutable, ensure it is copied
    if hasattr(profiles, "__delitem__"):
        del profiles[0]  # type: ignore
    assert_that(populated_profile_manager.profiles, equal_to([sample_profile_one]))


# Test add
def test_adding_a_profile_adds_correctly(
    populated_profile_manager: ProfileManager, sample_profile_one: Profile
):
    assert_that(populated_profile_manager.profiles[0], equal_to(sample_profile_one))


def test_adding_a_profile_sets_default(
    populated_profile_manager: ProfileManager, sample_profile_one: Profile
):
    assert_that(populated_profile_manager.current_profile, equal_to(sample_profile_one))


# Test selections
def test_first_profile_is_default(
    doubly_populated_profile_manager: ProfileManager, sample_profile_one: Profile
):
    assert_that(
        doubly_populated_profile_manager.current_profile, equal_to(sample_profile_one)
    )


def test_select_a_profile_selects_away_from_current_selection(
    doubly_populated_profile_manager: ProfileManager, sample_profile_two: Profile
):
    doubly_populated_profile_manager.select(1)
    assert_that(
        doubly_populated_profile_manager.current_profile, equal_to(sample_profile_two)
    )


def test_selecting_outofbounds_raises_key_error(
    populated_profile_manager: ProfileManager,
):
    assert_that(calling(populated_profile_manager.select).with_args(5), raises(KeyError))  # type: ignore


# Test profile deletion
def test_can_delete_profile(
    sample_profile_one: Profile, doubly_populated_profile_manager: ProfileManager
):
    doubly_populated_profile_manager.remove(1)
    assert_that(
        doubly_populated_profile_manager.profiles, equal_to([sample_profile_one])
    )


def test_deleting_last_changes_selected_profile(
    sample_profile_one: Profile, doubly_populated_profile_manager: ProfileManager
):
    doubly_populated_profile_manager.select(1)
    doubly_populated_profile_manager.remove(1)
    assert_that(
        doubly_populated_profile_manager.current_profile, equal_to(sample_profile_one)
    )


def test_deleting_only_profile_leaves_no_selection(
    populated_profile_manager: ProfileManager,
):
    populated_profile_manager.remove(0)
    assert_that(populated_profile_manager.current_profile, none())


def test_deleting_outofbounds_raises_key_error(
    populated_profile_manager: ProfileManager,
):
    assert_that(calling(populated_profile_manager.remove).with_args(5), raises(KeyError))  # type: ignore


# Test equals
def test_manager_equals_works(manager_generator: ManagerGenerator):
    manager_one = manager_generator(2)
    manager_two = manager_generator(2)
    assert_that(manager_one, equal_to(manager_two))


def test_manager_equals_fails_if_diff_selected_index(
    manager_generator: ManagerGenerator,
):
    manager_one = manager_generator(2)
    manager_two = manager_generator(2)
    manager_one.select(1)
    assert_that(manager_one, is_not(equal_to(manager_two)))


def test_manager_equals_fails_if_different_profile_amounts(
    manager_generator: ManagerGenerator,
):
    manager_one = manager_generator(2)
    manager_two = manager_generator(2)
    manager_one.remove(1)
    assert_that(manager_one, is_not(equal_to(manager_two)))


def test_manager_equals_fails_if_diff_profile_details(
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
def test_save_load(temp_dir_pathlib: Path, populated_profile_manager: ProfileManager):
    populated_profile_manager.save()
    loaded_profile_manager = ProfileManager(temp_dir_pathlib)
    assert_that(loaded_profile_manager, equal_to(populated_profile_manager))


def test_saving_with_nothing_does_nothing(
    expected_json_file: Path, profile_manager: ProfileManager
):
    profile_manager.save()
    assert_that(not expected_json_file.exists())


def test_loading_missing_selected_profile_raises_error(
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
def test_loading_profile_with_wrong_type_value_raises_error(
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


def test_error_if_target_is_not_a_dir(temp_dir_pathlib: Path):
    new_dir = temp_dir_pathlib / "not_a_dir"
    new_dir.touch()
    assert_that(calling(ProfileManager).with_args(new_dir), raises(NotADirectoryError))  # type: ignore


def test_stored_at_aws_profiles_json(
    temp_dir_pathlib: Path, populated_profile_manager: ProfileManager
):
    populated_profile_manager.save()
    expected_data_file = temp_dir_pathlib / "aws_profiles.json"
    assert_that(expected_data_file.exists())
