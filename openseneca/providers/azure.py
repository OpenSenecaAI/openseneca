from math import cos
from openseneca.interfaces.providers import BaseProvider
from openseneca.interfaces.response import ProviderResponse
from openseneca.utils.logger import Logger
from openseneca.costs import CostCalculator
from typing import Generator
import requests
import time
import json

# ----------------------------
# TODO, make this configurable.
# Enable debug output in the http.client module
# http.client.HTTPConnection.debuglevel = 1
# Create a http logger
# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True
# ----------------------------


logger = Logger()

class AzureProvider(BaseProvider):

  def request(self,
         endpoint: str,
         authentication_header: dict = None,
         body: dict = None,
         content_type: str = 'application/json',
         ) -> Generator[ProviderResponse, None, None]:
    """
    Sends a request to the specified endpoint using the specified authentication
    header and body.

    Args:
      endpoint (str): The URL endpoint to send the request to.
      authentication_header (dict, optional): The authentication header
        to include in the request. Defaults to None.
      body (dict, optional): The request body. Defaults to None.
      content_type (str, optional): The content type of the request.
        Defaults to 'application/json'.

    Returns:
      Generator: A generator that yields ProviderResponse objects.

    """
    if body is None:
      body = {}

    if authentication_header is None:
      authentication_header = {}

    headers = {
      'Content-Type': content_type
    }
    stream = self.stream

    headers.update(authentication_header)
    logger.info(f"Is streaming: {stream}")

    if stream:
      body.update({
        "stream": stream
      })

    # Retry the request up to 3 times.
    retry_attempts = 3
    # Wait 10 seconds before retrying, just to try to avoid rate limiting.
    retry_delay = 10

    costs_calulator = CostCalculator(self.llm_name)

    for attempt in range(retry_attempts):
      logger.debug(f"Sending request to {endpoint}")
      logger.debug(f"Body: {body}")
      logger.debug(f"Attempt {attempt + 1} of {retry_attempts}")
      try:

        response = requests.post(
          endpoint,
          json=body,
          headers=headers,
          timeout=self.timeout,
          stream=stream
        )

        if stream:
          json_object = {}
          # Process the response in chunks
          for chunk in response.iter_lines():
            if chunk.startswith(b"data:"):
              json_data = chunk.split(b"data:", 1)[1].strip()
              if len(json_data) > 0:
                try:
                  json_object = json.loads(json_data)
                  if 'choices' in json_object \
                      and 'finish_reason' in json_object['choices'][0] \
                      and json_object['choices'][0]['finish_reason']:
                    if json_object and 'usage' in json_object:
                      _usage = json_object['usage']
                      logger.info(f"Usage: {_usage}")

                      costs = costs_calulator.calculate(
                        _usage['prompt_tokens'],
                        _usage['completion_tokens']
                      )
                      logger.info(f"Costs: {costs}")
                      yield ProviderResponse(
                        200, {}, json.dumps(json_object), cost=costs
                      )
                      break
                  yield ProviderResponse(200, {}, json.dumps(json_object))
                except json.JSONDecodeError:
                  pass  # silence, it's an empty response.
            logger.debug(f"Chunk: {chunk}")
          time.sleep(0.1)

        else:  # not streaming, just return the entire response
          json_object = json.loads(response.text)
          if json_object and 'usage' in json_object:
            _usage = json_object['usage']
            logger.info(f"Usage: {_usage}")

            costs = costs_calulator.calculate(
              _usage['prompt_tokens'],
              _usage['completion_tokens']
            )

            final_response = ProviderResponse(
              response.status_code,
              response.headers,
              response.text,
              cost=costs
            )

          else:
            final_response = ProviderResponse(
              response.status_code,
              response.headers,
              response.text,
            )

          logger.debug(f"Response: {final_response}")
          if 'error' in json.loads(final_response.content):
            logger.error(f"Error in response: {final_response.content}")
            yield ProviderResponse(0, {}, "{}")

          yield final_response
      except requests.exceptions.Timeout:
        if attempt < (retry_attempts - 1):
          logger.error(f"Request timed out. Retrying in {retry_delay}s...")
          time.sleep(retry_delay)
          continue # retry
        else:
          logger.error("Request timed out. No more retries. " \
            "Emitting empty response.")
          yield ProviderResponse(0, {}, "{}")

    return