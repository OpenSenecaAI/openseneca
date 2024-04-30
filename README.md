# OpenSeneca

The opensource library to orchestrate all LLMs around the world (and save money).

**Table of Contents**

1. [Introduction](#introduction)
2. [How it works](#how-it-works)
3. [Setup](#setup)
4. [Configuration](#configuration)
5. [To-do list](#to-do-list)
6. [License](#license)

## Introduction

OpenSeneca is a python library with which to easily orchestrate different LLMs from different providers. \
The logic behind openseneca is simple: given a prompt, a model trained by us understands the intent of the prompt and selects the best model in terms of quality and price. \
Let's imagine that you are developing AI-based software, a chatbot for example.
If the user types “hello,” why use gpt-4 if we could also get a very good response with llama3-8B, a smaller and certainly cheaper model?

The [OpenSenecaLLM](https://huggingface.co/OpenSeneca/openseneca-llm-v01) is based on a finetuned and quantized version of google-bert/bert-base-multilingual-cased.

## How it works

OpenSeneca recognizes the intent of the prompt, and it selects the best LLM for that task, from those you have configured. \
Along with the template, it also selects the best configuration for this task (temperatures, top_p).

<img src="./docs/how-it-works-diagram.jpg" />

## Setup

OpenSeneca is a python package. \
You can install it with the command:

```bash
pip install openseneca
```

Here is a sample of code to integrate it in your software.

```python
from openseneca.providers.azure import AzureProvider
from openseneca.router import Prompt

messages = [
    {"role": "user", "content": "What's the best way to learn data science?"}
]

prompt = Prompt(messages).classify()
model = prompt.best_llm_builder(
    AzureProvider(),
    temperature=prompt.temp,
    top_p=prompt.top_p) \
.build()

# model.request returns a generator
res = next(model.request(prompt.messages))
print(res.content)
```

If you'd like to stream the response:

```python
model = prompt.best_llm_builder(
    AzureProvider(stream=True),
    temperature=prompt.temp,
    top_p=prompt.top_p) \
.build()

res = next(model.request(prompt.messages))

for r in res:
  content = json.loads(res.content)
  yield f"data: {content}\n\n"
```

## Configuration

To configure your LLM endpoints you will need to create an env file (as in the [example](.env.example)).
You can also just configure two LLMs, such as gpt-3.5 and gpt-4, the [Router](openseneca/router.py) will filter only your LLMs from the table.

## To-do list

- [ ] Web Inference Server (in progress)
- [ ] OpenAI Provider class
- [ ] HuggingFace Provider class
- [ ] Abstract the authentication module
- [ ] Multi LLM Function Calling

## License

The OpenSeneca library is licensed under the GNU AFFERO GENERAL PUBLIC LICENSE Version 3. You can find more information about the license in the [LICENSE](LICENSE) file.
