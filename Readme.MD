# Flashquiz RAG — AI-Powered Study Assistant

An AI-powered flashcard and Q&A study tool built with Retrieval-Augmented Generation (RAG). Upload any PDF, auto-extract key topics, generate flashcards, and get AI evaluation on your answers.

---

## Demo

> Upload PDF → Select Topics → Study with Flashcards → Get AI Feedback

---

## UI Design

The interface was designed in Figma as low-fidelity wireframes before implementation, covering two main screens:
Page 1 - Upload & Configure:
![alt text](image.png)
![alt text](image-1.png)

Page 2 - Study Mode:
![alt text](image-2.png)
![alt text](<截屏2026-05-29 18.34.29.png>)
![alt text](<截屏2026-05-29 18.36.33.png>)

**Page 1 — Upload & Configure**
- PDF upload zone with processing status
- Auto-extracted keyword chips (multi-select)
- Settings: cards per topic, answer mode (voice / text / both)

**Page 2 — Study Mode**
- Flashcard viewer with progress bar
- Voice recording + text input for answers
- AI evaluation with score and feedback
- Collapsible Q&A chat sidebar
- Session summary with retry wrong cards

A usability evaluation was conducted using the System Usability Scale (SUS), achieving a score of **78/100**, indicating good usability.

---

## Features

- **RAG Pipeline** — PDF is chunked, vectorized, and stored in ChromaDB; answers are grounded in retrieved document passages
- **Auto Keyword Extraction** — LLM analyzes the document and extracts key topics for study
- **Flashcard Generation** — Topic-specific Q&A cards generated from retrieved context
- **Answer Evaluation** — AI scores user answers (1–10) with feedback and model answer
- **Voice & Text Input** — Users can answer by voice recording or typing
- **Q&A Chat Sidebar** — Ask any question about the document, with multi-turn conversation support
- **Session Summary** — Score breakdown by topic with option to retry weak cards
- **Export** — Download session summary as `.txt`

---

## Tech Stack

| Layer | Tools |
|---|---|
| RAG Pipeline | LangChain, ChromaDB, HuggingFace Embeddings |
| LLM | OpenAI API (GPT) |
| Frontend | Streamlit |
| PDF Processing | PyPDF, LangChain Document Loaders |
| Environment | Python 3.12, dotenv |

---

## Project Structure

'''
flashcard_RAG/
├── backend/
│   └── main.py         
├── core/
│   ├── loader.py
│   ├── vectorstore.py
│   ├── keywords.py
│   ├── flashcard.py
│   ├── qa.py
│   ├── evaluator.py
│   └── client.py
├── frontend/
│   └── index.html       
├── doc/
├── chroma_db/
└── .env
'''
---

## Getting Started

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Fill in your API key and LLM base URL

# Run the app
streamlit run ui/app.py
```

---

## Environment Variables

```
OPENAI_API_KEY=your_api_key
LLM_BASE_URL=https://your-llm-endpoint/v1
```