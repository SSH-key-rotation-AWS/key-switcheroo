import json
from typing import Sequence, Any
from pathlib import Path
import boto3
from botocore.exceptions import ClientError
from aws_profiles.exceptions import (
    InvalidProfileFormatException,
    InvalidCredentialsException,
)
from aws_profiles.profile import Profile


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
        """The current selected profile. If no profiles are added, this property is None.
        When the first profile is added this property defaults to 0.
        Returns:
            Profile | None: The selected profile, or no profile if none have been added
        """
        if self._selected_profile_index is None:
            return None
        return self._profiles[self._selected_profile_index]

    @staticmethod
    def _validate_profile(profile: Profile):
        cli = boto3.client(  # type: ignore
            "sts",
            aws_access_key_id=profile.access_key,
            aws_secret_access_key=profile.secret_access_key,
            region_name=profile.region,
        )
        try:
            cli.get_caller_identity()
        except ClientError as exc:
            raise InvalidCredentialsException(profile) from exc

    def add(self, access_key: str, secret_acces_key: str, region: str):
        """Adds a profile to the profile manager

        Args:
            access_key (str): The access key
            secret_acces_key (str): The secret access key
            region (str): the region
        """
        last_id = len(self.profiles) - 1
        profile = Profile(last_id + 1, access_key, secret_acces_key, region)
        self._validate_profile(profile)
        self._profiles.append(profile)
        if last_id == -1:  # creating first profile
            self._selected_profile_index = 0

    def _validate_identifier(self, identifier: int):
        if len(self.profiles) == 0 or not 0 <= identifier < len(self._profiles):
            raise KeyError(f"The profile with ID {identifier} does not exist!")

    def remove(self, identifier: int):
        """Removes a profile from the profile manager. 
        If the currently selected profile is removed, the current selected profile defaults to 0,\
        or None if no profiles remain.

        When profiles are removed, their ID's are changed to keep the collection of profiles \
        contiguous. ie for profiles [A,B,C,D,E] with ID [0,1,2,3,4], if C is removed, \
        we end up with [A,B,D,E] with ID [0,1,2,3]. The currently selected profile also \
        changes to keep the selection - in the above example, if D was selected before \
        deleting C, D remains selected after deleting C.

        Args:
            identifier (int): The ID of the profile to remove
        """
        self._validate_identifier(identifier)
        del self._profiles[identifier]
        assert self._selected_profile_index is not None
        if self._selected_profile_index == identifier:
            if identifier == 0:  # We removed the last profile
                self._selected_profile_index = None
            else:  # We removed the selected profile, but profiles still exist
                self._selected_profile_index = 0
        elif (
            self._selected_profile_index > identifier
        ):  # we moved the selected profile down an index
            self._selected_profile_index -= 1
        # All profiles higher up have their identifiers decremented as well
        for i in range(identifier, len(self._profiles)):
            old_profile = self._profiles[i]
            self._profiles[i] = Profile(
                old_profile.id_number - 1,
                old_profile.access_key,
                old_profile.secret_access_key,
                old_profile.region,
            )

    def select(self, identifier: int):
        """Selects a new profile to be the currently selected one

        Args:
            identifier (int): The identifier of the profile to select
        """
        self._validate_identifier(identifier)
        self._selected_profile_index = identifier

    def save(self):
        """Saves the profile to a JSON file, located under the directory passed in when creating \
        this manager. The JSON file is called aws_profiles.json
        """
        if len(self.profiles) == 0:
            return
        json_profiles = list(map(lambda profile: profile.__dict__, self.profiles))
        json_obj = {
            "selected_profile": self._selected_profile_index,
            "profiles": json_profiles,
        }
        with open(self._profiles_path, mode="wt", encoding="utf-8") as profiles_out:
            json.dump(json_obj, profiles_out)

    def _load(self):
        """Loads profiles from a JSON file located under the directory passed in when creating \
        this manager. The JSON file is called aws_profiles.json

        Raises:
            InvalidProfileFormatException: If the JSON format is corrupted
            InvalidProfileFormatException: _description_
        """
        if not self._profiles_path.exists():
            return None
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
        for profile in profiles:
            self._validate_profile(profile)
        self._selected_profile_index = json_obj["selected_profile"]
        self._profiles = profiles
        return True

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ProfileManager):
            return False
        same_index = other._selected_profile_index == self._selected_profile_index
        return same_index and self._profiles == other._profiles
