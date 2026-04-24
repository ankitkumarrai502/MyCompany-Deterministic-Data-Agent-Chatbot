import os
import time
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.globals import set_debug

# === ADDED: LangChain's built-in token tracker ===
from langchain_community.callbacks import get_openai_callback

set_debug(True)
# Configuration & Setup
load_dotenv(override=True)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
SERVER = '208.112.103.123'
DATABASE = 'LearnQuest'
USERNAME = 'learnquest2'

CONNECTION_STRING = f"mssql+pyodbc://{USERNAME}:{DB_PASSWORD}@{SERVER}/{DATABASE}?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
engine = create_engine(CONNECTION_STRING)

# 1. THE MINI-SCHEMA
MINI_SCHEMA = """
TABLE: vw_clean_schedule
COLUMNS:
- classid (Unique ID)
- coursenumber (Course Code)
- coursename (Name of Course)
- startdate, enddate (Format: YYYY-MM-DD)
- country, city (Location)
- class_price_from_schedule (Numeric - ALWAYS use this for price, cost, or $)
- country_currency_symbol_from_schedule (Text - e.g., 'USD', 'EUR', 'GBP')
- country_search_tags (Text - ALWAYS use this column when searching for country names, abbreviations, or locations)
"""


def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass


def ask_katie(user_question, memory):
    start_time = time.time()
    llm = ChatOpenAI(model="gpt-5-mini", temperature=1, api_key=OPENAI_API_KEY, model_kwargs={"store": True})

    with get_openai_callback() as cb:

        # === CHANGE 1: Give the SQL AI a "Safe Word" ===
        sql_prompt = ChatPromptTemplate.from_template("""
        You are a SQL Server expert. Write a valid MS SQL query to answer the user's question.

        CRITICAL RULES:
        1. Use ONLY the tables and columns listed in the schema below.
        2. NEVER use 'SELECT *'. Always select specific, relevant columns.
        3. If the user asks a generic, conversational, or off-topic question (e.g., "Who created you?", "Tell me a joke", "How are you?"), DO NOT WRITE SQL. Output exactly this word: GENERIC_CHAT
        4. Output ONLY the raw SQL query (or the word GENERIC_CHAT). Do not include markdown formatting.

        SCHEMA:
        {schema}

        CONVERSATION HISTORY:
        {memory}

        USER QUESTION: {question}
        """)

        sql_chain = sql_prompt | llm | StrOutputParser()
        raw_sql = sql_chain.invoke({"schema": MINI_SCHEMA, "memory": memory, "question": user_question})
        clean_sql = raw_sql.replace("```sql", "").replace("```", "").strip()

        # === CHANGE 2: Python intercepts the Safe Word and skips the DB ===
        if clean_sql == "GENERIC_CHAT":
            records = "GENERIC_CHAT"
        else:
            try:
                with engine.connect() as conn:
                    result = conn.execute(text(clean_sql)).fetchmany(50)
                    records = [dict(row._mapping) for row in result]
            except Exception as e:
                records = f"Error executing query: {e}"


        answer_prompt = ChatPromptTemplate.from_template("""
        You are Katie, a Data Analyst for LearnQuest. Answer the user's question.

        RULES:
        1. If the Database Result says "GENERIC_CHAT": DO NOT answer the user's question. Reply with a MAXIMUM of 2 sentences. Be sarcastic, tell them you are a database analyst and not a generic chatbot, and demand they ask a question about courses or schedules.
        2. If querying the database normally: Be concise, natural, and conversational.
        3. NEVER show the user the raw SQL query or column names.
        4. If the Database Result is empty ([]), explicitly list the exact parameters you searched for (e.g., "I couldn't find courses for 'Cognos' in the 'UK'.")
        5. If the Database Result contains an Error, apologize and say the data could not be pulled.

        USER QUESTION: {question}
        DATABASE RESULT: {result}
        """)

        answer_chain = answer_prompt | llm | StrOutputParser()
        final_answer = answer_chain.invoke({"question": user_question, "result": str(records)})

        end_time = time.time()
        execution_time = round(end_time - start_time, 2)

        token_tracking_text = f"\n\n---\n*⏱️ Time taken: {execution_time}s | 📉 Tokens used: {cb.total_tokens} (Input: {cb.prompt_tokens}, Output: {cb.completion_tokens})*"
        final_answer += token_tracking_text

    return final_answer


# Main application flow
def main():
    load_css("style.css")
    st.markdown("""
        <div class="fixed-header">
            📊 LQ Database Assistant
        </div>
    """, unsafe_allow_html=True)

    prompt = st.chat_input("Ask a question about your data...")

    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {'role': 'assistant',
             'content': "Hello! I am Katie. How can I help?"}
        ]

    for message in st.session_state.messages:
        st.chat_message(message['role']).markdown(message['content'])

    if prompt:
        st.chat_message('user').markdown(prompt)
        st.session_state.messages.append({'role': 'user', 'content': prompt})

        # Fast-Path Router for greetings
        greetings = ["hi", "hello", "hey", "thanks", "thank you", "good morning", "good afternoon"]
        if prompt.strip().lower() in greetings:
            response_text = "Hello! Katie here. I'm ready to pull any schedule or course data you need. What can I look up for you?"
            st.chat_message('assistant').markdown(response_text)
            st.session_state.messages.append({'role': 'assistant', 'content': response_text})
            return

        # Build basic memory string
        old_messages = st.session_state.messages[-5:-1]
        memory_storybook = "\n".join(
            [f"{msg['role']}: {msg['content']}" for msg in old_messages if "Hello! I am Katie" not in msg['content']])

        with st.chat_message('assistant'):
            with st.spinner("Thinking..."):
                response_text = ask_katie(prompt, memory_storybook)
            st.markdown(response_text)

        st.session_state.messages.append({'role': 'assistant', 'content': response_text})


if __name__ == "__main__":
    main()