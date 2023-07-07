class KeyNotFoundException(Exception):
    """Raised when a public key cannot be found for the user.
    
    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="Public key could not be found!"):
        self.message = message
        super().__init__(self.message)
