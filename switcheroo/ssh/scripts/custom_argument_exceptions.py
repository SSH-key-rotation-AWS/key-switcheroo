class CustomExceptions(Exception):
    """Base class for all custom argparse CLI exceptions"""


class InvalidArgumentError(CustomExceptions):
    """Exception thrown when the user inputs an invalid argument

    Attributes:
        message -- explanation of the error
    """
    def __init__(self, message) -> None:
        super().__init__(message)


class MissingArgumentError(CustomExceptions):
    """Exception thrown when the user doesn't input a required argument

    Attributes:
        message -- explanation of the error
    """
    def __init__(self, message) -> None:
        super().__init__(message)


class InvalidPathError(CustomExceptions):
    """Exception thrown when the user inputs an invalid path

    Attributes:
        message -- explanation of the error
    """
    def __init__(self, path: str) -> None:
        super().__init__(f"Invalid path: {path}")
