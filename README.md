# 💻 Terminal Search Engine (TSE) & Web Admin Portal

### *The Ultimate AI-Powered Terminal Assistant & Central API Proxy.*

---

```
████████╗███████╗███████╗     ██████╗██╗     ██╗
╚══██╔══╝██╔════╝██╔════╝    ██╔════╝██║     ██║
   ██║   ███████╗█████╗      ██║     ██║     ██║
   ██║   ╚════██║██╔══╝      ██║     ██║     ██║
   ██║   ███████║███████╗    ╚██████╗███████╗██║
   ╚═╝   ╚══════╝╚══════╝     ╚═════╝╚══════╝╚═╝
```

---

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Next.js Version](https://img.shields.io/badge/next.js-16.2-black.svg)](https://nextjs.org/)
[![Vercel Deployment](https://img.shields.io/badge/deployed_on-vercel-000000.svg?logo=vercel)](https://vercel.com/)
[![Supabase Database](https://img.shields.io/badge/database-supabase-3ECF8E.svg?logo=supabase)](https://supabase.com/)

TSE is an AI-powered terminal assistant and study preparation utility. It provides mark-targeted theoretical answers, dynamic multiple-choice quizzes, local subject leaderboards, Leitner-system spaced repetition flashcards, high-yield revision sheets, and local PDF document RAG search.

Additionally, a central **Next.js Web Admin Portal** hosted on Vercel acts as a secure, rate-limiting API proxy, allowing zero-setup terminal commands to query models globally while protecting API keys.

---

## 💬 Quick Start — Instant Terminal AI Chat (No Install)

Want a simple AI assistant right in your terminal? Just run the zero-setup command for your operating system:

### 🪟 Windows (PowerShell)
```powershell
irm https://tinyurl.com/tseai | iex
```
*(Fallback if TinyURL is blocked)*:
```powershell
irm https://raw.githubusercontent.com/adityasing9/TSE/master/ask.ps1 | iex
```

### 🐧 Linux / 🍎 macOS (Bash/Zsh)
```bash
bash -c "$(curl -sL https://tinyurl.com/tse-lx)"
```
*(Fallback if TinyURL is blocked)*:
```bash
bash -c "$(curl -sL https://raw.githubusercontent.com/adityasing9/TSE/master/ask.sh)"
```

> **Zero Configuration Required:** You do not need to clone the repo, install Python, or configure any API keys. 
> The commands connect directly to your Vercel Proxy backend, which securely forwards requests to Google Gemini.

---

## 🖥️ Web Admin Portal & Proxy Dashboard

The instant terminal commands connect to a Next.js web application deployed on Vercel, backed by a Supabase relational database:

* **Production URL**: [https://portal-olive-ten.vercel.app](https://portal-olive-ten.vercel.app)
* **Access Passcode**: `admin123` (by default, or ask your admin)

### Key Portal Features:
1. **Central Key Management**: Update API keys in one place (Vercel/Supabase). All terminal users instantly start using the new key without script updates.
2. **Central Model Switching**: Toggle the active provider and model name via the web interface.
3. **API Normalisation**: Standardizes outputs from all backends into the Gemini format. The PowerShell/Bash scripts never break when you switch providers.
4. **Vulnerable Key Shield**: API keys are kept on the server and never sent to terminal clients.
5. **Robust Auto-Retry Engine**: Intercepts `429` (Rate Limit) and `503` (Server Busy) responses from upstream APIs, retrying up to 4 times using **exponential backoff with random jitter**.

### ⚙️ Switch Settings / Passcode directly from Terminal (Optional)
While you manage your API keys on the Web Admin Portal, you can switch the active provider/model or change the admin passcode centrally **directly from your terminal**.

#### 1. Interactive Switch Menu
While chatting in the terminal prompt (`You >`), simply type:
```text
You > /switch
```
This opens an interactive menu to change your active provider and model:
```text
  ┌─── Select AI Provider ───┐
  │ 1. Google Gemini (Free)   │
  │ 2. Groq (Ultra-fast)      │
  │ 3. OpenAI (ChatGPT)       │
  │ 4. OpenRouter             │
  │ 5. Anthropic (Claude)     │
  └───────────────────────────┘
  Choose option (1-5): 2
```

#### 2. Change Admin Passcode Centrally
To change your Vercel/Supabase admin passcode right from the terminal prompt, type:
```text
You > /password
```
It will prompt you for your current passcode, authorize, and let you save a new passcode centrally.

#### 3. Switch via Environment Variables at Startup
* **Windows (PowerShell)**:
  ```powershell
  $env:ADMIN_PASS="admin123"; $env:SET_PROVIDER="groq"; irm https://tinyurl.com/tseai | iex
  ```
  *(Fallback)*:
  ```powershell
  $env:ADMIN_PASS="admin123"; $env:SET_PROVIDER="groq"; irm https://raw.githubusercontent.com/adityasing9/TSE/master/ask.ps1 | iex
  ```
* **Linux / macOS (Bash)**:
  ```bash
  ADMIN_PASS="admin123" SET_PROVIDER="groq" bash -c "$(curl -sL https://tinyurl.com/tse-lx)"
  ```
  *(Fallback)*:
  ```bash
  ADMIN_PASS="admin123" SET_PROVIDER="groq" bash -c "$(curl -sL https://raw.githubusercontent.com/adityasing9/TSE/master/ask.sh)"
  ```

---



## 📂 Project Architecture

```
TSE/
├── ask.ps1                  # Instant Windows AI Chat script
├── ask.sh                   # Instant macOS/Linux AI Chat script
├── install.ps1              # PowerShell PATH installer (Windows)
├── pyproject.toml           # Python package manifests & metadata
├── setup.py                 # Package setup configuration
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
└── tse/                     # Python CLI Package Root
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
        ├── logger.py        # File-based logger (~/.tse/tse.log)
        └── helpers.py       # Spaced-repetition scheduling helpers
```

---



## 🛠️ Troubleshooting & FAQs

| Issue | Cause | Solution |
|-------|-------|----------|
| **402 Payment Required** (OpenRouter) | Your account has no credits. | Switch to free Gemini: `tse settings set provider "gemini"` |
| **404 Model Not Found** (OpenRouter) | Model name misspelled. | Verify model name at [openrouter.ai/models](https://openrouter.ai/models) |
| **503 Server Overloaded** (Gemini) | API server is temporarily busy. | The Vercel proxy will retry automatically. If running local CLI, wait 10s and retry. |


---

## ⚖️ License
Distributed under the MIT License. See `LICENSE` for details.
