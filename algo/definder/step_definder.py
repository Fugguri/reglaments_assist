from llama_index.llms.openai import OpenAI
from llama_index.core.llms import ChatMessage


class StepDefinder:
    def __init__(self) -> None:
        self.llm = OpenAI(
            system_prompt="Отвечай только на русском языке", temperature=0.3)

    async def define(self, messages: tuple):
        answer = await self.llm.achat(messages)
        return answer.message.content
