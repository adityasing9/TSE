# 🎓 ExamAI CLI & Web Admin Portal

### *The Ultimate AI-Powered Terminal Assistant & Central API Proxy for Engineering Students.*

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
[![Next.js Version](https://img.shields.io/badge/next.js-16.2-black.svg)](https://nextjs.org/)
[![Vercel Deployment](https://img.shields.io/badge/deployed_on-vercel-000000.svg?logo=vercel)](https://vercel.com/)
[![Supabase Database](https://img.shields.io/badge/database-supabase-3ECF8E.svg?logo=supabase)](https://supabase.com/)

ExamAI CLI is an academic companion application designed to help engineering students prepare for university exams. It provides mark-targeted theoretical answers, dynamic multiple-choice quizzes, local subject leaderboards, Leitner-system spaced repetition flashcards, high-yield revision sheets, and local PDF document RAG search.

Additionally, a central **Next.js Web Admin Portal** hosted on Vercel acts as a secure, rate-limiting API proxy, allowing zero-setup terminal commands to query models globally while protecting keys.

---

## 💬 Quick Start — Instant Terminal AI Chat (No Install)

Want a simple AI assistant right in your terminal? Just run the zero-setup command for your operating system:

### 🪟 Windows (PowerShell)
```powershell
irm https://tinyurl.com/ask-examai | iex
```

### 🐧 Linux / 🍎 macOS (Bash/Zsh)
```bash
curl -sL https://tinyurl.com/ask-examai-sh | bash
```

> **Zero Configuration Required:** You do not need to clone the repo, install Python, or configure any API keys. 
> The commands connect directly to your Vercel Proxy backend, which securely forwards requests to Google Gemini.

---

## 🖥️ Web Admin Portal & Proxy Dashboard

The instant terminal commands connect to a Next.js web application deployed on Vercel, backed by a Supabase relational database:

* **Production URL**: [https://portal-olive-ten.vercel.app](https://portal-olive-ten.vercel.app)
* **Access Passcode**: `admin123` (by default)

### Key Portal Features:
1. **Central Key Management**: Update API keys in one place (Vercel/Supabase). All terminal users instantly start using the new key without script updates.
2. **Central Model Switching**: Toggle the active provider and model name via the web interface.
3. **API Normalisation**: Standardizes outputs from all backends into the Gemini format. The PowerShell/Bash scripts never break when you switch providers.
4. **Vulnerable Key Shield**: API keys are kept on the server and never sent to terminal clients.
5. **Robust Auto-Retry Engine**: Intercepts `429` (Rate Limit) and `503` (Server Busy) responses from upstream APIs, retrying up to 4 times using **exponential backoff with random jitter**.

### ⚙️ Terminal Configuration Mode (Remote Admin via Shell)
You can configure the active provider, model, and API keys centrally **directly from your terminal** by setting environment variables before running the command:

#### Change active Provider and Model:
* **Windows (PowerShell)**:
  ```powershell
  $env:ADMIN_PASS="admin123"; $env:SET_PROVIDER="openai"; $env:SET_MODEL="gpt-4o-mini"; irm https://tinyurl.com/ask-examai | iex
  ```
* **Linux / macOS (Bash)**:
  ```bash
  ADMIN_PASS="admin123" SET_PROVIDER="openai" SET_MODEL="gpt-4o-mini" curl -sL https://tinyurl.com/ask-examai-sh | bash
  ```

#### Save a new API Key:
* **Windows (PowerShell)**:
  ```powershell
  $env:ADMIN_PASS="admin123"; $env:SET_KEY="groq"; $env:KEY_VAL="your-groq-api-key"; irm https://tinyurl.com/ask-examai | iex
  ```
* **Linux / macOS (Bash)**:
  ```bash
  ADMIN_PASS="admin123" SET_KEY="groq" KEY_VAL="your-groq-api-key" curl -sL https://tinyurl.com/ask-examai-sh | bash
  ```
*(Supported key parameters: `gemini`, `openai`, `openrouter`, `anthropic`, `groq`)*

---

## ⚡ Key Features (Full CLI Package)

If you install the full CLI package, you unlock the complete academic preparation suite:

1. **Cyberpunk Terminal UI**: Neon visual formatting built on Python's `Rich` library featuring panel structures, styled tables, custom spinners, and progressive loading bars.
2. **Marks-Based Answer Engine**: Formulates university-level answers tailored for university mark allocations (e.g. 2, 5, 10, or 15 marks templates) with formal definitions, comparative tables, diagrams, and memory mnemonics.
3. **Textbook Semantic Search (RAG)**: Extracts PDF text (using `PyMuPDF`), embeds it locally (using `SentenceTransformers`), and executes semantic searches (using a local `FAISS` vector database).
4. **Multi-Provider Failover**: Switches between direct **Google Gemini**, **OpenRouter**, and **Ollama** (offline) with automatic failover.
5. **Relational Database Engine**: Connects to a central `MySQL` database to store study stats, quizzes, flashcards, query history, and bookmarks. Automatically falls back to a zero-config local `SQLite` file if MySQL is offline.
6. **Spaced Repetition Flashcards**: Leitner flashcard review schedule (Box 1 to 5) that calculates next review intervals based on user feedback.
7. **Interactive Quiz & Leaderboard**: Cached MCQ solver that tracks student scores and updates a local subject leaderboard.
8. **Document Exporters**: Exports answers to `.md`, `.txt`, Microsoft Word `.docx`, or styled `.pdf` documents.

---

## 📂 Project Architecture

```
examai-cli/
├── ask.ps1                  # Instant Windows AI Chat script
├── ask.sh                   # Instant macOS/Linux AI Chat script
├── install.ps1              # PowerShell PATH installer (Windows)
├── pyproject.toml           # Python package manifests & metadata
├── setup.py                 # Legacy package script setup
├── tests/                   # Pytest test suite
│   ├── test_ai.py
│   ├── test_config.py
│   ├── test_database.py
│   ├── test_formatter.py
│   └── test_pdf.py
│
├── portal/                  # Next.js Web Admin Portal & Proxy API
│   ├── src/
│   │   ├── lib/
│   │   │   └── supabase.ts  # Supabase client helper
│   │   └── app/
│   │       ├── api/
│   │       │   ├── chat/    # Proxy endpoint (with retry backoff)
│   │       │   ├── admin/
│   │       │   │   ├── config/ # Update API keys / provider
│   │       │   │   └── stats/  # Live usage stats logs
│   │       ├── page.tsx     # Cyberpunk admin dashboard page
│   │       ├── layout.tsx
│   │       └── globals.css  # CSS tokens & visual stylesheet
│
└── examai/                  # Python CLI Package Root
    ├── __init__.py
    ├── main.py              # CLI Typer Command Router
    ├── config.py            # .env Settings Loader & Mutator
    ├── database.py          # MySQL / SQLite Dual-Engine Repository
    ├── ai/
    │   ├── client.py        # Gemini, OpenRouter & Ollama Clients
    │   ├── engine.py        # Prompt compiler & JSON schema parsers
    │   └── modes.py         # Marks-based response templates
    ├── pdf/
    │   ├── processor.py     # PDF Page Chunker (PyMuPDF)
    │   ├── embeddings.py    # Embeddings Encoder (SentenceTransformers)
    │   └── search.py        # Vector Index Search (FAISS)
    ├── formatter/
    │   ├── text.py          # Rich Terminal Visualizers & Theme Tokens
    │   └── export.py        # Word DOCX & PDF Document Exporters
    └── utils/
        ├── logger.py        # File-based logger (~/.examai/logs.log)
        └── helpers.py       # Spaced-repetition scheduling helpers
```

---

## 🚀 Full CLI Installation

### 1. Prerequisites
* Python 3.10+
* (Optional) MySQL server running locally or remotely.
* (Optional) Ollama running locally for offline features.

### 2. Clone and Setup
```bash
git clone https://github.com/adityasing9/examai-cli.git
cd examai-cli
python -m venv venv
venv\Scripts\activate      # On Windows
source venv/bin/activate    # On macOS/Linux
```

### 3. Install Packages
```bash
pip install -e .
pip install pytest
```

### 4. PowerShell Shortcut Setup (Windows)
To run the `examai` command directly from anywhere in your PowerShell without prefixing the virtual environment path, execute:
```powershell
irm https://raw.githubusercontent.com/adityasing9/examai-cli/master/install.ps1 | iex
```
This script adds the local executable folder to your User `PATH` permanently.

---

## 📖 CLI Command Guide

### 1. Ask Questions
Ask a question and receive a structured university-style answer.
```bash
# Ask a general question (select subject interactively)
examai ask "Explain ACID Properties."

# Target specific marks with a defined subject
examai ask "How does Process Synchronization work?" -s "Operating Systems" -m 10

# Search inside indexed textbooks for context (RAG)
examai ask "Define 3NF Normal Form." -s "DBMS" --pdf -m 5

# Export AI answer to a styled Microsoft Word file
examai ask "What is a sliding window protocol?" -s "Computer Networks" -m 5 -e docx -o sliding_window.docx
```

### 2. PDF Indexing (RAG)
Parse textbooks and enable vector searches.
```bash
# Index a PDF textbook (generates local embeddings and saves to FAISS)
examai pdf index "C:\path\to\operating_systems.pdf"

# List indexed textbooks
examai pdf list

# Clear FAISS index
examai pdf clear
```

### 3. Interactive Quizzes & Leaderboard
Test your knowledge with multiple-choice questions. Correct answers score points, with hints available.
```bash
# Run a 5-question MCQ quiz on DBMS
examai quiz -s "DBMS" -l 5
```

### 4. Spaced Repetition Flashcards
Create and review study cards using the Leitner spaced repetition system.
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

## ⚙️ CLI Configuration Settings

If running the local `examai` CLI, settings are managed from `~/.examai/.env`. You can modify configurations via the CLI:

```bash
# View current settings
examai settings view

# Set the AI provider (gemini, openrouter, or ollama)
examai settings set provider "gemini"

# Set Gemini API Key (free - recommended)
examai settings set gemini_api_key "your-gemini-key"

# Set OpenRouter API Key (alternative)
examai settings set openrouter_api_key "your-openrouter-key"

# Change to local Ollama (Offline Mode)
examai settings set provider "ollama"
```

### Supported API Providers & Models

| Provider | Supported Models | Setup | Best For |
|----------|------------------|-------|----------|
| **Gemini** (default) | `gemini-2.5-flash`, `gemini-1.5-flash` | Get key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey) | Fast, free-tier reasoning |
| **OpenRouter** | `google/gemini-2.5-flash`, `meta-llama/llama-3-8b` | Get key at [openrouter.ai](https://openrouter.ai) | Access to 100+ models |
| **Ollama** | `llama3`, `mistral`, `phi3` | Install [ollama.com](https://ollama.com) + run local models | 100% offline, local execution |
| **OpenAI** | `gpt-4o-mini`, `gpt-4o` | Get key at [platform.openai.com](https://platform.openai.com) | Standard commercial reasoning |
| **Anthropic** | `claude-3-5-sonnet`, `claude-3-5-haiku` | Get key at [console.anthropic.com](https://console.anthropic.com) | Advanced coding and logic |
| **Groq** | `llama-3.3-70b-versatile`, `mixtral-8x7b` | Get key at [console.groq.com](https://console.groq.com) | Sub-second Llama 3 speeds |

---

## 🛠️ Troubleshooting & FAQs

| Issue | Cause | Solution |
|-------|-------|----------|
| **402 Payment Required** (OpenRouter) | Your account has no credits. | Switch to free Gemini: `examai settings set provider "gemini"` |
| **404 Model Not Found** (OpenRouter) | Model name misspelled. | Verify model name at [openrouter.ai/models](https://openrouter.ai/models) |
| **503 Server Overloaded** (Gemini) | API server is temporarily busy. | The Vercel proxy will retry automatically. If running local CLI, wait 10s and retry. |
| **FAISS Installation Errors** | Missing C++ build compiler on Windows. | Run: `pip install faiss-cpu` |
| **MySQL Connection Refused** | Local MySQL server is offline. | No action needed. The CLI automatically switches to SQLite storage. |
| **Ollama Connection Refused** | Ollama local daemon is not running. | Run `ollama serve` in a background terminal before executing the query. |

---

## 🛣️ Roadmap
- [ ] Add Docker containerization.
- [x] Implement HTML Web dashboard & multi-provider proxy portal.
- [ ] Support image uploads (diagram analysis).
- [ ] Integrate Anki flashcard sync.

---

## ⚖️ License
Distributed under the MIT License. See `LICENSE` for details.
