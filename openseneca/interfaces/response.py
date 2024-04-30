import requests
from openseneca.utils.logger import Logger
import json

logger = Logger()

class ProviderResponse:

  cost = 0.00  # default cost

  def __init__(self,
      status_code: int = 200,
      headers: dict = None,
      content: str = '{"status": "error", "message": "No content"}',
      cost: float = 0
    ):

    if headers is None:
      headers = {}

    self.status_code = status_code
    self.headers = headers
    self.content = content

    if cost:
      if cost:
        content_json = json.loads(self.content)
        content_json["usage"]["cost"] = cost
        self.content = json.dumps(content_json)

  @staticmethod
  def from_requests_response(response: requests.Response):
    return ProviderResponse(
      response.status_code,
      response.headers,
      response.text
    )


  def print_properties(self):
    logger.info(f"status_code: {self.status_code}")
    logger.info(f"headers: {self.headers}")
    logger.info(f"content: {self.content}")
    logger.info(f"cost: {self.cost}")
