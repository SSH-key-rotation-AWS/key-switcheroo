class InvalidPathError(Exception):
    """Exception thrown when the user inputs an invalid path

    Attributes:
        message -- explanation of the error
    """
    def __init__(self, path: str, error: Exception) -> None:
        super().__init__(f"Invalid path: {path}\nError: {error}")
