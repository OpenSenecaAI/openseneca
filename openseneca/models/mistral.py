from typing import List, Dict, Any
from openseneca.interfaces.models import (
  ModelBuilder,
  ChatModel,
)


class MistralLargeChatBuilder(ModelBuilder):
  """
  The Builder can do some complex initialization here or transform data
  if needed before passing it to the Model.

  https://learn.microsoft.com/en-gb/azure/ai-studio/how-to/deploy-models-mistral
  """


  def build(self) -> ChatModel:
    return MistralLargeChatModel(
      provider=self.provider,
      temperature=self.temperature,
      top_p=self.top_p,
      max_tokens=self.max_tokens,
    )


class MistralLargeChatModel(ChatModel):
  """
  Represents a chat model for Mistral Large.
  """

  NAME = 'MISTRAL_LARGE_CHAT'

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
