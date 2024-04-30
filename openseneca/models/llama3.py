from typing import List, Dict, Any
from openseneca.interfaces.models import (
  ModelBuilder,
  ChatModel,
)


class LLama38BChatBuilder(ModelBuilder):
  """
  The Builder can do some complex initialization here or transform data
  if needed before passing it to the Model.

  https://learn.microsoft.com/en-gb/azure/ai-studio/how-to/deploy-models-llama?tabs=azure-studio
  """

  def build(self) -> ChatModel:
    return LLama38BChatModel(
      provider=self.provider,
      temperature=self.temperature,
      top_p=self.top_p,
      max_tokens=self.max_tokens,
    )


class LLama38BChatModel(ChatModel):
  """
  Represents a chat model for llama3.

  Inherits from the ChatModel class.
  """

  NAME = 'LLAMA3_8B_CHAT'

  def request(self,
      messages: List[Dict[Any, Any]],
    ) -> str:

    body = {
      "messages": messages,
      "stop": [
        "### Human",
        "### Assistant",
        "<|eot_id|>",
        "<|start_header_id|>"
      ]
    }

    body.update(self.settings)

    response = self.provider.request(
      endpoint=self.endpoint,
      authentication_header={'Authorization': f'Bearer {self.auth_token}'},
      body=body
    )
    return response


class LLama370BChatBuilder(ModelBuilder):
  """
  The Builder can do some complex initialization here or transform data
  if needed before passing it to the Model.

  https://learn.microsoft.com/en-gb/azure/ai-studio/how-to/deploy-models-llama?tabs=azure-studio
  """

  def build(self) -> ChatModel:
    return LLama370BChatModel(provider=self.provider)


class LLama370BChatModel(ChatModel):
  """
  Represents a chat model for llama3.

  Inherits from the ChatModel class.
  """

  NAME = 'LLAMA3_70B_CHAT'

  def request(self,
      messages: List[Dict[Any, Any]],
    ) -> str:

    body = {
      "messages": messages,
      "stop": [
        "### Human",
        "### Assistant",
        "<|eot_id|>",
        "<|start_header_id|>"
      ]
    }

    body.update(self.settings)

    response = self.provider.request(
      endpoint=self.endpoint,
      authentication_header={'Authorization': f'Bearer {self.auth_token}'},
      body=body
    )
    return response
