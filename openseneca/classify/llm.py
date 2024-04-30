from venv import logger
from torch import nn
import torch
from transformers import BertTokenizer, BertModel
import numpy as np
import time
from huggingface_hub import hf_hub_download
from openseneca.utils.logger import Logger
from openseneca.classify.categories import Categories
import os

from dotenv import load_dotenv
load_dotenv()

logger = Logger()

class OpenSenecaLLM(nn.Module):

  MAX_SEQ = 128

  def __init__(self):
      super(OpenSenecaLLM, self).__init__()
      self.bert = BertModel.from_pretrained(
        'google-bert/bert-base-multilingual-cased'
      )
      self.dropout = nn.Dropout(0.0)
      self.linear = nn.Linear(768, len(Categories.get()))
      self.relu = nn.ReLU()

      current_path = os.path.dirname(os.path.abspath(__file__))
      self.path = f'{current_path}/openseneca-llm-v01/openseneca-llm-v01.pt'

      if not os.path.exists(self.path):
        try:
          # Download the model
          hf_hub_download(
            repo_id="OpenSeneca/openseneca-llm-v01",
            filename="openseneca-llm-v01.pt",
            local_dir=f"{current_path}/openseneca-llm-v01/"
          )
        except Exception as e:
          logger.error(f"Error downloading model: {e}")
          raise Exception("Error downloading the OpenSeneca-LLM.")

      self.__tokenizer = \
        BertTokenizer.from_pretrained(
          'google-bert/bert-base-multilingual-cased'
        )
      self.labels = Categories.get()
      self.__load()

  def forward(self, input_id, mask):

    _, pooled_output = self.bert(input_ids= input_id, attention_mask=mask,return_dict=False)
    dropout_output = self.dropout(pooled_output)
    linear_output = self.linear(dropout_output)
    final_layer = self.relu(linear_output)

    return final_layer

  def __load(self):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    self.load_state_dict(torch.load(self.path, map_location=device))
    self.eval()

  def get_label(self, text: str) -> str:
    start_time = time.time()

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    encoded_input = self.__tokenizer(
      text,
      max_length=self.MAX_SEQ,
      padding='max_length',
      truncation=True,
      return_tensors='pt',
    )

    mask = encoded_input['attention_mask'].to(device)
    input_id = encoded_input['input_ids'].squeeze(1).to(device)
    output = self(input_id, mask).cpu().detach().numpy()
    predictions = np.argmax(output, axis=1)
    label_id = predictions[0]

    label = self.__search_label(self.labels, label_id)
    end_time = time.time()
    execution_time_ms = (end_time - start_time) * 1000

    logger.debug("OpenSenecaLLM Execution time: {} milliseconds."\
      .format(execution_time_ms))

    return label

  @staticmethod
  def __search_label(labels, label_id):
    for package_name, package_label_id in labels.items():
        if package_label_id == label_id:
            return package_name
    return None
