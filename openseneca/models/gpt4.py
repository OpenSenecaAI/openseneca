from typing import List, Dict, Any
from openseneca.interfaces.models import (
  ModelBuilder,
  ChatModel,
)



class GPT4ChatBuilder(ModelBuilder):
  """
  The Builder can do some complex initialization here or transform data
  if needed before passing it to the Model.

  https://learn.microsoft.com/en-us/azure/ai-services/openai/reference
  """


  def build(self) -> ChatModel:
    return GPT4ChatModel(
      provider=self.provider,
      temperature=self.temperature,
      top_p=self.top_p,
      max_tokens=self.max_tokens,
    )


class GPT4ChatModel(ChatModel):
  """
  Represents a chat model for OpenAI GPT4.X.
  """

  NAME = 'GPT4_CHAT'

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
