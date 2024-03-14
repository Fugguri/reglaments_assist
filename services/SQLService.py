# from langchain_core.output_parsers import StrOutputParser
# from langchain_openai import ChatOpenAI
# from langchain_core.runnables import RunnablePassthrough
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_community.utilities import SQLDatabase
# from dotenv import dotenv_values
# import os
# config = dotenv_values(".env")
# proxy_url = config["proxy"]
# api_key = config['openAi']
# os.environ["OPENAI_API_KEY"] = api_key
# os.environ['HTTP_PROXY'] = proxy_url
# os.environ['HTTPS_PROXY'] = proxy_url


# template = """Based on the table schema below, write a SQL query that would answer the user's question:
# {schema}

# Question: {question}
# SQL Query:"""
# prompt = ChatPromptTemplate.from_template(template)
# db = SQLDatabase.from_uri(
#     "mysql+mysqlconnector://fugguri:Neskazu1@99605bb2fc3e.vps.myjino.ru:49394/lisaladanova")


# def get_schema(_):
#     return db.get_table_info()


# def run_query(query):
#     return db.run(query)


# model = ChatOpenAI()

# sql_response = (
#     RunnablePassthrough.assign(schema=get_schema)
#     | prompt
#     | model.bind(stop=["\nSQLResult:"])
#     | StrOutputParser()
# )

# template = """Based on the table schema below, question, sql query, and sql response, write a natural language response:

# {schema}
# Question: {question}
# SQL Query: {query}
# SQL Response: {response}"""
# prompt_response = ChatPromptTemplate.from_template(template)


# full_chain = (
#     RunnablePassthrough.assign(query=sql_response).assign(
#         schema=get_schema,
#         response=lambda x: db.run(x["query"]),
#     )
#     | prompt_response
#     | model
# )

# print(full_chain.invoke(
#     {"question": "Сколько админов в базе данных и как их зовут"}))
