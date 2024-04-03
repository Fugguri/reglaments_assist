from abc import ABC, abstractmethod
from llama_index.core.llms import ChatMessage


class BaseStorage(ABC):
    def __init__(self) -> None:
        ...

    @abstractmethod
    def add_user_message_to_history(self, user_id, message):
        ...

    @abstractmethod
    def add_message_to_history(self, user_id, message, role):
        ...

    @abstractmethod
    def get_user_message_history(self, user_id):
        ...

    @abstractmethod
    def initialize_message_history(self, user_id, settings):
        ...

    def create_chat_message(self, content, role: str = "user"):
        return ChatMessage(role=role, content=content)


class DictStorage(BaseStorage):
    def __init__(self) -> None:
        self.history: dict[tuple | list] = dict()

    def add_user_message_to_history(self, user_id, message):
        history = self.history.get(user_id, None)
        if not history:
            self.history.setdefault(user_id, [])
        chat_message = self.create_chat_message(
            message, "user",)

        self.history[user_id].append(chat_message)
        return self.history.get(user_id, None)

    def add_message_to_history(self, user_id, message, role):
        history = self.history.get(user_id, None)
        if not history:
            self.history.setdefault(user_id, [])
        chat_message = self.create_chat_message(
            message, role)
        self.history[user_id].append(chat_message)
        return self.history.get(user_id, None)

    def get_user_message_history(self, user_id) -> tuple | list | None:
        return self.history.get(user_id)

    def initialize_message_history(self, user_id, settings):
        if settings:
            system_message = self.create_chat_message(settings, "system")
            self.history.setdefault(user_id, [system_message])
        else:
            self.history.setdefault(user_id, [])

        return self.history.get(user_id)
