# 🎓 LearnQuest AI Assistant (RAG + Lead Generation)

An enterprise-grade AI chatbot built for LearnQuest that combines **Retrieval-Augmented Generation (RAG)** for accurate customer support with an automated **Lead Generation** pipeline. 

Instead of relying on basic LLM knowledge, this bot grounds its answers in official company documentation. When it detects buying intent, it seamlessly pivots from Q&A to a conversational lead capture flow, saving prospects directly to a local database for the sales team.

## 🚀 Key Features
* **Document-Grounded Q&A (RAG):** Answers user queries strictly using the provided LearnQuest PDF manual, eliminating AI hallucinations.
* **Intent-Driven Lead Capture:** Automatically detects when a user wants to enroll or asks about specific courses, pausing the RAG flow to capture their Name, Email, Course, and Country.
* **Secure Admin Dashboard:** A password-protected Streamlit portal for the sales team to view captured leads and export them to CSV.
* **Conversational Guardrails:** Hardcoded logic prevents the AI from leaking system prompts or breaking character.

## 🛠️ Tech Stack
* **Frontend UI:** Streamlit
* **AI Orchestration:** LangChain
* **LLM:** Llama 3.1 (via Groq API for ultra-fast inference)
* **Embeddings:** HuggingFace (`sentence-transformers/all-MiniLM-L6-v2`)
* **Vector Database:** FAISS
* **Relational Database:** SQLite (for secure lead storage)

## 📁 Project Structure
* `LQbot.py`: The main conversational interface and lead routing logic.
* `admin_dashboard.py`: Secure portal for viewing and exporting leads.
* `create_LQmemory_for_llm.py`: Offline ingestion script to chunk PDFs and build the FAISS vector index.
* `connect_LQmemory_with_llm.py`: Core logic for connecting the vector store to the LLM.

## ⚙️ Local Setup Instructions

**1. Clone the repository:**
```bash
git clone [https://github.com/yourusername/LearnQuest-AI-Assistant.git](https://github.com/yourusername/LearnQuest-AI-Assistant.git)
cd LearnQuest-AI-Assistant