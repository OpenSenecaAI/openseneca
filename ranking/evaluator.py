from ast import Tuple
import re
from unittest import result
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage
from langchain.evaluation import load_evaluator
from langchain.evaluation import EvaluatorType
import os
from typing import Union
from langchain.evaluation.schema import StringEvaluator
from langchain.chains.base import Chain
from typing import Callable, Literal
from dotenv import load_dotenv
from openseneca.interfaces.models import Model
from openseneca.utils.logger import Logger
from typing import Tuple
import json
import concurrent.futures
load_dotenv()
logger = Logger()

judging_timeouts = 90

assert os.environ.get("AZURE_OPENAI_API_KEY") is not None, \
    "Please set AZURE_OPENAI_API_KEY environment variable"
assert os.environ.get("AZURE_OPENAI_ENDPOINT") is not None, \
    "Please set AZURE_OPENAI_ENDPOINT environment variable"

class EmptyResponseException(Exception):
  """
  Exception raised when an empty response is received.
  """
  pass

template = """
Assistant A:
{result_a}

-------

Assistant B:
{result_b}"""

def generate(text, model: Model) -> str:
  """
  Generate content based on the given text using the given model.

  Args:
    text (str): The input text to generate content from.
    model (Model): The model to use for generating content.

  Returns:
    str: The generated content.

  """
  result = model.request(
    [{"role": "user", "content": text}]
  )

  result_dict = json.loads(next(result).content)
  # next(result.content) is a generator

  logger.debug(result_dict)
  if "choices" not in result_dict:
    raise EmptyResponseException("Empty response received")
  else:
    content = result_dict["choices"][0]["message"]["content"].strip()
    return content

class EvaluationResult:
  result: bool      # True if the evaluation passed, False otherwise
  response_a: str   # The result from model A
  response_b: str   # The result from model B
  reasoning: str    # The reasoning behind the evaluation.

  def __init__(
    self,
    result: bool,
    response_a: str,
    response_b: str,
    reasoning: str
  ):
    self.result = result
    self.response_a = response_a
    self.response_b = response_b
    self.reasoning = reasoning

class Evaluator:
  """
  The Evaluator class represents an evaluator used for model evaluation.

  """

  def create(
    self,
    evaluation_llm: AzureChatOpenAI,
    generate: Callable[[str], str] = generate,
    evaluator_type: Literal[
      "qa",
      "cot_qa",
      "criteria",
      "string_distance",
      "score_string",
      "context_qa",
    ] = EvaluatorType.CRITERIA,
    criteria_description: str = "conciseness",
  ) -> Union[Chain, StringEvaluator]:
    """
    Create a new evaluator.

    Args:
      evaluation_llm (AzureChatOpenAI): The LLM used for evaluation.
      generate (Callable[[str], str]): The function used for generating predictions.
      evaluator_type (Literal): The type of evaluator to create.
        Defaults to EvaluatorType.CRITERIA.

    Returns:
      Union[Chain, StringEvaluator]: The created evaluator.
    """
    self.evaluator = load_evaluator(
      evaluator_type,
      criteria=criteria_description,
      llm=evaluation_llm
    )

    self.generate_fn = generate

  def evaluate(self,
               message: HumanMessage,
               model_a: Model,
               model_b: Model,
               ) -> Tuple[bool, str, str, str]:
    """
    Evaluate a message using the evaluator.

    Args:
      message (HumanMessage): The message to evaluate.
    """

    result_a = self.generate_fn(message.content, model=model_a)
    result_b = self.generate_fn(message.content, model=model_b)

    if not result_a or not result_b:
      raise EmptyResponseException("Empty response received")

    result = template.format(result_a=result_a, result_b=result_b)
    logger.debug(result)

    try:
      # This because the evaluation through gpt-4 or bigger models sometimes
      # takes long time to response and evaluate the result. It seems that
      # when it happens the script stuck and the evaluation never ends.
      # So, we are using ThreadPoolExecutor to limit the time of the evaluation
      # and take control of the evaluation time.
      with concurrent.futures.ThreadPoolExecutor() as executor:
        logger.info("Judging...")
        future = executor.submit(
          self.evaluator.evaluate_strings,
          prediction=result,
          input=message.content
        )
        eval_result = future.result(timeout=judging_timeouts)
    except concurrent.futures.TimeoutError:
      raise Exception(f"Evaluation took longer than {judging_timeouts}s.")

    logger.info(eval_result)

    return EvaluationResult(
      result=bool(eval_result["score"]),
      response_a=result_a,
      response_b=result_b,
      reasoning=eval_result["reasoning"]
    )

