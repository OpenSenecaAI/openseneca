from typing import List, Dict, Any
from openseneca.interfaces.models import (
  ModelBuilder,
  ChatModel,
)


class GPT35ChatBuilder(ModelBuilder):
  """
  The Builder can do some complex initialization here or transform data
  if needed before passing it to the Model.

  https://learn.microsoft.com/en-us/azure/ai-services/openai/reference
  """


  def build(self) -> ChatModel:
    return GPT35ChatModel(
      provider=self.provider,
      temperature=self.temperature,
      top_p=self.top_p,
      max_tokens=self.max_tokens,
    )


class GPT35ChatModel(ChatModel):
  """
  Represents a chat model for OpenAI GPT3.X.
  """

  NAME = 'GPT3.5_CHAT_TURBO'

  def request(self,
      messages: List[Dict[Any, Any]],
    ) -> str:

    body = {
      "messages": messages,
    }

    body.update(self.settings)

    response = self.provider.request(
      endpoint=self.endpoint,
      authentication_header={'api-key': self.auth_token},
      body=body
    )
    return response