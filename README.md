# 📊 LearnQuest Data Agent (AskKatie)

A high-performance, deterministic Text-to-SQL AI Agent designed to empower non-technical staff to query live schedule and course data using natural English. 

Instead of writing complex SQL, users simply ask "Katie" (the AI persona) questions like *"List the Cognos classes in the UK for May"*, and receive conversational, accurate answers in under 5 seconds.

## ✨ Key Features
* **Lightning Fast & Cost-Effective:** Replaced traditional, expensive Agent ReAct loops with a strict 3-step Deterministic Pipeline, dropping token consumption by 98% (from ~100k tokens down to ~1.5k per query) and reducing response times to <5 seconds.
* **Smart Routing (Zero-Token Chat):** Generic or off-topic questions (e.g., "Who created you?") are intercepted via a `GENERIC_CHAT` safe-word, bypassing the database entirely for instant, safe responses.
* **Built-in Telemetry:** Every response outputs live metrics in the UI, tracking exact execution time and OpenAI token usage (Input/Output).
* **Database Safety Valves:** Hard-capped data extraction using Python's `.fetchmany(50)` ensures the LLM's context window never explodes, preventing application crashes.
* **Semantic SQL Views:** Utilizes a custom SQL View (`vw_clean_schedule`) to handle location abbreviations (e.g., mapping "UK" to "United Kingdom") at the database level, drastically reducing the AI's cognitive load.

## 🛠️ Tech Stack
* **Frontend:** [Streamlit](https://streamlit.io/)
* **AI Orchestration:** [LangChain](https://www.langchain.com/) (LCEL - LangChain Expression Language)
* **LLM:** OpenAI `gpt-5-mini`
* **Database / ORM:** MS SQL Server, SQLAlchemy, PyODBC
* **Language:** Python 3

## 🧠 Architecture: The 3-Step Pipeline
This agent avoids the unpredictability of standard autonomous AI agents by using a strict, heavily guardrailed LangChain Expression Language (LCEL) pipeline:
1. **Translate (English to SQL):** The LLM receives the user's question alongside a highly compressed "Mini-Schema" and outputs *only* raw SQL.
2. **Execute (Python):** The SQL is executed securely via SQLAlchemy. The AI is put to sleep during this phase, and results are safely capped.
3. **Format (Data to English):** The LLM wakes back up to ingest the capped raw data and format it into a friendly, easy-to-read response as "Katie".

## 🚀 Local Setup & Installation

### Prerequisites
* Python 3.8+
* [ODBC Driver 18 for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server) installed on your machine.

### 1. Clone the repository
```bash
git clone [https://github.com/ankitkumarrai502/MyCompany-Deterministic-Data-Agent-Chatbot.git]
cd MyCompany-Deterministic-Data-Agent-Chatbot
