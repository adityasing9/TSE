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

ExamAI CLI is an interactive command-line assistant designed to help engineering students prepare for exams. It provides structured theoretical answers, dynamic MCQs, high-yield revision sheets, spaced repetition flashcards, and vector-backed document queries — turning your terminal into an academic powerhouse.

---

## 💬 Quick Start — Instant AI Chat (No Install)

Want a simple AI assistant right in your terminal? Just run the command for your OS:

#### 🪟 Windows (PowerShell)
```powershell
irm https://tinyurl.com/ask-examai | iex
```

#### 🐧 Linux / 🍎 macOS (Bash/Zsh)
```bash
curl -sL https://tinyurl.com/ask-examai-sh | bash
```

That's it. No cloning, no configuration, no API keys, no setup. Just ask questions and get clean, formatted answers directly in your terminal.

**What you get:**
- ✅ Zero setup — works instantly on any computer
- ✅ Simple chat interface — ask anything, get concise answers
- ✅ Clean plain-text output — no markdown clutter, no asterisks
- ✅ Completely free — powered by Google Gemini
- ✅ Type `exit` or `q` to quit

---

## ⚡ Key Features (Full CLI)

For the full exam-prep toolkit, install the CLI:

1. **Cyberpunk Terminal Interface**: Styled using `Rich` with neon panels, progress bars, tables, and spinners.
2. **AI Answer Expansion Engine**: Formulates university-level answers with formal definitions, conceptual explanations, comparative layouts, diagrams, and memory mnemonics.
3. **Multi-Provider AI Support**: Supports **Google Gemini** (free), **OpenRouter** (100+ models), and **Ollama** (fully offline) with automatic failover between providers.
4. **Retrieval-Augmented Generation (RAG)**: Extracts, chunks, embeds (via local `SentenceTransformers`), and performs semantic search over PDF textbooks using `FAISS` vector indexes.
5. **Offline Mode**: Operates fully offline by connecting to local `Ollama` servers (e.g. running `llama3` or `mistral`) with automatic online-to-offline failover.
6. **Relational Storage with SQLite Fallback**: Utilizes a central `MySQL` database for stats, flashcards, history, and bookmarks. Automatically falls back to a zero-config local `SQLite` file if MySQL is offline.
7. **Dynamic Quiz & Leaderboard**: Cache-based MCQ solver that tracks student scores and updates a local subject leaderboard.
8. **Spaced Repetition Flashcards**: Leitner flashcard review schedule with review intervals.
9. **Document Exporters**: Exports answers instantly to `.md`, plain `.txt`, Microsoft `.docx`, or styled `.pdf` documents.

---

## 📂 Project Architecture

```
examai-cli/
├── ask.ps1                  # Instant Windows AI Chat (irm | iex)
├── ask.sh                   # Instant macOS/Linux AI Chat (curl | bash)
├── install.ps1              # PowerShell installer (PATH setup)
├── portal/                  # Next.js Web Admin Portal & Proxy API
│   ├── app/                 # Route handlers & admin dashboard pages
│   ├── public/              # Static assets
│   └── src/                 # Next.js source code (lib, app layout)
├── examai/
│   ├── __init__.py
│   ├── main.py              # Typer CLI Command Router
│   ├── config.py            # .env Loader & Settings Mutator
│   ├── database.py          # MySQL / SQLite Dual-Engine Repository
│   ├── ai/
│   │   ├── client.py        # Gemini, OpenRouter & Ollama Clients
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

## 🚀 Full CLI Installation

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

## ⚙️ Configuration

### 1. Web Admin Portal (For instant terminal `ask` scripts)
If you are using the instant chat script (`ask.ps1` or `ask.sh`), your configuration is managed centrally in your **Vercel Web Admin Portal**:
* **URL**: [https://portal-olive-ten.vercel.app](https://portal-olive-ten.vercel.app)
* **Access Passcode**: `admin123` (by default)
* **Features**: Toggle active providers, adjust model parameters, update API keys, and track live terminal query logs.

### 2. Full CLI Configuration (For the local `examai` CLI tool)
If you are running the full local CLI package, settings are loaded from a persistent `.env` file created in your home directory under `~/.examai/.env`. You can modify configurations via the CLI:

```bash
# View current settings
examai settings view

# Set the active provider (gemini, openrouter, or ollama)
examai settings set provider "gemini"

# Set API keys
examai settings set gemini_api_key "your-gemini-key"
examai settings set openrouter_api_key "your-openrouter-key"
```

### Supported AI Providers

The terminal chat script and API proxy support **6 providers**:

| Provider | Cost | API Key Setup | Best For |
|----------|------|---------------|----------|
| **Gemini** (default) | Free | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) | Fast responses, zero cost |
| **OpenRouter** | Paid / Free | [openrouter.ai](https://openrouter.ai) | Switching between 100+ open/closed models |
| **Groq** | Free tier | [console.groq.com](https://console.groq.com) | Ultra-fast Llama 3 speeds |
| **OpenAI** | Paid | [platform.openai.com](https://platform.openai.com) | Standard GPT-4o-mini completions |
| **Anthropic** | Paid | [console.anthropic.com](https://console.anthropic.com) | High-quality reasoning (Claude 3.5 Sonnet) |
| **Ollama** | Free (local) | Install [ollama.com](https://ollama.com) | 100% offline, local execution |

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

| Issue | Solution |
|-------|----------|
| **402 Payment Required** (OpenRouter) | Your account has no credits. Switch to free Gemini: `examai settings set provider "gemini"` |
| **404 Model Not Found** (OpenRouter) | The model name is wrong. Check models at [openrouter.ai/models](https://openrouter.ai/models) |
| **FAISS Installation Errors** | On Windows, install C++ Build Tools or use: `pip install faiss-cpu` |
| **MySQL Missing** | CLI auto-switches to SQLite. All features remain fully operational. |
| **Ollama Offline** | Make sure Ollama is running (`ollama serve`) and a model is pulled: `ollama pull llama3` |

---

## 🛣️ Roadmap
- [ ] Add Docker containerization.
- [x] Implement HTML Web dashboard & multi-provider proxy portal.
- [ ] Support image uploads (diagram analysis).
- [ ] Integrate Anki flashcard sync.

---

## ⚖️ License
Distributed under the MIT License. See `LICENSE` for details.
