from openseneca.interfaces.providers import BaseProvider
from openseneca.interfaces.response import ProviderResponse

class DummyProvider(BaseProvider):
  """
  Mock class for testing purposes.
  """
  def request(self,
      endpoint: str,
      authentication_header: dict = None,
      body: dict = None,
      content_type: str = 'application/json',
      ) -> ProviderResponse:
    """
    Implementation of the request method for the mock provider.

    Returns:
      A tuple containing a mock ProviderResponse object and an empty string.
    """
    return ProviderResponse(), ''