from dataclasses import dataclass


@dataclass
class QnAresponce:

    answer: str
    chat_id: int | str


class BaseQnAService:

    def __init__(self) -> None:
        pass

    def create_message_responce(message: str, chat_id: int | str) -> QnAresponce:
        responce = QnAresponce()
        responce.chat_id = chat_id

        responce.answer = ...
        return responce
