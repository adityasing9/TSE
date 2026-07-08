# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-07-08

### Added
- **Interactive CLI**: Implemented beautiful Cyberpunk interface using Typer and Rich Panels/Tables.
- **AI Answer Expansion Engine**: Formulates exam-focused templates (2, 5, 10, 15 marks, MCQ, short notes).
- **Offline Mode Support**: Support for local Ollama instances with automatic fallback when OpenRouter is unreachable.
- **Relational Storage**: MySQL database schema support with dynamic SQLite memory/file backup fallback.
- **PDF Semantic Search**: Implemented text-extraction with PyMuPDF and offline semantic search using SentenceTransformers and local FAISS vector indexes (RAG).
- **Interactive Quiz Mode**: Dynamic exam MCQs, interactive terminal selection, hints, and local score leaderboards.
- **Spaced Repetition Flashcards**: Leitner flashcard review schedule with review intervals.
- **File Exporters**: Direct export of answers into formatted Markdown, plain text, DOCX, and styled PDF files.
- **Quality Controls**: Comprehensive test suite using pytest covering config, DB, AI, search, and formatter.
