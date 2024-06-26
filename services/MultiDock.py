from llama_index.core.llms import ChatMessage
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
from llama_index.core.chat_engine import SimpleChatEngine, CondenseQuestionChatEngine, ContextChatEngine
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core.query_engine import BaseQueryEngine, RouterQueryEngine
from llama_index.core.tools import QueryEngineTool


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


sys_llm = OpenAI(
    api_key=api_key,
    model="gpt-3.5-turbo-0125",
    temperature=0,
    system_prompt="""Ты ассистент по регламентам в Группе компаний Смарт.
если вопрос не понятен - уточни. Говори только на темы связанные с Группой компаний и о загруженных документах документы
Твоя задача - Дать исчерпывающий ответ сотруднику на вопрос основываясь на данных из документа и дать полную и исчерпывающую инструкцию а не просто сослаться на документ, который относится к организации рабочих процессов или другую информацию, описанную в регламентах и правила компании Smart.
Вот некоторые правила, которые ты должен соблюдать.
Отвечай только на русском языке. 
 Ты должен Проанализировать запрос сотрудника, уточнить из какого он отдела. Если запрос тебе понятен, то обратиться к поиску информации в регламентах и  полностью ответить на запрос сотрудника на основании документа. Если запрос не понятен, то попросить пользователя написать более развернутый ответ, уточнить детали.
 1.Тебе запрещено общаться на темы, не касающиеся документации и регламента. Если сотрудник задает вопросы не связанные с темой регламентов, то напоминать сотруднику, что ты можешь помочь только на определенные темы, которые в тебя загруженные. Не нужно придумывать иную информацию.
 2.Ответы давай только из переданных документов и интрукций. Давай развернутую информацию по вопросу.
 2.Если есть временные рамки или какой то временной период обязательно укажи это
 3.Не используй одно слово "Smart", а используй "ГК Smart" или "Группа Компаний Smart".
 4.Не используй одно слово "Заработная плата" или "зарплата", а используй "Оплата услуг" или "Оплата за оказание услуг".
 5.Не используй одно слово "Отпуск", а используй "Отпускные выплаты" или "Вознаграждение".
 6.Не используй одно слова "увольнение" или "уволиться", а используй "Прекращение сотрудничества" или "Прекратить сотрудничество".
 7.Также используй длинные тире "—",  а не короткое.
 9.Язык общения: Общение происходит только на русском языке, не используй другие языки.
 10.Стиль общения: Формальный, ненавязчивый, с соблюдение бизнес-этики
 11.Если ты написал ответ сотруднику, то обязательно добавь в конце название регламента, к которому стоит обратиться, чтобы детальнее изучить информацию. Также добавь ссылку на регламент в конце сообения на новой, чтобы пользователь мог обратиться к ней. Используй следующие ссылки для регламентов:
 12.не дублируй ссылки в сообщении, используй только те ссылки, которые я описал в данной инструкции. Используй ссылку только в квадратных скобках, не используй ссылку в круглых скобках.
 Для регламента "Как_получить_Чек_и_заполнить_раздел_Перечень_услуг.docx" используй ссылку "https://clck.ru/39EKEB".
 Для регламента  "Регламент взаимодействия ГК Smart.docx" используй ссылку "https://clck.ru/39EKLf".
 Для регламента  "Праздничные дни _ ГК Smart.docx" используй ссылку "https://clck.ru/39EKRb".
 Для регламента  "Регламент_о_сохранности_и_конфиденциальности_интеллектуальной_собственности.docx" используй ссылку "https://clck.ru/39EKWU".
 Для регламента "Регламент_расторжения_договора_услуг.docx" используй ссылку "https://clck.ru/39EKaa".
 Для регламента "Оплата услуг _ ГК Smart.docx" используй ссылку "https://clck.ru/39EKez".
 Всегда Отправляй ссылку в конце сообщения на новом абзаце.
 Сокращения о которых может спросить сотрудник: СЗ - самозанятый, ИП - индивидуальный предприниматель
""")
#  Темы документов, если ты нашел ответ по теме одного из документов тебе нужно выслать ссылку, на него. Сссылки расположены выше:
#  Оплата услуг _ ГК Smart.docx - обращайся к этому файлу, если у сотрудника возникли вопросы связанные с оплатой услуг, в каких числах и как выплачивается заработная плата, что делать в случае болезни, как запланировать отпускные дни.обязательно укажи в какие даты производятся выплаты
#  Праздничные дни _ ГК Smart.docx - обращайся к этому файлу, если у сотрудника возникли вопросы связанные с праздничными днями, какая миссия компании, в какие дни компания работает в стандартном режиме, оплате в праздничные дни.
#  Регламент взаимодействия ГК Smart.docx - обращайся к этому файлу, если у сотрудника возникли вопросы связанные с правоотношениями, регламентом учета рабочего времени, выход во вне рабочее время, работа с задачами по принципу ответственности и доверия, основные правила при постановке задач, прием, ведение и постановка задач, как включить учет рабочего времени для краткосрочных задач, примеры краткосрочных и долгосрочных задач, коммуникация с коллегами, рабочие чаты, какие есть чаты, еженедельные планерки.
#  Регламент_о_сохранности_и_конфиденциальности_интеллектуальной_собственности.docx -  обращайся к этому файлу, если у сотрудника возникли вопросы связанные с интеллектуальной собственностью, вопросы безопасности.
#  Регламент_расторжения_договора_услуг.docx - обращайся к этому файлу, если у сотрудника возникли вопросы связанные с прекращением сотрудничества, когда последний день, инструкция по финальному документообороту, если сотрудничество было по самозанятости, причины расторжения договора по инициативе Заказчика.
#  Как_получить_Чек_и_заполнить_раздел_Перечень_услуг.docx -  обращайся к этому файлу, если у сотрудника возникли вопросы связанные с сбором закрывающих документов, что делать после оплаты услуги, как получить чек самозанятого, как отправить документы на проверку по оплате, как создать задачу в Битрикс24 для проверки чеков оплаты услуг, что писать в предоставлении услуг, примеры заполнения раздела перечень услуг по отделам, проверка закрывающих документов и подпись, процесс подписания документов по ЭДО.

Settings.llm = sys_llm
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
                query_engine=current_index.as_query_engine(llm=Settings.llm,
                                                           similarity_top_k=3),
                description=("Отвечай только на русском языке."
                             "обращайся к этому файлу, если у сотрудника возникли вопросы связанные с оплатой услуг, в каких числах и как выплачивается заработная плата, что делать в случае болезни, как запланировать отпускные дни. Обязательно укажи в какие даты производятся выплаты"
                             "Используйте подробный текстовый вопрос в качестве входных данных для инструмента")
            ))
        case "Праздничные дни _ ГК Smart.pdf":
            tools.append(QueryEngineTool.from_defaults(
                name="Праздничные дни _ ГК Smart.pdf",
                query_engine=current_index.as_query_engine(llm=Settings.llm,
                                                           similarity_top_k=3),
                description=("Отвечай только на русском языке."
                             "обращайся к этому файлу, если у сотрудника возникли вопросы связанные с праздничными днями, какая миссия компании, в какие дни компания работает в стандартном режиме,об оплате в праздничные дни."
                             "Используйте подробный текстовый вопрос в качестве входных данных для инструмента")
            ))

        case "Регламент взаимодействия ГК Smart.pdf":
            tools.append(QueryEngineTool.from_defaults(
                name="Регламент взаимодействия ГК Smart.pdf",
                query_engine=current_index.as_query_engine(llm=Settings.llm,
                                                           similarity_top_k=3),
                description=("Отвечай только на русском языке."
                             "Если спрашивают про учет рабочего времени или ведение задач обязательно упоминай про то как начать и завершшить рабочий день"
                             " обращайся к этому файлу, если у сотрудника возникли вопросы связанные с правоотношениями, регламентом учета рабочего времени, выход во вне рабочее время, работа с задачами по принципу ответственности и доверия, основные правила при постановке задач, прием, ведение и постановка задач, как включить учет рабочего времени для краткосрочных задач, примеры краткосрочных и долгосрочных задач, коммуникация с коллегами, рабочие чаты, какие есть чаты, еженедельные планерки."
                             "Используйте подробный текстовый вопрос в качестве входных данных для инструмента")
            ))

        case "Регламент_о_сохранности_и_конфиденциальности_интеллектуальной_собственности.pdf":
            tools.append(QueryEngineTool.from_defaults(
                name="Регламент_о_сохранности_и_конфиденциальности_интеллектуальной_собственности.pdf",
                query_engine=current_index.as_query_engine(llm=Settings.llm,
                                                           similarity_top_k=3),
                description=("Отвечай только на русском языке."
                             " обращайся к этому файлу, если у сотрудника возникли вопросы связанные с интеллектуальной собственностью, вопросы безопасности."
                             "Используйте подробный текстовый вопрос в качестве входных данных для инструмента")
            ))

        case "Регламент_расторжения_договора_услуг.pdf":
            tools.append(QueryEngineTool.from_defaults(
                name="Регламент_расторжения_договора_услуг.pdf",
                query_engine=current_index.as_query_engine(llm=Settings.llm,
                                                           similarity_top_k=3),
                description=("Отвечай только на русском языке."
                             "Регламент_расторжения_договора_услуг.pdf - обращайся к этому файлу, если у сотрудника возникли вопросы связанные с прекращением сотрудничества, когда последний день, инструкция по финальному документообороту, если сотрудничество было по самозанятости, причины расторжения договора по инициативе Заказчика."
                             "Используйте подробный текстовый вопрос в качестве входных данных для инструмента")
            ))

        case "Как_получить_Чек_и_заполнить_раздел_Перечень_услуг.pdf":
            tools.append(QueryEngineTool.from_defaults(
                name="Как_получить_Чек_и_заполнить_раздел_Перечень_услуг.pdf",
                query_engine=current_index.as_query_engine(llm=Settings.llm,
                                                           similarity_top_k=3),
                description=("Отвечай только на русском языке."
                             " Как_получить_Чек_и_заполнить_раздел_Перечень_услуг.pdf -  обращайся к этому файлу, если у сотрудника возникли вопросы связанные с сбором закрывающих документов, что делать после оплаты услуги, как получить чек самозанятого, как отправить документы на проверку по оплате, как создать задачу в Битрикс24 для проверки чеков оплаты услуг, что писать в предоставлении услуг, примеры заполнения раздела перечень услуг по отделам, проверка закрывающих документов и подпись, процесс подписания документов по ЭДО."
                             "Используйте подробный текстовый вопрос в качестве входных данных для инструмента")
            ))
        case "2_0_Smart_ИП_Подрядчик_оформление_и_получение_оплаты.pdf":
            tools.append(QueryEngineTool.from_defaults(
                name="2_0_Smart_ИП_Подрядчик_оформление_и_получение_оплаты.pdf",
                query_engine=current_index.as_query_engine(llm=Settings.llm,
                                                           similarity_top_k=3),
                description=("Отвечай только на русском языке."
                             " 2_0_Smart_ИП_Подрядчик_оформление_и_получение_оплаты.pdf -  обращайся к этому файлу, если у сотрудника возникли вопросы связанные "
                             "Используйте подробный текстовый вопрос в качестве входных данных для инструмента")
            ))
        case "Закрывающие_документы_для_СЗ_и_ИП.pdf":
            tools.append(QueryEngineTool.from_defaults(
                name="Закрывающие_документы_для_СЗ_и_ИП.pdf",
                query_engine=current_index.as_query_engine(llm=Settings.llm,
                                                           similarity_top_k=3),
                description=("Отвечай только на русском языке."
                             "Закрывающие_документы_для_СЗ_и_ИП.pdf -  обращайся к этому файлу, если нужно получить информацию по сбору закрывающих документов для Самозанятого,что нужно делаь после получения выплат или Сбор закрывающих документов для ИП (Индивидуальных предпринимателей)."
                             "Используйте подробный текстовый вопрос в качестве входных данных для инструмента")
            ))
DEFAULT_SINGLE_PYD_SELECT_PROMPT_TMPL = (
    "Некоторые варианты приведены ниже. Они пронумерованы "
    "список (от 1 до {num_choices}), "
    "где каждый элемент списка соответствует сводке.\n"
    "---------------------\n"
    "{context_list}"
    "\n---------------------\n"
    "Используя только приведенные выше варианты, а не предварительные знания, верните лучший вариант(ы)"
    "(не более {max_outputs}, но выбирайте только то, что необходимо), сгенерировав "
    "объект выбора и причины, которые наиболее актуальны для "
    "вопрос: '{query_str}'\n"
)
llm = OpenAI(
    api_key=api_key,
    model="gpt-4-turbo-preview",
    temperature=0,
    system_prompt="Овечай на русском")

query_engine = RouterQueryEngine.from_defaults(

    selector=PydanticSingleSelector.from_defaults(llm=llm,
                                                  #   prompt_template_str=DEFAULT_SINGLE_PYD_SELECT_PROMPT_TMPL,
                                                  verbose=True
                                                  ),
    query_engine_tools=tools,)


chat_engine = CondenseQuestionChatEngine.from_defaults(
    query_engine, llm=sys_llm)
chat_history = {}


def create_chat_message(content, role: str = "user"):
    return ChatMessage(role=role, content=content)


async def create_answer(user_id, message):
    chat = chat_history.get(user_id, None)

    # return res

    if not chat:
        chat_history.setdefault(user_id, [])
    chat = chat_history[user_id].append((create_chat_message(message)))
    res = chat_engine.chat(message, chat_history=chat)
    chat_history[user_id].append((create_chat_message(res, role="assistant")))

    return res
