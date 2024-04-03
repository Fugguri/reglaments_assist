import re
from .models import DialogStage
from llama_index.llms.openai import OpenAI
from llama_index.core.base.response.schema import Response
from .storages import BaseStorage
from .engine_router import QueryEngine
from llama_index.core.callbacks import TokenCountingHandler
from .definder.step_definder import StepDefinder


class AiAlgorithm:
    def __init__(self, storage: BaseStorage, query_engine: QueryEngine, token_counter: TokenCountingHandler, step_definder: StepDefinder) -> None:
        self.storage: BaseStorage = storage
        self.query_engine: QueryEngine = query_engine
        self.token_counter: TokenCountingHandler = token_counter
        self.step_definder: StepDefinder = step_definder
        self.trace = False
        self.llm = OpenAI(system_prompt="Отвечай только на русском языке")

    async def create_answer(self, message: str, chat_id: int | str) -> str:
        return await self._create_answer(message, chat_id)

    async def _create_answer(self, message: str, user_id: int | str) -> str:
        ai_settings, STEPS = self._get_settings()

        self.create_message_history(user_id, ai_settings)
        message_history = self._add_message(user_id, message, "user")
        print(message_history)
        definder: str = await self.step_definder.define(message_history)
        answer = await self._handle_answer(definder, user_id, message, STEPS)
        self._add_message(user_id, answer, "assistant")
        self.write_token_usage()
        return answer

    def write_token_usage(self):
        return self.__get_tokens_amount()

    async def _handle_answer(self, definder, user_id, message, STEPS):
        print(definder)
        current_step = re.search(r"Шаг: \d", definder).group(0).strip()
        client_data = re.search(r"Данные сотрудника:(.*)", definder)
        objection = re.search(r"Возражение:(.*)", definder)
        if objection:
            objection = objection.group(0).strip()
        client_category = re.match(r"Категория сотрудника:(.*)", definder)
        answer = re.search(r"Ответ клиенту:(.*)", definder, re.DOTALL).group(0)
        answer = answer.replace("Ответ клиенту: ", "").strip()
        suggestions = re.match(
            r"Предложенный консультантом вариант:(.*)", definder)

        print(answer)
        steps = {
            "Шаг 1": str("Тебе нужно узнать, по какому вопросу обратился сотрудник. Если нужно ответить на одну из следующих тем - переходи на шаг 3. Если не понятно уточняй вопрос в шаге 2"
                         "категории вопросов и общая информация о них"
                         "- Общие регламенты ГК Smart"
                         "Описание: здесь ты можешь задать вопросы по взаимодействию в команде (учет рабочего времени, работа с задачами, коммуникация с коллегами, рабочие чаты), о праздничных днях, о сохранности и конфиденциальности информации"
                         "- Оплата услуг и закрывающие документы"
                         "Описание: здесь ты можешь задать вопросы по оплате услуг, что делать в случае болезни, как запланировать отпускные дни, какие закрывающие документы необходимо предоставлять после получения выплаты за оказанные услуги"
                         " - Расторжение договора услуг"
                         "Описание: здесь ты можешь узнать о порядке действий, если ты принял решение прекратить сотрудничество"),
            "Шаг 2":  "Если сотрудник задал вопрос - отчеваем на вопрос сотрудника "

        }

        match current_step:
            case "Шаг: 3":
                step_and_instruct = re.search(
                    current_step, STEPS, re.MULTILINE)
                prompt = ("Тебе будет передан шаг, с инструкцией, данные сотрудника и предложенный консультантом вариант."
                          "Шаг и инструкция - {step}"
                          "Данные сотрудника - {client_data}"
                          "Предложенные консультантом варианты -{suggestions}"
                          ).format(step=step_and_instruct, client_data=client_data, suggestions=suggestions)

                answer: Response = await self.query_engine.create_answer_from_engine_router(user_id, prompt)

        return answer

    def _get_settings(self):
        STEPS = (
            "Шаг 1 - Тебе нужно узнать, по какому вопросу обратился сотрудник. "
            "категории вопросов и общая информация о них"
            "- Общие регламенты ГК Smart"
            "Описание: здесь ты можешь задать вопросы по взаимодействию в команде (учет рабочего времени, работа с задачами, коммуникация с коллегами, рабочие чаты), о праздничных днях, о сохранности и конфиденциальности информации"
            "- Оплата услуг и закрывающие документы"
            "Описание: здесь ты можешь задать вопросы по оплате услуг, что делать в случае болезни, как запланировать отпускные дни, какие закрывающие документы необходимо предоставлять после получения выплаты за оказанные услуги"
            " - Расторжение договора услуг"
            "Описание: здесь ты можешь узнать о порядке действий, если ты принял решение прекратить сотрудничество"
            "Шаг 2 - Узнаем детали вопроса. для этого- обращаемся к загруенным документам, для поиска информации."
            "Шаг 3 - Если вопрос задан полно - отвечаем на него."
        )
        # TODO  transfer in analyzer only the last 10 message in history ?
        AI_NAME = "чат-бот ГК Smart."
        greet_template = """Привет! давай знакомиться! Я чат-бот ГК Smart. Я помогу оперативно найти ответ на твой вопрос, нужный документ или регламент, а также подскажу контакты коллег!
Чтобы я дал корректный ответ на твой вопрос, прошу тебя задавать мне максимально понятный и подробный вопрос.
Пример вопроса, на который я смогу найти ответ:
"Расскажи о действиях, которые необходимо сделать самозанятому после получения выплаты"
Пример вопроса, на который я не смогу найти ответ, либо он будет некорректным:
"Расскажи про выплаты"
"""
        # "не придумывай данные, если нужны данные вставь эту строку - {{data}}, я заменю эти данных на нужные"
        ai_settings = (
            "Для приветсвия используй этот шаблон: {greet_template} "
            "ты нейро-саммаризатор, основываясь на истории диалога ты должен собирать и обрабатывать данные"
            "Тебе будут переданы шаги, по которым должен идти диалог ты должен определить, на каком этапе находится диалог"
            'ШАГИ:'
            '{STEPS}'
            "Так же тебе нужно категоризировать сотрудника по диалогу - категории клиентов:"
            "1.Первое касание 2.заинтересован 3.готов купить 4.оставил контакты/заявку"
            'отправляй только данные, которые требуются'
            "Никогда не пропускай шаги  и всегда пиши номер шага"
            "ответ клиенту формируется на основании информации и инструкций о текущем щаге и собранных о клинете данных"
            "обязательно отвечай только в указанном ниже формате ответа. обязательно укажи шаг, на котором находится общение Если данных нет напиши - отсутствуют "
            "Обязательный Формат ответа:"
            "\nШаг: [номер шага]"
            '\nВозражение: [если нужно отработать возражение- тут отмечается "ДА", во всех остальных случаях - НЕТ]'
            "\nКатегория сотрудника: [порядковый номер категории] - [категория сотрудника]"
            "\nПредложенный консультантом вариант: [все варианты, который предложил консультант]"
            "\nДанные сотрудника: [тут все данные, что могут понадобиться для работы с клинетом, его личные данные или предложенные ассистентом варианты]"
            "\nОтвет клиенту: [ответ на сообщение сотрудника]"
        ).format(STEPS=STEPS, greet_template=greet_template)

        return (ai_settings, STEPS)

    def create_message_history(self, user_id, ai_settings):
        is_message_history_exist = self.storage.get_user_message_history(
            user_id)

        if not is_message_history_exist:
            return self._create_messages(user_id, ai_settings)

    def _create_messages(self, user_id, ai_settings):
        self.storage.initialize_message_history(
            user_id, ai_settings)

    def _add_message(self, user_id, message, role,):
        self.storage.add_message_to_history(
            user_id, message=message, role=role)
        return self.storage.get_user_message_history(user_id)

    def __get_tokens_amount(self):
        llm_tokens = self.token_counter.total_llm_token_count
        embedding_tokens = self.token_counter.total_embedding_token_count
        if self.trace:
            print("LMM tokens usage - "+str(llm_tokens))
            print("Embedding tokens usage - "+str(embedding_tokens))
        self.token_counter.reset_counts()
        return (llm_tokens, embedding_tokens)
