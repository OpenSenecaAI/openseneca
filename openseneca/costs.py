import yaml
from openseneca.utils.logger import Logger
import os
import pkg_resources
logger = Logger()


class CostCalculator:
  def __init__(self, llm_name):
    self.llm_name = llm_name
    self.prompt_tokens_cost = None
    self.completion_tokens_cost = None
    self.load_costs_from_config()

  def load_costs_from_config(self):
    local_path = os.path.dirname(os.path.abspath(__file__))
    config_file = f'{local_path}/../config.yml'
    if not os.path.exists(config_file):
      config_file = pkg_resources.resource_filename('openseneca', 'config.yml')

    with open(f'{local_path}/config.yml', 'r') as config_file:
      config = yaml.safe_load(config_file)
      llm_config = config.get('models', {}).get(self.llm_name, {})
      if not llm_config:
          llm_config = config.get('models', {}).get('_DEFAULT', {})

      llm_config = config.get('models', {}).get('_DEFAULT', {})
      logger.debug(f"LLM config: {llm_config}")
      self.prompt_tokens_cost = llm_config.get('costs', {}).get('prompt_tokens', 0)
      self.completion_tokens_cost = llm_config.get('costs', {}).get('completion_tokens', 0)
      logger.debug(f"Prompt tokens cost: {self.prompt_tokens_cost}")
      logger.debug(f"Completion tokens cost: {self.completion_tokens_cost}")

  def calculate(self, prompt_tokens, completion_tokens):
    total_cost = (prompt_tokens * self.prompt_tokens_cost/1000) +\
      (completion_tokens * self.completion_tokens_cost/1000)
    return float(total_cost)