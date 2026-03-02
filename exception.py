
class GetCredentialsException(Exception):
  """Error raised when an error occurred while retrieving credentials.

  Attributes:
    authorization_url: Authorization URL to redirect the user to in order to
                      request offline access.
  """
  def __init__(self, authorization_url: str):
    """Construct a GetCredentialsException."""
    super().__init__(f"Authorization URL: {authorization_url}")
    self.authorization_url: str = authorization_url

class CodeExchangeException(GetCredentialsException):
    """Error raised when a code exchange has failed."""
    pass

class NoRefreshTokenException(GetCredentialsException):
    """Error raised when no refresh token has been found."""
    pass

class NoUserIdException(Exception):
    """Error raised when no user ID could be retrieved."""
    pass

class FlowExchangeError(Exception):
    """Error raised when a code exchange has failed."""
    pass
