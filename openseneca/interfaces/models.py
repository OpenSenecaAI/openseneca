from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Generator
from openseneca.interfaces.providers import BaseProvider
import os
from typing import List, Dict, Any
from dotenv import load_dotenv
import pkg_resources
from openseneca.interfaces.response import ProviderResponse
load_dotenv()
import yaml

def import_model_settings(model_name) -> dict:
    local_path = os.path.dirname(os.path.abspath(__file__))
    config_file = f'{local_path}/../config.yml'
    if not os.path.exists(config_file):
      config_file = pkg_resources.resource_filename('openseneca', 'config.yml')
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
        if model_name not in config["models"]:
          return config["models"]["_DEFAULT"]['settings']
        return config["models"][model_name]['settings']

class ModelSetupNotFound(Exception):
  """
  Exception raised when the endpoint or bearer token is not found
  during model setup.
  """
  pass

class ModelBuilder(ABC):
  """
  The Model Creator Class is the interface that declares the factory method
  to return a Model Class (e.g. Llama2Model).
  """

  def __init__(
      self,
      provider: BaseProvider,
      temperature: float = 0.0,
      top_p: float = 0.0,
      max_tokens: int = 0,
    ):
    self.provider = provider
    self.temperature = temperature
    self.top_p = top_p
    self.max_tokens = max_tokens

  @abstractmethod
  def build(self) -> Model:
    """
    This method have to be implemented by the concrete creators, build and
    return the Model Class.
    """
    pass


class Model(ABC):
  """
  Represents an AI model.
  """

  NAME = 'MODEL'  # it should be overwritten by the concrete model.

  def __init__(
      self,
      provider: BaseProvider,
      temperature: float = 0.0,
      top_p: float = 0.0,
      max_tokens: int = 0,
    ):
    """
    Initializes a new instance of the Model class.

    Args:
      provider (BaseProvider): The provider object.
      endpoint (str): The endpoint URL.
      bearer_token (str): The bearer token for authentication.

    Raises:
      ModelSetupNotFound: If the endpoint or the bearer_token is empty.

    """
    self.provider = provider
    self.provider.set_llm_name(self.NAME)
    self.endpoint = os.getenv(f'oS__{self.NAME}_ENDPOINT', None)
    self.auth_token = os.getenv(f'oS__{self.NAME}_AUTH', None)
    self.settings = import_model_settings(self.NAME)

    if temperature:
      self.settings['temperature'] = temperature

    if max_tokens:
      self.settings['max_tokens'] = max_tokens

    if top_p:
      self.settings['top_p'] = top_p

    if not self.endpoint or not self.auth_token:
        raise ModelSetupNotFound(
          f"{self.NAME} endpoint or authentication token not found" \
            " in the .env file."
          )

class ChatModel(Model):
  """
  The Product interface declares the operations that all concrete products
  must implement.
  """

  @abstractmethod
  def request(self,
        messages: List[Dict[Any, Any]],
        ) -> Generator[ProviderResponse, None, None]:
    """
    Sends a request with the given messages and returns a response.

    Args:
      messages (List[Dict[Any, Any]]): A list of messages to be sent.

    Returns:
      Generator[ProviderResponse, None, None]: A generator that yields
      ProviderResponse objects.
    """
    pass
