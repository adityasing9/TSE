# 🎓 ExamAI CLI

### *An AI-powered Terminal Assistant for Engineering Students.*

---

```
 ██████╗██╗     ██╗     ███████╗██╗  ██╗ █████╗ ███╗   ███╗ █████╗ ██╗
██╔════╝██║     ██║     ██╔════╝╚██╗██╔╝██╔══██╗████╗ ████║██╔══██╗██║
██║     ██║     ██║     █████╗   ╚███╔╝ ███████║██╔████╔██║███████║██║
██║     ██║     ██║     ██╔══╝   ██╔██╗ ██╔══██║██║╚██╔╝██║██╔══██║██║
╚██████╗███████╗██║     ███████╗██╔╝ ██╗██║  ██║██║ ╚═╝ ██║██║  ██║██║
 ╚═════╝╚══════╝╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝
```

---

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![CI Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()

ExamAI CLI is an interactive command-line assistant designed to help engineering students prepare for exams. By providing structured theoretical answers, dynamic MCQs, high-yield revision sheets, spaced repetition flashcards, and vector-backed document queries, ExamAI turns the terminal into an academic powerhouse.

---

## ⚡ Key Features

1. **Cyberpunk Terminal Interface**: Styled using `Rich` with neon panels, progress bars, tables, and spinners.
2. **AI Answer Expansion Engine**: Formulates university-level answers with formal definitions, conceptual explanations, comparative layouts, diagrams, and memory mnemonics.
3. **Retrieval-Augmented Generation (RAG)**: Extracts, chunks, embeds (via local `SentenceTransformers`), and performs semantic search over PDF textbooks using `FAISS` vector indexes.
4. **Offline Mode**: Operates fully offline by connecting to local `Ollama` servers (e.g. running `llama3` or `mistral`) with automatic online-to-offline failover.
5. **Relational Storage with SQLite Fallback**: Utilizes a central `MySQL` database for stats, flashcards, history, and bookmarks. Automatically falls back to a zero-config local `SQLite` file if MySQL is offline.
6. **Dynamic Quiz & Leaderboard**: Cache-based MCQ solver that tracks student scores and updates a local subject leaderboard.
7. **Spaced Repetition Flashcards**: Leitner flashcard review schedule with review intervals.
8. **Document Exporters**: Exports answers instantly to `.md`, plain `.txt`, Microsoft `.docx`, or styled `.pdf` documents.

---

## 📂 Project Architecture

```
c:/Users/AADI/Desktop/My/CODE/Github/savior/
├── examai/
│   ├── __init__.py
│   ├── main.py              # Typer CLI Command Router
│   ├── config.py            # .env Loader & Settings Mutator
│   ├── database.py          # MySQL / SQLite Dual-Engine Repository
│   ├── ai/
│   │   ├── client.py        # OpenRouter & Ollama Clients
│   │   ├── engine.py        # Prompts compiler and JSON parsers
│   │   └── modes.py         # Exam marks templates (2m, 5m, 10m, 15m, MCQ)
│   ├── pdf/
│   │   ├── processor.py     # PDF Page Text Chunker (PyMuPDF)
│   │   ├── embeddings.py    # Embeddings Encoder (SentenceTransformers)
│   │   └── search.py        # Vector Index Search (FAISS)
│   ├── formatter/
│   │   ├── text.py          # Rich Terminal Visualizers & Theme Tokens
│   │   └── export.py        # DOCX, PDF, MD Document Writers
│   └── utils/
│       ├── logger.py        # File-based logger
│       └── helpers.py       # Spaced-repetition scheduling helpers
├── tests/                   # Pytest suite
└── pyproject.toml           # Package manifests
```

---

## 🚀 Installation

### 1. Prerequisites
- Python 3.10+
- (Optional) MySQL server running locally or remotely.
- (Optional) Ollama running locally for offline features.

### 2. Setup
Clone the repository and create a virtual environment:
```bash
git clone https://github.com/adityasing9/examai-cli.git
cd examai-cli
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate    # macOS/Linux
```

### 3. Install Package
Install the project in editable development mode:
```bash
pip install -e .
pip install pytest
```

### 4. PowerShell Shortcut Setup (Windows)
To run the `examai` command directly from anywhere in your PowerShell without prefixing the virtual environment path, execute:
```powershell
irm https://raw.githubusercontent.com/adityasing9/examai-cli/master/install.ps1 | iex
```
This script adds the local executable folder to your User `PATH` permanently and registers the `examai` alias in your current terminal session immediately.

---

## ⚙️ Configuration

Configurations are loaded from a persistent `.env` file created in your home directory under `~/.examai/.env`. You can modify configurations via the CLI:

```bash
# View current settings
examai settings view

# Set OpenRouter API Key
examai settings set openrouter_api_key "your-openrouter-key"

# Change provider to local Ollama (Offline Mode)
examai settings set provider "ollama"
```

---

## 📖 Command Guide

### 1. Ask Questions
Ask a question and receive a structured answer.
```bash
# Ask a general question (select subject interactively)
examai ask "Explain ACID Properties."

# Target specific marks with a defined subject
examai ask "How does Process Synchronization work?" -s "Operating Systems" -m 10

# Search inside indexed textbooks for context
examai ask "Define 3NF Normal Form." -s "DBMS" --pdf -m 5

# Export AI answer to a styled PDF file
examai ask "What is a sliding window protocol?" -s "Computer Networks" -m 5 -e pdf -o sliding_window.pdf
```

### 2. PDF Indexing (RAG)
Parse textbooks and enable vector searches.
```bash
# Index a PDF textbook
examai pdf index "C:\path\to\operating_systems.pdf"

# List indexed textbooks
examai pdf list

# Clear FAISS index
examai pdf clear
```

### 3. Interactive Quizzes
Test your knowledge with multiple-choice questions.
```bash
# Run a 5-question MCQ quiz on DBMS
examai quiz -s "DBMS" -l 5
```

### 4. Spaced Repetition Flashcards
Create and review study cards.
```bash
# Generate flashcards for a specific topic
examai flashcards generate -s "DBMS" -t "SQL Joins" -c 5

# Review due flashcards
examai flashcards study -s "DBMS"
```

### 5. High-Yield Revision Sheets
```bash
# Generate formulas, keyword checklists, and summaries
examai revision -s "Engineering Mathematics"
```

### 6. Query History & Bookmarks
```bash
# List previously asked questions
examai history list

# View full answer of a past query
examai history view 1

# Bookmark/favorite a question
examai history fav 1

# List bookmarked answers
examai bookmarks
```

---

## 🛠️ Troubleshooting

- **FAISS Installation Errors**: On Windows, if FAISS complains during installation, make sure C++ Build Tools are installed, or install pre-compiled binaries: `pip install faiss-cpu`.
- **MySQL Missing**: If MySQL is not running or credentials are wrong, the CLI will output a console notice and switch to SQLite. Your histories, flashcards, and settings will remain fully operational.
- **Ollama Offline**: When switching to offline provider, make sure Ollama is running (`ollama serve`) and the model is pulled locally: `ollama pull llama3`.

---

## 🛣️ Roadmap
- [ ] Add Docker containerization.
- [ ] Implement HTML Web dashboard.
- [ ] Support image uploads (diagram analysis).
- [ ] Integrate Anki flashcard sync.

---

## ⚖️ License
Distributed under the MIT License. See `LICENSE` for details.
