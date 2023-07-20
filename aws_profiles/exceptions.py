class InvalidProfileFormatException(Exception):
    """Thrown when the profile JSON file has an invalid format"""

    def __init__(self, further_message: str | None = None) -> None:
        message = "The profiles JSON file has an invalid format!"
        if further_message is not None:
            message += f"\nFurther information {further_message}"
        super().__init__(message)
