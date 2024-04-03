
from langchain_openai import ChatOpenAI
from langchain.chains import create_sql_query_chain
from langchain_community.utilities import SQLDatabase


class SQLQuery_chain:

    def select_from_query(self, question: str, db: str, prompt: str = None, k: int = 5) -> str:
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        db = SQLDatabase.from_uri("sqlite:///Chinook.db")
        chain = create_sql_query_chain(llm, db, prompt, k=5)

        return chain.invoke({"question": question})
