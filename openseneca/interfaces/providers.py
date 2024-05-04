from __future__ import annotations
from abc import ABC, abstractmethod
from openseneca.interfaces.response import ProviderResponse
from typing import Generator

class BaseProvider(ABC):
  """
  Base class for providers (Azure, HF, Google, etc.)
  """

  llm_name = None

  def __init__(
    self,
    stream: bool = False,
    timeout: int = 120
  ):
    """
    Initializes an instance of the Base Provider class.

    Args:
      stream (bool, optional): Whether to enable streaming. Defaults to False.
      timeout (int, optional): The request timeout in seconds. Defaults to 120.
    """
    self.stream = stream
    self.timeout = timeout

  @abstractmethod
  def request(self,
        endpoint: str,
        authentication_header: dict = None,
        body: dict = None,
        content_type: str = 'application/json',
        ) -> Generator[ProviderResponse, None, None]:
    """
    Abstract method for making a request.

    Returns:
      Generator: A generator that yields ProviderResponse objects.
    """
    return ProviderResponse()

  def set_llm_name(self, llm_name: str):
    """
    Sets the name of the LLM.

    Args:
      llm_name (str): The name of the LLM.
    """
    self.llm_name = llm_name