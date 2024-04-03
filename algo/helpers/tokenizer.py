import tiktoken
from llama_index.core.callbacks import TokenCountingHandler


token_counter = TokenCountingHandler(
    tokenizer=tiktoken.encoding_for_model("gpt-3.5-turbo").encode
)
