import random
import json
import pycountry

class Dataset:

  def __init__(self) -> None:
    """
    Initializes a Dataset object.
    Reads the contents of a JSON file and stores it in the `dataset` attribute.

    """
    file_path = '../notebooks/dataset_chat.json'
    with open(file_path, 'r') as file:
      self.dataset = file.readlines()

  def get_random_chat(self) -> tuple[str, str]:
    """
    Returns a random string from the dataset.
    """
    json_string = random.choice(self.dataset)
    json_dict = json.loads(json_string)
    conversation = json_dict['conversation']
    language = self.__get_iso_639(json_dict['language'])
    return conversation, language

  @staticmethod
  def __get_iso_639(language: str) -> str:
      """
      Converts the language name into the ISO 639 string with two letters.

      Args:
        language: The language name.

      Returns:
        The ISO 639 string with two letters.
      """
      try:
        language_code = pycountry.languages.get(name=language).alpha_2
      except AttributeError:
        language_code = ''
      return language_code