

class DatabaseConnectionError(Exception):
    """Exception raised when the database connection fails."""

    def __init__(self, message="Failed to connect to the database."):
        self.message = message
        super().__init__(self.message)
