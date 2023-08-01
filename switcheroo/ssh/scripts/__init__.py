from aws_profiles import ProfileManager
from switcheroo.base import Constants


def get_credentials() -> tuple[str, str, str] | None:
    profile_manager = ProfileManager(Constants.APP_DATA_DIR)
    profile = profile_manager.current_profile
    if profile is not None:
        return (profile.access_key, profile.secret_access_key, profile.region)
    return None
