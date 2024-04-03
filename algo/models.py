from dataclasses import dataclass


@dataclass
class DialogStage:
    message_history: tuple | list
    stage: str
    context: str
    client_category: str
