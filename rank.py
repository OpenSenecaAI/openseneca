from openseneca.providers.azure import AzureProvider
from openseneca.utils.logger import Logger
from ranking.dataset import Dataset
from ranking.battle import Game
import threading
import os
import traceback

logger = Logger()

MAX_GAMES_PER_THREAD = 1024
THREADS = 8

# Define a function that will be executed in each thread
def run_game():
  """
  Runs the game loop until the maximum number of games is reached.

  The function starts a new game and plays multiple rounds until the maximum
  number of games per thread is reached. If an error occurs during the game,
  the function restarts the game and continues the loop.
  """
  while True:
    logger.info("Starting a new game...")
    try:
      dataset = Dataset()
      game = Game(k_factor=32, provider=AzureProvider())
      for i in range(1, MAX_GAMES_PER_THREAD + 1):
        prompt, language = dataset.get_random_chat()
        game.play(prompt=prompt, language=language)
      break  # if no errors occurred, exit the loop
    except Exception as e:
      # If an error occurred, restart the game (continuing the while loop)
      traceback.print_exc()
      logger.error(f"An error occurred: {e}. Restarting...")

def delete_lock_files():
  """
  Deletes all lock files in the specified directory.

  This function iterates over all files in the directory and deletes any file
  that starts with '.lock_'. It logs the path of each deleted lock file.

  Args:
    None

  Returns:
    None
  """
  current_path = os.path.dirname(os.path.abspath(__file__))
  for filename in os.listdir(current_path):
    if filename.startswith('.lock_'):
      file_path = os.path.join(current_path, filename)
      logger.info(f"Deleting lock file: {file_path}")
      os.remove(file_path)
      logger.info(f"Lock file deleted: {file_path}")

# Main
try:

  # Create three threads
  threads = []
  for _ in range(THREADS):
    thread = threading.Thread(target=run_game)
    thread.start()
    threads.append(thread)

  # Wait for all threads to finish
  for thread in threads:
    thread.join()

# Handle keyboard interrupts, and delete lock files
# (delete_lock_files() function).
except KeyboardInterrupt:
  delete_lock_files()
