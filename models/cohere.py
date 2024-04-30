from openseneca.interfaces.models import (
  ModelBuilder,
  ChatModel,
)
from typing import List, Dict, Any


class CohereCommandRChatBuilder(ModelBuilder):
  """
  The Builder can do some complex initialization here or transform data
  if needed before passing it to the Model.

  https://learn.microsoft.com/en-gb/azure/ai-studio/how-to/deploy-models-cohere-command
  """


  def build(self) -> ChatModel:
    return CohereCommandRChatModel(
      provider=self.provider,
      temperature=self.temperature,
      top_p=self.top_p,
      max_tokens=self.max_tokens,
    )


class CohereCommandRChatModel(ChatModel):
  """
  Represents a chat model for Mistral Large.
  """

  NAME = 'COHERE_COMMAND_R_CHAT'

  def request(self,
      messages: List[Dict[Any, Any]],
    ) -> str:

    body = {
      "messages": messages,
    }

    body.update(self.settings)

    response = self.provider.request(
      endpoint=self.endpoint,
      authentication_header={'Authorization': f'Bearer {self.auth_token}'},
      body=body
    )
    return response


class CohereCommandRPlusChatBuilder(ModelBuilder):
  """
  The Builder can do some complex initialization here or transform data
  if needed before passing it to the Model.

  https://learn.microsoft.com/en-gb/azure/ai-studio/how-to/deploy-models-cohere-command
  """


  def build(self) -> ChatModel:
    return CohereCommandRPlusChatModel(provider=self.provider)


class CohereCommandRPlusChatModel(ChatModel):
  """
  Represents a chat model for Mistral Large.
  """

  NAME = 'COHERE_COMMAND_R_PLUS_CHAT'

  def request(self,
      messages: List[Dict[Any, Any]],
    ) -> str:

    body = {
      "messages": messages,
    }

    body.update(self.settings)

    response = self.provider.request(
      endpoint=self.endpoint,
      authentication_header={'Authorization': f'Bearer {self.auth_token}'},
      body=body
    )
    return response