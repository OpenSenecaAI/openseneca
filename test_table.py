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
