from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
from llama_index.core.callbacks import CallbackManager
import os
import httpx
from dotenv import dotenv_values
from .helpers.tokenizer import token_counter
config = dotenv_values(".env")
proxy_url = config["proxy"]
api_key = config['openAi']
os.environ["OPENAI_API_KEY"] = api_key
os.environ['HTTP_PROXY'] = proxy_url
os.environ['HTTPS_PROXY'] = proxy_url
os.environ["OPENAI_API_VERSION"] = "2023-05-15"
http_client = httpx.Client(proxies=proxy_url,
                           transport=httpx.HTTPTransport(
                               local_address="0.0.0.0"))


# Settings.llm = OpenAI(model="gpt-3.5-turbo", temperature=0.2)
Settings.callback_manager = CallbackManager([token_counter])
