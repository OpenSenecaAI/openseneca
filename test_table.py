# Code to test the consinstency of the table where all the ranking models are stored.
from ranking.ranking import RankedModel

test_model = RankedModel(
  category_name='text_greetings',
  context=False,
  instruction=False,
  language='en',
  is_chat=True,
  top_p=0.9,
  temperature=0.75,
  model_name='GPT3.5_CHAT_TURBO'
)

print(" - Test model Class:", end=" "  )
print(test_model)
print(" - Test model ELO Score:", end=" ")
print(test_model.get_elo_score())

# Assert that the instance is of the correct class
assert isinstance(test_model, RankedModel), "test_model is not an instance of RankedModel"

# Assert that the ELO score is a non-negative integer (assuming that's the expected value)
elo_score = test_model.get_elo_score()
assert isinstance(test_model.get_elo_score(), int) and elo_score >= 0, "ELO score is not a non-negative integer"