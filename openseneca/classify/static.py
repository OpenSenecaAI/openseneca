from torch import nn


class StaticOpenSenecaLLMInstance:
  ollm = None

  @staticmethod
  def set_instance(instance: nn.Module):
    """
    Sets the instance of the OpenSenecaLLM model.

    Args:
      instance (nn.Module): The instance of the OpenSenecaLLM model to be set.

    """
    if StaticOpenSenecaLLMInstance.ollm is None:
      StaticOpenSenecaLLMInstance.ollm = instance
