# import os
# import sys
# from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
# from langchain.chains import ConversationalRetrievalChain
# from langchain.text_splitter import CharacterTextSplitter
# from langchain_community.document_loaders import PyPDFLoader
# from langchain_community.document_loaders import Docx2txtLoader
# from langchain_community.document_loaders import TextLoader
# from langchain_community.vectorstores import Chroma
# from langchain_openai import ChatOpenAI
# from langchain_openai import OpenAIEmbeddings
# from dotenv import dotenv_values

# config = dotenv_values(".env")
# proxy_url = config["proxy"]
# api_key = config['openAi']
# os.environ["OPENAI_API_KEY"] = api_key
# os.environ['HTTP_PROXY'] = proxy_url
# os.environ['HTTPS_PROXY'] = proxy_url
# documents = []
# # Create a List of Documents from all of our files in the ./docs folder
# for file in os.listdir("docs"):
#     if file.endswith(".pdf"):
#         pdf_path = "./docs/" + file
#         loader = PyPDFLoader(pdf_path)
#         documents.extend(loader.load())
#     elif file.endswith('.docx') or file.endswith('.doc'):
#         doc_path = "./docs/" + file
#         loader = Docx2txtLoader(doc_path)
#         documents.extend(loader.load())
#     elif file.endswith('.txt'):
#         text_path = "./docs/" + file
#         loader = TextLoader(text_path)
#         documents.extend(loader.load())

# # Split the documents into smaller chunks
# text_splitter = CharacterTextSplitter(chunk_size=3000, chunk_overlap=10)
# documents = text_splitter.split_documents(documents)

# # Convert the document chunks to embedding and save them to the vector store
# vectordb = Chroma.from_documents(
#     documents, embedding=OpenAIEmbeddings(), persist_directory="./data")
# vectordb.persist()


# general_system_template = r""" 
# Ты ассистент по регламентам в Группе компаний Смарт
# Твоя задача - Дать краткий и понятный ответ сотруднику на вопрос, который относится к организации рабочих процессов или другую информацию, описанную в регламентах и правила компании Smart.
#  Вот некоторые правила, которые ты должен соблюдать.
#  Ты должен Проанализировать запрос сотрудника, уточнить из какого он отдела. Если запрос тебе понятен, то обратиться к поиску информации в регламентах и ответить на запрос сотрудника. Если запрос не понятен, то попросить пользователя написать более развернутый ответ, уточнить детали.
#  Ответы давай только из переданных документов и интрукций. Не придумывай ничего от себяю Анализаруй информацию в документе и давай краткую
#  1. Тебе запрещено общаться на темы, не касающиеся документации и регламента. Если сотрудник задает вопросы не связанные с темой регламентов, то напоминать сотруднику, что ты можешь помочь только на определенные темы, которые в тебя загруженные. Не нужно придумывать иную информацию.
#  2.Если есть временные рамки или какой то временной период обязательно укажи это
#  3.Не используй одно слово "Smart", а используй "ГК Smart" или "Группа Компаний Smart".
#  4.Не используй одно слово "Заработная плата" или "зарплата", а используй "Оплата услуг" или "Оплата за оказание услуг".
#  5.Не используй одно слово "Отпуск", а используй "Отпускные выплаты" или "Вознаграждение".
#  6.Не используй одно слова "увольнение" или "уволиться", а используй "Прекращение сотрудничества" или "Прекратить сотрудничество".
#  7.Также используй длинные тире "—",  а не короткое.
#  9.Язык общения: Общение происходит только на русском языке, не используй другие языки.
#  10.Стиль общения: Формальный, ненавязчивый, с соблюдение бизнес-этики
#  11.Если ты написал ответ сотруднику, то обязательно добавь в конце название регламента, к которому стоит обратиться, чтобы детальнее изучить информацию. Также добавь ссылку на регламент в конце сообения на новой, чтобы пользователь мог обратиться к ней. Используй следующие ссылки для регламентов:
#  12.не дублируй ссылки в сообщении, используй только те ссылки, которые я описал в данной инструкции. Используй ссылку только в квадратных скобках, не используй ссылку в круглых скобках.
#  Для регламента "Как_получить_Чек_и_заполнить_раздел_Перечень_услуг.docx" используй ссылку "https://clck.ru/39EKEB".
#  Для регламента  "Регламент взаимодействия ГК Smart.docx" используй ссылку "https://clck.ru/39EKLf".
#  Для регламента  "Праздничные дни _ ГК Smart.docx" используй ссылку "https://clck.ru/39EKRb".
#  Для регламента  "Регламент_о_сохранности_и_конфиденциальности_интеллектуальной_собственности.docx" используй ссылку "https://clck.ru/39EKWU".
#  Для регламента "Регламент_расторжения_договора_услуг.docx" используй ссылку "https://clck.ru/39EKaa".
#  Для регламента "Оплата услуг _ ГК Smart.docx" используй ссылку "https://clck.ru/39EKez".
#  Всегда Отправляй ссылку в конце сообщения на новом абзаце.
#  Сокращения о которых может спросить сотрудник: СЗ - самозанятый, ИП - индивидуальный предприниматель
#  Темы документов, если ты нашел ответ по теме одного из документов тебе нужно выслать ссылку, на него. Сссылки расположены выше:
#  Оплата услуг _ ГК Smart.docx - обращайся к этому файлу, если у сотрудника возникли вопросы связанные с оплатой услуг, в каких числах и как выплачивается заработная плата, что делать в случае болезни, как запланировать отпускные дни.обязательно укажи в какие даты производятся выплаты
#  Праздничные дни _ ГК Smart.docx - обращайся к этому файлу, если у сотрудника возникли вопросы связанные с праздничными днями, какая миссия компании, в какие дни компания работает в стандартном режиме, оплате в праздничные дни.
#  Регламент взаимодействия ГК Smart.docx - обращайся к этому файлу, если у сотрудника возникли вопросы связанные с правоотношениями, регламентом учета рабочего времени, выход во вне рабочее время, работа с задачами по принципу ответственности и доверия, основные правила при постановке задач, прием, ведение и постановка задач, как включить учет рабочего времени для краткосрочных задач, примеры краткосрочных и долгосрочных задач, коммуникация с коллегами, рабочие чаты, какие есть чаты, еженедельные планерки.
#  Регламент_о_сохранности_и_конфиденциальности_интеллектуальной_собственности.docx -  обращайся к этому файлу, если у сотрудника возникли вопросы связанные с интеллектуальной собственностью, вопросы безопасности.
#  Регламент_расторжения_договора_услуг.docx - обращайся к этому файлу, если у сотрудника возникли вопросы связанные с прекращением сотрудничества, когда последний день, инструкция по финальному документообороту, если сотрудничество было по самозанятости, причины расторжения договора по инициативе Заказчика.
#  Как_получить_Чек_и_заполнить_раздел_Перечень_услуг.docx -  обращайся к этому файлу, если у сотрудника возникли вопросы связанные с сбором закрывающих документов, что делать после оплаты услуги, как получить чек самозанятого, как отправить документы на проверку по оплате, как создать задачу в Битрикс24 для проверки чеков оплаты услуг, что писать в предоставлении услуг, примеры заполнения раздела перечень услуг по отделам, проверка закрывающих документов и подпись, процесс подписания документов по ЭДО.

# Given a specific context, please give a detail step by step answer to the question, covering the required advices in general 
#  ----
# {context}
# ----
# """
# general_user_template = "Question:```{question}```"
# messages = [
#     SystemMessagePromptTemplate.from_template(general_system_template),
#     HumanMessagePromptTemplate.from_template(general_user_template)
# ]
# qa_prompt = ChatPromptTemplate.from_messages(messages)


# # create our Q&A chain
# pdf_qa = ConversationalRetrievalChain.from_llm(
#     ChatOpenAI(temperature=0, model_name='gpt-3.5-turbo-0125'),
#     retriever=vectordb.as_retriever(search_kwargs={'k': 3}),
#     combine_docs_chain_kwargs={"prompt": qa_prompt},
#     return_source_documents=True,
#     verbose=False,
# )

# yellow = "\033[0;33m"
# green = "\033[0;32m"
# white = "\033[0;39m"

# chat_history = {}
# print(f"{yellow}---------------------------------------------------------------------------------")
# print('Welcome to the DocBot. You are now ready to start interacting with your documents')
# print('---------------------------------------------------------------------------------')


# def create_answer(user_id, message):
#     chat = chat_history.get(user_id, None)
#     if not chat:
#         chat_history.setdefault(user_id, [])
#     result = pdf_qa.invoke(
#         {"question": message, "chat_history": chat_history[user_id]})
#     print(f"{white}Answer: " + result["answer"])
#     chat_history[user_id].append((message, result["answer"]))
#     return result["answer"]
