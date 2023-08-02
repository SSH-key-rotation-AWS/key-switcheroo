from aws_profiles import ProfileManager
from switcheroo.paths import app_data_dir


def get_credentials() -> tuple[str, str, str] | None:
    profile_manager = ProfileManager(app_data_dir())
    profile = profile_manager.current_profile
    if profile is not None:
        return (profile.access_key, profile.secret_access_key, profile.region)
    return None
