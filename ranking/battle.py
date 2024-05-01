from openseneca.interfaces.models import Model
from openseneca.interfaces.providers import BaseProvider
from openseneca.providers.azure import AzureProvider
from langchain_openai import AzureChatOpenAI
from openseneca.utils.logger import Logger
from openseneca.utils.inspection import get_model_builder, get_LLMs
from langchain_core.messages import HumanMessage, SystemMessage
from ranking.evaluator import Evaluator, EmptyResponseException
from langchain.evaluation import EvaluatorType
from typing import Tuple
from openseneca.interfaces.models import ModelBuilder
from openseneca.models.gpt4 import GPT4ChatModel
from openseneca.classify.llm import OpenSenecaLLM
import random
import os
import openai
from abc import ABC
from ranking.ranking import RankedModel

logger = Logger()

THE_BEST_MODEL_TO_FIGHT = GPT4ChatModel.NAME
# TODO. Need to move it to the orchestrator.

custom_criterion = {
  "High-quality and correct A response": \
      "Is answer A a high quality answer compared to answer B, in terms of " \
      "the quality and correctness of the answer and language property? " \
      "It's important to consider that the answer must be in the same " \
      "language of the prompt, and the answer must be correct and high " \
      "quality.\nIs it aligned with the answer that can be expected? [S|N]",
}

custom_criterion = {
  "Does Assistant A win?": "Two AI Assistants generated these responses, Assistant A and Assistant B. Which one has a better answer? Analyze their answers in terms of correctness, quality, language property, and negatively evaluate redundancy. Answer Yes if you think the winner is Assistant A's first answer. In the game, does Assistant A win?"
}

category_instructions = """
category_names = [ {categories} ]
Following the list above, respond to the message prompt simply with the corresponding category.
Pay attention to the text_greetings category, which is a special category that includes greetings, goodbyes, and other similar messages. But remember, it has to include only greetings and not other types of requests or questions. Otherwise, it will be considered another category.
DO NOT answer with a sentence, just the category_name!
"""

categories_set = {'text_greetings', 'language_translation', 'creative_writing', 'data_analysis', 'code_python', 'code_generation', 'math_equation', 'code_javascript', 'history_analysis', 'text_poetry', 'health_advice', 'technology_analysis', 'psychology_analysis', 'artificial_intelligence', 'customer_service', 'software_development', 'philosophical_question', 'psychology_study', 'text_summary', 'code_c++', 'technology_management', 'history_search', 'psychology_management', 'business_management', 'market_analysis', 'sports_analysis', 'technology_practice', 'travel_advice', 'technology_review', 'math_solution', 'code_java', 'philosophy_analysis', 'business_practice', 'business_solution', 'technology_introduction', 'education_advice', 'public_relations', 'politics_analysis', 'code_sql', 'crafting_ideas', 'fact_checking', 'mystery_solving', 'place_theory', 'business_advice', 'parenting_advice', 'business_introduction', 'technology_advice', 'animal_explanation', 'health_search', 'history_management', 'technology_exploration', 'text_riddle', 'education_tutorial', 'text_tutorial', 'sports_introduction', 'science_study', 'computer_programming', 'content_creation', 'history_theory', 'philosophy_history', 'place_exploration', 'relationship_guidance', 'history_introduction'}

class GameAbstract(ABC):

  def print_attributes(self):
    """
    Prints the attributes of the GameSettings object.
    """
    attributes = vars(self)
    for attribute, value in attributes.items():
      print(f"{attribute}: {value}")

class GameSettings(GameAbstract):
  """
  Represents the settings for a game.

  Attributes:
    category_name (str): The name of the category for the prompt
      (e.g: 'text_greetings', 'language_translation', etc.)
    is_context_based (bool): Indicates whether the prompt is context-based.
    language (str): The language used in the prompt.
    is_chat (bool): Indicates whether the prompt is a chat prompt,
      or a completion prompt.
  """

  category_name: str
  is_context_based: bool
  is_instruction_based: bool
  language: str
  is_chat: bool

  def __init__(
    self,
    category_name: str,
    is_context_based: bool,
    is_instruction_based: bool,
    language: str,
    is_chat: bool,
  ):
    self.category_name = category_name
    self.is_context_based = is_context_based
    self.is_instruction_based = is_instruction_based
    self.language = language
    self.is_chat = is_chat

class Player(GameAbstract):
  """
  Represents a player in the game.

  Attributes:
    builder (ModelBuilder): The model builder for the player.
    top_p (float): The top-p value for the player.
    temperature (float): The temperature value for the player.
  """

  model: Model
  top_p: float
  temperature: float

  def __init__(
    self,
    model: Model,
    top_p: float,
    temperature: float
  ):
    self.model = model
    self.top_p = top_p
    self.temperature = temperature

class Game:

  game_number: int = 0
  players: Tuple[Model, Model] = None

  def __init__(
    self,
    k_factor=32,
    provider: BaseProvider = AzureProvider()
  ) -> Tuple[Model, Model]:
    self.k_factor = k_factor
    self.provider = provider
    self.llm_base_client = AzureChatOpenAI(
        openai_api_version="2023-05-15",
        azure_deployment=os.environ.get("oS__GPT4_DEPLOYMENT"),
      )

    self.llm_category_client = AzureChatOpenAI(
        openai_api_version="2023-05-15",
        azure_deployment=os.environ.get("oS__GPT3.5_DEPLOYMENT"),
      )

    self.evaluator = Evaluator()
    self.evaluator.create(
      evaluation_llm=self.llm_base_client,
      evaluator_type=EvaluatorType.CRITERIA,
      criteria_description=custom_criterion
    )

    self.llmclassifier = OpenSenecaLLM()

  def play(self, prompt: str = None, language: str = None):

    if prompt is None:
      raise Exception("The prompt must be defined.")

    if language is None:
      raise Exception("The language must be defined.")

    # Increment the game number
    self.game_number += 1

    logger.info(f"Game {self.game_number} started.")

    logger.debug(prompt)
    category = self.get_category(
      prompt,
      use_local_llm=True,
    )
    logger.info(f"Category: {category}")

    # I know, it's a bit of a hack, but it's a good one, we have too many
    # greetings prompts, and we don't need to evaluate them all, so we skip.
    if random.randint(0, 2) > 0 and category == "text_greetings":
      logger.info("Skipping the game because the category is text_greetings " \
                  "and the dice roll is not in favor :)")
      return

    message = HumanMessage(prompt)

    # Define the game environment variables
    gs = GameSettings(
      category_name=category,
      is_context_based=self.is_context_based(message),
      is_instruction_based=self.is_instruction_based(message),
      language=language,
      is_chat=True,  # default is chat, for now -- completetion coming soon.
    )

    sub_games = 6

    for i in range(1, sub_games+1):
      # Select two random players from llms
      self.__get_players()
      logger.info(f"Players: {self.players}")
      logger.info(f"Sub-game {i} started.")

      sub_sub_games = 8
      for i in range(1, sub_sub_games+1):

        logger.info(f"Sub^2-game {i} started.")

        player_a = Player(
          model=self.players[0],
          top_p=self.random_top_p(),
          temperature=self.random_temperature(),
        )

        player_b = Player(
          model=self.players[1],
          top_p=self.random_top_p(),
          temperature=self.random_temperature(),
        )

        if player_a.model == player_b.model \
          and player_a.top_p == player_b.top_p \
          and player_a.temperature == player_b.temperature:
          logger.warning("Player A is identical to Player B. " \
            "Skipping to the next step in the loop.")
          continue  # < Skip to the next step in the loop

        gs.print_attributes()
        player_a.print_attributes()
        player_b.print_attributes()

        player_a.model.settings["top_p"] = player_a.top_p
        player_a.model.settings["temperature"] = player_a.temperature

        player_b.model.settings["top_p"] = player_b.top_p
        player_b.model.settings["temperature"] = player_b.temperature

        try:
          eva = self.evaluator.evaluate(
            message,
            model_a=player_a.model,
            model_b=player_b.model
          )
        except EmptyResponseException as exc:
          logger.error(str(exc))
          logger.info('Skipping the game...')
          return

        r = eva.result

        """
        Notes.

          (r) is the result of the evaluation. It's a boolean value.
          If True, the answer A is a high quality and correct.

          The goal is to compare the quality of the two answers, but not directly,
          just to check if the answer A is suitable for the given question with
          the right quality and correctness.

          In other words, It's a different way to make a battle between two
          models, because this not measures if the Answer A or Answer B wins or
          loses on the other, but if simple the Answer A is a good answer or not.

          Why this? Because the goal of the ranking is to find the best model for
          the given question, and make it possible to save computational
          resources. If we can answer the question completely with the cheaper
          model, why use the more expensive one (such as gpt-4)?

        """
        winner_model = self.players[0].NAME if r is True else self.players[1].NAME
        logger.info('The winner model is: ' + winner_model)

        a = RankedModel(
          category_name=gs.category_name,
          context=gs.is_context_based,
          instruction=gs.is_instruction_based,
          language=gs.language,
          is_chat=gs.is_chat,
          top_p=player_a.top_p,
          temperature=player_a.temperature,
          model_name=player_a.model.NAME
        )

        b = RankedModel(
          category_name=gs.category_name,
          context=gs.is_context_based,
          instruction=gs.is_instruction_based,
          language=gs.language,
          is_chat=gs.is_chat,
          top_p=player_b.top_p,
          temperature=player_b.temperature,
          model_name=player_b.model.NAME
        )

        logger.info('Calculating ELO scores...')
        player_a_elo_score = self.calculate_elo_score(
          a.get_elo_score(),
          b.get_elo_score(),
          result=1 if r is True else 0
        )
        logger.info(f"Player A ELO score: {player_a_elo_score}")

        player_b_elo_score = self.calculate_elo_score(
          b.get_elo_score(),
          a.get_elo_score(),
          result=1 if r is False else 0
        )
        logger.info(f"Player B ELO score: {player_b_elo_score}")

        a.store(elo_score=player_a_elo_score)
        b.store(elo_score=player_b_elo_score)

        logger.info(f"Game {i}/{sub_games}/{sub_sub_games} "\
          f"[{self.game_number}] ended.\n"\
          "---------------------------------\n"
          "Recap:\n"\
          "---------------------------------\n"
          "Prompt: " + prompt[:64] + "\n"\
          f"Winner: {winner_model}\n"\
          f"Player A: {player_a.model.NAME} - ELO score: {player_a_elo_score}\n"\
          f"Player B: {player_b.model.NAME} - ELO score: {player_b_elo_score}\n"\
          "---------------------------------"
        )


  def __get_players(self):
    # Select two random players from llms
    llms = get_LLMs()
    logger.info(f"LLMs: {llms}")

    # Select the first player randomly except the best model, then
    # select the second player randomly from all models.
    # player1_name = random.choice(
    #   [llm for llm in llms if llm != THE_BEST_MODEL_TO_FIGHT]
    # )

    player1_name = random.choice(llms)

    # Second player from all models except the first player.
    player2_name = random.choice([llm for llm in llms if llm != player1_name])

    # Get the model builders for the selected players
    builder_a = get_model_builder(player1_name)
    builder_b = get_model_builder(player2_name)

    # Build the models (aka players)
    player1 = builder_a(self.provider).build()
    player2 = builder_b(self.provider).build()

    # Return the players to the class attribute
    self.players = (player1, player2)

  def get_category(
    self,
    prompt: str,
    category_set: set = None,
    add_instruction: str = "",
    force_llm: AzureChatOpenAI = None,
    use_local_llm = False
  ):

    if use_local_llm:
      label = self.llmclassifier.get_label(prompt)
      return label

    if category_set is None:
      raise Exception("The category set must be defined.")

    instruction_string = category_instructions.format(
        categories=", ".join(category_set)
      ).strip()

    if add_instruction:
      instruction_string += '\n' + add_instruction.strip()

    instruction = SystemMessage(
      content=instruction_string
    )

    message = HumanMessage(
      content=prompt.strip(),
    )

    __model = force_llm if force_llm else self.llm_category_client

    try:
      category = __model(
        [instruction, message],
        temperature=0.7,
        top_p=0.1,
      )
    except openai.BadRequestError as e:
      # Bad request error, probably the prompt is violating the API rules
      # (policy, etc.), so we log the error and return 'unknown'.
      logger.error(f"Bad request error: {str(e)}")
      return "unknown"
    except Exception as e:
      # Log the error and return 'unknown'
      logger.error(str(e))
      return "unknown"

    if "_" not in category.content or len(category.content) > 50:
      return "unknown"

    return category.content

  def is_context_based(
    self,
    prompt: HumanMessage,
    force_llm: AzureChatOpenAI = None
    ) -> bool:
    query = "Answer with either 0 or 1, where 0 means FALSE: the prompt is "\
      "not based on a context and factual data included in the same message," \
      "or 1, which means TRUE: the prompt contains a context on which the " \
      "question is based and in which relevant data and facts are contained " \
      "for use in answering the prompt.\n" \
      "Just answer with 0 or 1, and nothing else."

    instruction = SystemMessage(content=query)

    __model = force_llm if force_llm else self.llm_category_client
    try:
      context = __model(
          [instruction, prompt],
          temperature=0.7,
          top_p=0.1,
        )
    except openai.BadRequestError as e:
      # Bad request error, probably the prompt is violating the API rules
      # (policy, etc.), so we log the error and return 'unknown'.
      logger.error(f"Bad request error: {str(e)}")
      return 0
    except Exception as e:
      # Log the error and return 'unknown'
      logger.error(str(e))
      return 0

    if not context.content.isdigit():
      return False
    return bool(int(context.content))

  def is_instruction_based(
    self,
    prompt: HumanMessage,
    force_llm: AzureChatOpenAI = None
    ) -> bool:
    query = "Answer 0 or 1, where 0 means FALSE: the query is not based "\
      "on an instruction given by the user, such as \"you are an artificial " \
      "intelligence impersonating, and blah blah blah,\" or 1, which means " \
      "TRUE: the query contains a very specific instruction that gives " \
      "guidance to the AI as to what it needs to do in order to give an " \
      "answer to the prompt, for example \"Pretend you are a programmer, " \
      "a writer\", and so on... Simply write 0 or 1, and nothing else, in " \
      "response to this question: Is the prompt instruction-based?"

    instruction = SystemMessage(content=query)

    __model = force_llm if force_llm else self.llm_category_client
    try:
      context = __model(
          [instruction, prompt],
          temperature=0.7,
          top_p=0.1,
        )
    except openai.BadRequestError as e:
      # Bad request error, probably the prompt is violating the API rules
      # (policy, etc.), so we log the error and return 'unknown'.
      logger.error(f"Bad request error: {str(e)}")
      return 0
    except Exception as e:
      # Log the error and return 'unknown'
      logger.error(str(e))
      return 0

    if not context.content.isdigit():
      return False
    return bool(int(context.content))


  def __elo_expected_score(self, player_a_elo: int, player_b_elo: int) -> float:
    result = 1 / (1 + 10 ** ((player_b_elo - player_a_elo) / 400))
    logger.info(f"Expected score: {result}")
    return result

  def calculate_elo_score(
    self,
    player_elo: int,
    opponent_elo: int,
    result: int
  ) -> int:
    """
    Calculates the updated Elo score for a player after a battle.

    Args:
      player_elo (int): The current Elo score of the player.
      opponent_elo (int): The current Elo score of the opponent.
      result (int): The result of the battle.
        1 for a win, 0 for a loss.

    Returns:
      int: The updated Elo score of the player after the battle.
    """
    return int(player_elo + self.k_factor * \
      (result - self.__elo_expected_score(player_elo, opponent_elo)))

  def random_top_p(self):
    return random.choice([0.25, 0.5, 0.8, 0.9])

  def random_temperature(self):
    return random.choice([0.5, 0.75, 0.9])