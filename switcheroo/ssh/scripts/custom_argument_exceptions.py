class InvalidArgumentError(Exception):
    """Exception thrown when the user inputs an invalid argument

    Attributes:
        message -- explanation of the error
    """
    def __init__(self, message) -> None:
        super().__init__(message)


class MissingArgumentError(Exception):
    """Exception thrown when the user doesn't input a required argument

    Attributes:
        message -- explanation of the error
    """
    def __init__(self, message) -> None:
        super().__init__(message)
