from llama_index.core.chat_engine import CondenseQuestionChatEngine
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core import PromptTemplate
from llama_index.core.selectors import LLMSingleSelector, LLMMultiSelector
from llama_index.core.selectors import (
    PydanticMultiSelector,
    PydanticSingleSelector,
)
from llama_index.core import Settings, SQLDatabase
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core.query_engine import BaseQueryEngine, RouterQueryEngine, SQLAutoVectorQueryEngine
from llama_index.core.chat_engine import SimpleChatEngine
from llama_index.core.tools import QueryEngineTool
from llama_index.core.llms import ChatMessage
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.readers.web import AsyncWebPageReader
from llama_index.core.selectors import (
    PydanticMultiSelector,
    PydanticSingleSelector,
)
from llama_index.core.selectors import LLMSingleSelector, LLMMultiSelector
import os
import httpx
from dotenv import dotenv_values
from llama_index.core import (
    Settings,
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage
)
from llama_index.core.chat_engine import SimpleChatEngine, CondenseQuestionChatEngine
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core.query_engine import BaseQueryEngine, RouterQueryEngine
from llama_index.core.tools import QueryEngineTool
from llama_index.core import SummaryIndex
from llama_index.readers.web import SimpleWebPageReader

from .helpers.utils import create_index
from .config import api_key

from sqlalchemy import create_engine

from google.oauth2 import service_account

# SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
# SERVICE_ACCOUNT_FILE = 'credentials.json'

# credentials = service_account.Credentials.from_service_account_file(
#     SERVICE_ACCOUNT_FILE, scopes=SCOPES)


class QueryEngine:

    def __init__(self) -> None:
        ...

    indexes = []

    for file in os.listdir("docs"):
        filename = file.lstrip(".")
        try:
            storage_context = StorageContext.from_defaults(
                persist_dir="./storage/"+filename
            )
            index = load_index_from_storage(storage_context)
            indexes.append({"index": index, "name": file})
        except:
            directory = SimpleDirectoryReader(
                input_files=["docs/"+file]
            ).load_data()
            index = VectorStoreIndex.from_documents(
                directory, show_progress=True)
            indexes.append({"index": index, "name": file})
            index.storage_context.persist(
                persist_dir="./storage/"+filename)

    tools = []
    for index in indexes:
        current_index: VectorStoreIndex = index.get("index")
        match index.get("name"):
            case "Оплата услуг _ ГК Smart.pdf":
                tools.append(QueryEngineTool.from_defaults(
                    name="Оплата услуг _ ГК Smart.pdf",
                    query_engine=current_index.as_chat_engine(llm=Settings.llm,
                                                              similarity_top_k=3),
                    description=("Отвечай только на русском языке."
                                 "обращайся к этому файлу, если у сотрудника возникли вопросы связанные с оплатой услуг, в каких числах и как выплачивается заработная плата, что делать в случае болезни, как запланировать отпускные дни. Обязательно укажи в какие даты производятся выплаты"
                                 "Используйте подробный текстовый вопрос в качестве входных данных для инструмента")
                ))
            case "Праздничные дни _ ГК Smart.pdf":
                tools.append(QueryEngineTool.from_defaults(
                    name="Праздничные дни _ ГК Smart.pdf",
                    query_engine=current_index.as_chat_engine(llm=Settings.llm,
                                                              similarity_top_k=3),
                    description=("Отвечай только на русском языке."
                                 "обращайся к этому файлу, если у сотрудника возникли вопросы связанные с праздничными днями, какая миссия компании, в какие дни компания работает в стандартном режиме,об оплате в праздничные дни."
                                 "Используйте подробный текстовый вопрос в качестве входных данных для инструмента")
                ))

            case "Регламент взаимодействия ГК Smart.pdf":
                tools.append(QueryEngineTool.from_defaults(
                    name="Регламент взаимодействия ГК Smart.pdf",
                    query_engine=current_index.as_chat_engine(llm=Settings.llm,
                                                              similarity_top_k=3),
                    description=("Отвечай только на русском языке."
                                 "Если спрашивают про учет рабочего времени или ведение задач обязательно упоминай про то как начать и завершшить рабочий день"
                                 " обращайся к этому файлу, если у сотрудника возникли вопросы связанные с правоотношениями, регламентом учета рабочего времени, выход во вне рабочее время, работа с задачами по принципу ответственности и доверия, основные правила при постановке задач, прием, ведение и постановка задач, как включить учет рабочего времени для краткосрочных задач, примеры краткосрочных и долгосрочных задач, коммуникация с коллегами, рабочие чаты, какие есть чаты, еженедельные планерки."
                                 "Используйте подробный текстовый вопрос в качестве входных данных для инструмента")
                ))

            case "Регламент_о_сохранности_и_конфиденциальности_интеллектуальной_собственности.pdf":
                tools.append(QueryEngineTool.from_defaults(
                    name="Регламент_о_сохранности_и_конфиденциальности_интеллектуальной_собственности.pdf",
                    query_engine=current_index.as_chat_engine(llm=Settings.llm,
                                                              similarity_top_k=3),
                    description=("Отвечай только на русском языке."
                                 " обращайся к этому файлу, если у сотрудника возникли вопросы связанные с интеллектуальной собственностью, вопросы безопасности."
                                 "Используйте подробный текстовый вопрос в качестве входных данных для инструмента")
                ))

            case "Регламент_расторжения_договора_услуг.pdf":
                tools.append(QueryEngineTool.from_defaults(
                    name="Регламент_расторжения_договора_услуг.pdf",
                    query_engine=current_index.as_chat_engine(llm=Settings.llm,
                                                              similarity_top_k=3),
                    description=("Отвечай только на русском языке."
                                 "Регламент_расторжения_договора_услуг.pdf - обращайся к этому файлу, если у сотрудника возникли вопросы связанные с прекращением сотрудничества, когда последний день, инструкция по финальному документообороту, если сотрудничество было по самозанятости, причины расторжения договора по инициативе Заказчика."
                                 "Используйте подробный текстовый вопрос в качестве входных данных для инструмента")
                ))

            case "Как_получить_Чек_и_заполнить_раздел_Перечень_услуг.pdf":
                tools.append(QueryEngineTool.from_defaults(
                    name="Как_получить_Чек_и_заполнить_раздел_Перечень_услуг.pdf",
                    query_engine=current_index.as_chat_engine(llm=Settings.llm,
                                                              similarity_top_k=3),
                    description=("Отвечай только на русском языке."
                                 " Как_получить_Чек_и_заполнить_раздел_Перечень_услуг.pdf -  обращайся к этому файлу, если у сотрудника возникли вопросы связанные с сбором закрывающих документов, что делать после оплаты услуги, как получить чек самозанятого, как отправить документы на проверку по оплате, как создать задачу в Битрикс24 для проверки чеков оплаты услуг, что писать в предоставлении услуг, примеры заполнения раздела перечень услуг по отделам, проверка закрывающих документов и подпись, процесс подписания документов по ЭДО."
                                 "Используйте подробный текстовый вопрос в качестве входных данных для инструмента")
                ))
            case "2_0_Smart_ИП_Подрядчик_оформление_и_получение_оплаты.pdf":
                tools.append(QueryEngineTool.from_defaults(
                    name="2_0_Smart_ИП_Подрядчик_оформление_и_получение_оплаты.pdf",
                    query_engine=current_index.as_chat_engine(llm=Settings.llm,
                                                              similarity_top_k=3),
                    description=("Отвечай только на русском языке."
                                 " 2_0_Smart_ИП_Подрядчик_оформление_и_получение_оплаты.pdf -  обращайся к этому файлу, если у сотрудника возникли вопросы связанные "
                                 "Используйте подробный текстовый вопрос в качестве входных данных для инструмента")
                ))
            case "Закрывающие_документы_для_СЗ_и_ИП.pdf":
                tools.append(QueryEngineTool.from_defaults(
                    name="Закрывающие_документы_для_СЗ_и_ИП.pdf",
                    query_engine=current_index.as_chat_engine(llm=Settings.llm,
                                                              similarity_top_k=3),
                    description=("Отвечай только на русском языке."
                                 "Закрывающие_документы_для_СЗ_и_ИП.pdf -  обращайся к этому файлу, если нужно получить информацию по сбору закрывающих документов для Самозанятого,что нужно делаь после получения выплат или Сбор закрывающих документов для ИП (Индивидуальных предпринимателей)."
                                 "Используйте подробный текстовый вопрос в качестве входных данных для инструмента")
                ))

    PROMT = (
        "Некоторые варианты приведены ниже. Они пронумерованы "
        "список (от 1 до {num_choices}), "
        "где каждый элемент списка соответствует сводке.\n"
        "---------------------\n"
        "{context_list}"
        "\n---------------------\n"
        "Используя только приведенные выше варианты, а не предварительные знания, верните лучший вариант(ы)"
        "(не более {max_outputs}, но выбирайте только то, что необходимо), сгенерировав "
        "объект выбора и причины, которые наиболее актуальны для "
        "ответ должен удовлетворять стадии, на которой находится пользователь"

        "вопрос: '{query_str}'\n"
    )

    llm = OpenAI(
        api_key=api_key,
        model="gpt-3.5-turbo-0125",
        temperature=0,)

    query_engine = RouterQueryEngine.from_defaults(
        selector=LLMMultiSelector.from_defaults(
            llm=llm, prompt_template_str=PROMT),
        query_engine_tools=tools,)

    async def create_answer_from_engine_router(self, user_id, message, message_history=None):

        if not message_history:
            result: RouterQueryEngine = await self.query_engine.aquery(message)
            return result

        custom_prompt = PromptTemplate(
            """\
        Given a conversation (between Human and Assistant) and a follow up message from Human, \
        rewrite the message to be a standalone question that captures all relevant context \
        from the conversation.

        <Chat History>
        {chat_history}

        <Follow Up Message>
        {question}

        <Standalone question>
        """
        )

# list of `ChatMessage` objects
        chat_engine = CondenseQuestionChatEngine.from_defaults(
            query_engine=self.query_engine,
            condense_question_prompt=custom_prompt,
            # chat_history=message_history,
            verbose=True,
        )
        result = await chat_engine.achat(message, message_history)
        return result
