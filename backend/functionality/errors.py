class ValidationError(Exception):
    """
    An error for when some sort of validation goes wrong
    """
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class DuplicationError(Exception):
    """
    An error for when some sort of duplication is going to occur

    Most particularly used if an item is already in a database
    """
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class AuthorisationError(Exception):
    """
    An error for when some sort of duplication is going to occur

    Most particularly used if an item is already in a database
    """
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
