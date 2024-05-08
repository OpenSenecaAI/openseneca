import pandas as pd
from openseneca.classify.llm import OpenSenecaLLM
from openseneca.classify.static import StaticOpenSenecaLLMInstance
from langdetect import detect
from openseneca.interfaces.models import Model
from openseneca.utils.inspection import get_model_builder, get_LLMs
from openseneca.utils.logger import Logger
from typing import List, Dict, Any
import pkg_resources

import os
from dotenv import load_dotenv
import os
import time
load_dotenv()
logger = Logger()


class Router:

  default_model = "GPT3.5_CHAT_TURBO"

  # TODO: cheapest model preference.

  def __init__(self, source: str):
    start_time = time.time()
    self.dataframe = pd.read_pickle(source)

    llms = get_LLMs()
    logger.info("LLMS configured: " + str(llms))
    # Filter the dataframe to only include the models in the LLMs list.
    self.dataframe = self.dataframe[self.dataframe['model_name'].isin(llms)]

    end_time = time.time()
    logger.debug("Time to load the router file: "\
      f"{round((end_time - start_time) * 1000, 2)} ms.")

  def get_best(
    self,
    prompt,
  ):
    """
    Returns the best model name based on the given criteria.

    Args:
      category (str): The category of the model.
      language (str): The language of the model.
      context (bool): Whether the model requires context.
      instruction (bool): Whether the model requires instruction.
      is_chat (bool): Whether the model is for chat purposes.

    Returns:
      str: The name of the best model that matches the given criteria.
    """
    filtered_df = self.dataframe[
      (self.dataframe['category_name'] == prompt.label) &
      (self.dataframe['language'] == prompt.language) &
      (self.dataframe['context'] == prompt.is_context_based) &
      (self.dataframe['instruction'] == prompt.is_instructed) &
      (self.dataframe['is_chat'] == prompt.is_chat)
    ]

    try:
      filtered_df = filtered_df.sort_values(by='elo_score', ascending=False)
      best_model = filtered_df.iloc[0]['model_name']
      temperature = filtered_df.iloc[0]['temperature']
      top_p = filtered_df.iloc[0]['top_p']
    except (ValueError, IndexError):
      return self.__get_best_by_language(
        prompt.label,
        prompt.language,
        prompt.is_chat
      )

    return best_model, temperature, top_p

  def __get_best_by_language(
    self,
    category: str,
    language: str,
    is_chat: bool = True,
  ):
    filtered_df = self.dataframe[
        (self.dataframe['category_name'] == category) &
        (self.dataframe['language'] == language) &
        (self.dataframe['is_chat'] == is_chat)
    ]

    try:
      filtered_df = filtered_df.sort_values(by='elo_score', ascending=False)
      best_model = filtered_df.iloc[0]['model_name']
      temperature = filtered_df.iloc[0]['temperature']
      top_p = filtered_df.iloc[0]['top_p']

    except (ValueError, IndexError):
      return self.default_model, 0.7, 0.8
      # return self.__get_best_category_only(category, is_chat)

    return best_model, temperature, top_p

  # def __get_best_category_only(
  #   self,
  #   category: str,
  #   is_chat: bool = True,
  # ):
  #   filtered_df = self.dataframe[
  #       (self.dataframe['category_name'] == category) &
  #       (self.dataframe['is_chat'] == is_chat)
  #   ]

  #   try:
  #     filtered_df = filtered_df.sort_values(by='elo_score', ascending=False)
  #     best_model = filtered_df.iloc[0]['model_name']
  #     temperature = filtered_df.iloc[0]['temperature']
  #     top_p = filtered_df.iloc[0]['top_p']
  #   except (ValueError, IndexError):
  #     return self.default_model, 0.5, 0.92

  #   return best_model, temperature, top_p


router_path = os.path.dirname(os.path.abspath(__file__)) + '/weights.pk'
if not os.path.exists(router_path):
  router_pk_path = pkg_resources.resource_filename('openseneca', 'weights.pk')
router = Router(router_path)

class Prompt:
  messages: List[Dict[Any, Any]]
  user_prompt: str
  language: str
  label: str
  # TODO: context, instruction, is_chat must be set from api params
  #   or autodetected (!?)
  is_context_based: bool = False # TODO
  is_instructed: bool = False  # TODO
  is_chat: bool = True
  best_llm_builder: Model = None
  temp = 0.8
  top_p = 0.9

  def __init__(self, messages: List[Dict[Any, Any]]):

    StaticOpenSenecaLLMInstance\
      .set_instance(OpenSenecaLLM())

    self.messages = messages

    if messages[-1]['role'] != 'user':
      raise Exception("Last message is not from user")

    self.user_prompt = messages[-1]['content']
    self.language = detect(self.user_prompt)
    self.label = StaticOpenSenecaLLMInstance.ollm.get_label(self.user_prompt)
    logger.info(f"Detected language: {self.language}")
    logger.info(f"Detected label: {self.label}")

  def classify(self,):
      best_llm, temp, top_p = router.get_best(self)
      logger.info(f"Best LLM: {best_llm, temp, top_p}")
      best_llm_builder = get_model_builder(best_llm)
      logger.info(f"Builder: {best_llm_builder}")
      self.best_llm_builder = best_llm_builder
      self.temp = temp
      self.top_p = top_p
      return self
