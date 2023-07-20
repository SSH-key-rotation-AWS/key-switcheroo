from dataclasses import dataclass
import json
from typing import Sequence, Any
from pathlib import Path
import boto3
from aws_profiles.exceptions import InvalidProfileFormatException


@dataclass
class Profile:
    id_number: int
    access_key: str
    secret_access_key: str
    region: str


class ProfileManager:
    def __init__(self, profile_data_dir: Path) -> None:
        if profile_data_dir.exists() and not profile_data_dir.is_dir():
            raise NotADirectoryError(
                "The specified AWS profile path is not a directory!"
            )
        profile_data_dir.mkdir(parents=True, exist_ok=True)

        self._profiles_path = profile_data_dir / "aws_profiles.json"
        self._profiles: list[Profile] = []
        self._selected_profile_index: int | None = None
        self._load()

    @property
    def profiles(self) -> Sequence[Profile]:
        return self._profiles.copy()

    @property
    def current_profile(self) -> Profile | None:
        if self._selected_profile_index is None:
            return None
        return self._profiles[self._selected_profile_index]

    @staticmethod
    def validate_profile(profile: Profile):
        cli = boto3.client(
            "sts",
            aws_access_key_id=profile.access_key,
            aws_secret_access_key=profile.secret_access_key,
            region_name=profile.region,
        )
        cli.get_caller_identity()

    def add(self, access_key: str, secret_acces_key: str, region: str):
        last_id = len(self.profiles) - 1
        profile = Profile(last_id + 1, access_key, secret_acces_key, region)
        self._profiles.append(profile)
        if last_id == -1:  # creating first profile
            self._selected_profile_index = 0

    def _validate_identifier(self, identifier: int):
        if not 0 <= identifier < len(self._profiles):
            raise KeyError(f"The profile with ID {identifier} does not exist!")

    def remove(self, identifier: int):
        self._validate_identifier(identifier)
        del self._profiles[identifier]
        if self._selected_profile_index == len(
            self._profiles
        ):  # Now selected index is out of bounds
            self._selected_profile_index = 0
        if len(self._profiles) == 0:  # No profiles left to select
            self._selected_profile_index = None

    def select(self, identifier: int):
        self._validate_identifier(identifier)
        self._selected_profile_index = identifier

    def save(self):
        if len(self.profiles) == 0:
            return
        json_profiles = list(map(lambda profile: profile.__dict__, self.profiles))
        json_obj = {
            "selected_profile": self._selected_profile_index,
            "profiles": json_profiles,
        }
        with open(self._profiles_path, mode="wt", encoding="utf-8") as profiles_out:
            json.dump(json_obj, profiles_out)

    def _load(self) -> bool:
        if not self._profiles_path.exists():
            return False
        with open(self._profiles_path, mode="rt", encoding="utf-8") as profiles_in:
            json_obj = json.load(profiles_in)

        def assert_is(obj: Any, key: str, clas: type | None = None):
            if not key in obj:
                raise InvalidProfileFormatException(f"The key {key} does not exist!")
            if clas is not None and not isinstance(obj[key], clas):
                raise InvalidProfileFormatException(
                    f"The key {key} is of the wrong type!\
                                                    Expected {type}"
                )

        assert_is(json_obj, "selected_profile", int)
        assert_is(json_obj, "profiles", list)

        def parse_profile(profile_obj: Any) -> Profile:
            assert_is(profile_obj, "id_number", int)
            assert_is(profile_obj, "access_key", str)
            assert_is(profile_obj, "secret_access_key", str)
            assert_is(profile_obj, "region", str)
            return Profile(
                profile_obj["id_number"],
                profile_obj["access_key"],
                profile_obj["secret_access_key"],
                profile_obj["region"],
            )

        profiles = list(map(parse_profile, json_obj["profiles"]))
        self._selected_profile_index = json_obj["selected_profile"]
        self._profiles = profiles
        return True

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ProfileManager):
            return False
        same_index = other._selected_profile_index == self._selected_profile_index
        return same_index and self._profiles == other._profiles
