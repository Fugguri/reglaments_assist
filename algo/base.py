from .algorithm import AiAlgorithm
from .storages import DictStorage
from .engine_router import QueryEngine
from .helpers.tokenizer import token_counter
from .definder.step_definder import StepDefinder
storage = DictStorage()
query_engin = QueryEngine()
step_definder = StepDefinder()

algorithm = AiAlgorithm(storage=storage,
                        query_engine=query_engin,
                        token_counter=token_counter,
                        step_definder=step_definder,
                        )
