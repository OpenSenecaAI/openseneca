import inspect
import importlib
import os
from openseneca.interfaces.models import ModelBuilder
from openseneca.utils.logger import Logger

logger = Logger()


class ModelBuilderNotFound(Exception):
  """
  Exception raised when the model or its builder is not found.
  """
  pass


def get_model_builder(name) -> ModelBuilder:
  """
  Retrieves the model builder class for a given model name.

  Args:
    name (str): The name of the model.

  Returns:
    ModelBuilder: The model builder class corresponding to the given model name.

  Raises:
    ModelBuilderNotFound: If the model builder class is not found for
      the given model name.
  """
  module = importlib.import_module('openseneca.models')
  for _, cls in inspect.getmembers(module, inspect.isclass):
    if hasattr(cls, 'NAME'):
      print(getattr(cls, 'NAME'))
    if hasattr(cls, 'NAME') and getattr(cls, 'NAME') == name:
      builder_class_name = cls.__name__.replace('Model', 'Builder')
      builder_class = getattr(module, builder_class_name, None)
      if builder_class is not None:
        return builder_class
  err = f"Model builder not found for model {name}"
  logger.error(err)
  raise ModelBuilderNotFound(err)


def get_LLMs():
  """
  Retrieves the LLMs (Logical Link Monitors) from the environment variables and
    returns them sorted alphabetically.

  Returns:
    list: A sorted list of LLMs (Logical Link Monitors).
  """
  os_vars = {
    key: value
    for key, value in os.environ.items()
    if key.startswith("oS__")
  }

  LLMs = set()
  for key, value in os_vars.items():
    if key.endswith("_ENDPOINT") or key.endswith("_AUTH"):
      name = key.split("__")[1].replace("_ENDPOINT", "").replace("_AUTH", "")
      LLMs.add(name)

  # Sort the LLMs by name (A-Z)
  LLMs = sorted(LLMs)

  return LLMs
