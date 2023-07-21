from aws_profiles.profile import Profile


class InvalidProfileFormatException(Exception):
    """Thrown when the profile JSON file has an invalid format"""

    def __init__(self, further_message: str | None = None) -> None:
        message = "The profiles JSON file has an invalid format!"
        if further_message is not None:
            message += f"\nFurther information {further_message}"
        super().__init__(message)


class InvalidCredentialsException(Exception):
    """Thrown when the user provides incorrect credentials when adding a new profile"""

    def __init__(self, profile: Profile) -> None:
        super().__init__(f"Illegal AWS profile values provided! Profile: {profile}")
