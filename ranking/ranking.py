from math import log
import pandas as pd
import os
from openseneca.utils.logger import Logger
import time
import random

logger = Logger()

class RankedModel:
  """
  Represents a ranking model used in the OpenSeneca project.

  Attributes:
    category_name (str): The name of the category the model belongs to.
    context (bool): Indicates whether the prompt is context-based or not.
    instruction (bool): Indicates whether the prompt is instruction-based.
    language (str): The language of the model.
    is_chat (bool): Indicates whether the model is designed for chat-based interactions.
    top_p (float): The top-p value used for text generation.
    temperature (float): The temperature value used for text generation.
    model_name (str): The name of the model.
    file_name (str): The name of the CSV file used for storing model data.

    			                 game	       								                         player
  | ————————————————————————————————————————————————————|  |————————————————————————————————————————————|
    category_name, language, context, instruction, chat,       model_name, top_p, temperature, elo_score

  """

  # The minimum ELO score for a ranking model.
  # It's set to 100 as USCF uses 100 as the floor for new chess players
  # -- we are insipring from the ELO rating system used in chess.
  ELO_RATING_FLOOR = 100

  def __init__(
    self,
    category_name,
    context,
    instruction,
    language,
    is_chat,
    top_p,
    temperature,
    model_name
  ):
    """
    Initializes a new instance of the RankedModel class.

    Args:
      category_name (str): The name of the category the model belongs to.
      context (bool): Indicates whether the prompt is context-based or not.
      instruction (bool): Indicates whether the prompt is instruction-based.
      language (str): The language of the model.
      is_chat (bool): Indicates whether the model is designed for chat-based interactions.
      top_p (float): The top-p value used for text generation.
      temperature (float): The temperature value used for text generation.
      model_name (str): The name of the model.
    """
    self.category_name = category_name
    self.context = context
    self.instruction = instruction
    self.language = language
    self.is_chat = is_chat
    self.top_p = top_p
    self.temperature = temperature
    self.model_name = model_name
    self.router_file_name = 'table_weights.csv'

  def get_elo_score(self):
    """
    Retrieves the ELO score for the ranking model.

    Returns:
      int: The ELO score of the model.
    """
    try:
      while self.is_locked(self.router_file_name):
        # Wait until the file is unlocked, because
        # the destination file could be empty.
        pass
      df = pd.read_csv(self.router_file_name, encoding="utf-8")
    except FileNotFoundError:
      return self.ELO_RATING_FLOOR

    mask = (
      (df.category_name == self.category_name) &
      (df.context == self.context) &
      (df.instruction == self.instruction) &
      (df.language == self.language) &
      (df.is_chat == self.is_chat) &
      (df.top_p == self.top_p) &
      (df.temperature == self.temperature) &
      (df.model_name == self.model_name)
    )

    if not df[mask].empty:
      return int(df.loc[mask, 'elo_score'].values[0])
    else:
      return self.ELO_RATING_FLOOR

  def store(
    self,
    elo_score,
  ):
    """
    Stores the ELO score for the ranking model.

    Args:
      elo_score (int): The ELO score to be stored.
    """
    _id = self.router_file_name
    while self.is_locked(_id):  # Wait until the file is unlocked
      pass
    self.lock_file(_id)  # Lock the file

    try:
      df = pd.read_csv(_id, encoding="utf-8")
    except FileNotFoundError:
      df = pd.DataFrame(
        columns=[
          'category_name',
          'context',
          'instruction',
          'language',
          'is_chat',
          'top_p',
          'temperature',
          'model_name',
          'elo_score',
        ]
      )

    mask = (
      (df.category_name == self.category_name) &
      (df.context == self.context) &
      (df.instruction == self.instruction) &
      (df.language == self.language) &
      (df.is_chat == self.is_chat) &
      (df.top_p == self.top_p) &
      (df.temperature == self.temperature) &
      (df.model_name == self.model_name)
    )

    if df[mask].empty:
      new_row = {
        'category_name': self.category_name,
        'context': self.context,
        'instruction': self.instruction,
        'language': self.language,
        'is_chat': self.is_chat,
        'top_p': self.top_p,
        'temperature': self.temperature,
        'model_name': self.model_name,
        'elo_score': int(elo_score),
      }
      df = df._append(new_row, ignore_index=True)
    else:
      df.loc[mask, 'elo_score'] = int(elo_score)

    try:
      df = df.sort_values(['category_name', 'elo_score'], ascending=[True, False])
      df['elo_score'] = df['elo_score'].astype(int)
      df.to_csv(self.router_file_name, index=False, encoding='utf-8')
      self.unlock_file(_id)  # Unlock the file
    except Exception as e:
      logger.error(f"Error storing ELO score: {e}")
      self.unlock_file(_id)  # Unlock the file after an error

  def lock_file(self, id: str) -> bool:
    """
    Locks the file to prevent concurrent writes.
    """
    lock_file_path = f".lock_{id}"
    if os.path.exists(lock_file_path):
      return False
    with open(lock_file_path, "w") as lock_file:
      lock_file.write("locked")
      return True

  def is_locked(self, id: str):
    """
    Checks if the file is locked.
    """
    lock_file_path = f".lock_{id}"
    result = os.path.exists(lock_file_path)
    if result:
      logger.info(f"File is locked: {lock_file_path}")
      # Sleep for 0.5 seconds, and retun to check again, probably.
      time.sleep(0.5)
    return result

  def unlock_file(self, id: str):
    """
    Unlocks the file.
    """
    lock_file_path = f".lock_{id}"
    logger.info(f"Unlocking file {lock_file_path}...")
    if os.path.exists(lock_file_path):
      os.remove(lock_file_path)
      logger.info(f"File {lock_file_path} unlocked.")
      # Sleep for a random time between 0.1 and 0.9 seconds.
      time.sleep(random.randint(1, 9) / 10)
      # This to avoid overlapping of lock files/events.

