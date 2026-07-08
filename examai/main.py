import typer
import json
import os
from pathlib import Path
from typing import Optional
from datetime import datetime

from rich.panel import Panel
from rich.table import Table
from rich.box import DOUBLE, ROUNDED
from rich.prompt import Prompt, Confirm

# Import local components
from examai.config import get_settings, update_config_key
from examai.database import db
from examai.ai.engine import prompt_engine
from examai.pdf.search import search_manager
from examai.formatter.text import (
    console, 
    print_welcome, 
    render_exam_answer, 
    get_progress_bar,
    COLOR_PRIMARY,
    COLOR_SECONDARY,
    COLOR_SUCCESS,
    COLOR_WARNING,
    COLOR_INFO
)
from examai.formatter.export import export_markdown, export_text, export_word, export_pdf

# Initialize Typer Apps
app = typer.Typer(
    help="🎓 ExamAI CLI: An AI-powered Terminal Assistant for Engineering Students.",
    rich_markup_mode="rich"
)

pdf_app = typer.Typer(help="📂 Manage and index PDF textbooks/notes.")
app.add_typer(pdf_app, name="pdf")

flash_app = typer.Typer(help="📇 Study and generate flashcards.")
app.add_typer(flash_app, name="flashcards")

hist_app = typer.Typer(help="📜 View and search question history.")
app.add_typer(hist_app, name="history")

sett_app = typer.Typer(help="⚙️ Configure API keys, LLMs, and DB settings.")
app.add_typer(sett_app, name="settings")


def select_subject_interactively() -> str:
    """Helper to let user select a subject from pre-populated list."""
    subjects = db.get_subjects()
    table = Table(title="Available Subjects", box=ROUNDED, border_style="cyan")
    table.add_column("No.", style="bold magenta")
    table.add_column("Subject Name", style="bold green")
    table.add_column("Description", style="white")
    
    for i, sub in enumerate(subjects):
        table.add_column()  # safety check
        table.add_row(str(i + 1), sub["name"], sub["description"])
    
    # Clean up redundant columns
    table.columns = table.columns[:3]
    console.print(table)
    
    choice = Prompt.ask(
        "Select a subject by number", 
        choices=[str(i+1) for i in range(len(subjects))],
        default="1"
    )
    return subjects[int(choice) - 1]["name"]


# ==========================================
# ASK COMMAND
# ==========================================
@app.command(name="ask")
def ask(
    question: Optional[str] = typer.Argument(None, help="The engineering question to answer."),
    subject: Optional[str] = typer.Option(None, "--subject", "-s", help="The academic subject."),
    marks: int = typer.Option(5, "--marks", "-m", help="Target marks (e.g. 2, 5, 10, 15)."),
    mode: str = typer.Option("theory", "--mode", help="Answer mode (theory, mcq, true_false, short_notes, long_answer)."),
    pdf_search: bool = typer.Option(False, "--pdf", "-p", help="Enable semantic RAG search in indexed PDFs."),
    export: Optional[str] = typer.Option(None, "--export", "-e", help="Export format (md, pdf, docx, txt)."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output path for export."),
    provider: Optional[str] = typer.Option(None, "--provider", help="Override LLM provider (openrouter, ollama)."),
    model: Optional[str] = typer.Option(None, "--model", help="Override LLM model name.")
):
    """Ask a question and receive an exam-ready academic answer."""
    print_welcome()
    
    # Prompt for question if not provided in arguments
    if not question:
        question = Prompt.ask("[bold magenta]Paste or Type your Question[/bold magenta]")
        if not question.strip():
            console.print("[bold red]Question cannot be empty![/bold red]")
            return

    # Select subject if not provided
    if not subject:
        subject = select_subject_interactively()
        
    subject_row = db.get_subject_by_name(subject)
    subject_id = subject_row["id"] if subject_row else None
    
    # PDF Context retrieval
    pdf_context = None
    if pdf_search:
        with console.status("[bold cyan]🔍 Searching indexed PDFs...[/bold cyan]", spinner="dots"):
            matched_chunks = search_manager.search(question, k=4)
            if matched_chunks:
                pdf_context = "\n\n".join(matched_chunks)
                logger.info(f"Retrieved {len(matched_chunks)} chunks for PDF context.")
            else:
                console.print("[yellow]⚠️ No matching content found in indexed PDFs. Answering from general knowledge...[/yellow]")

    # Run AI answer generation
    with console.status("[bold cyan]🤖 Thinking...[/bold cyan]", spinner="dots") as status:
        try:
            result = prompt_engine.generate_exam_answer(
                question=question,
                subject=subject,
                mode=mode,
                marks=marks,
                context=pdf_context,
                provider=provider,
                model=model
            )
            answer = result["answer"]
            final_provider = result["provider"]
            final_model = result["model"]
        except Exception as e:
            console.print(f"\n[bold red]Error generating answer:[/bold red] {e}")
            logger.error(f"AI Generation Failed: {e}")
            return
            
    # Save to history
    tags = f"{subject},{mode},{marks}marks"
    db.add_history(question, answer, subject_id, mode, marks, tags)

    # Render structured answer
    console.print(f"[bold cyan]AI Response (Powered by {final_provider} / {final_model}):[/bold cyan]\n")
    render_exam_answer(answer)
    
    # Handle Exports
    if export:
        export = export.lower()
        if not output:
            safe_q = "".join([c if c.isalnum() else "_" for c in question[:20]])
            output = f"export_{safe_q}.{export}"
            
        try:
            if export == "md":
                export_markdown(answer, output)
            elif export == "txt":
                export_text(answer, output)
            elif export == "docx":
                export_word(answer, output, title=question)
            elif export == "pdf":
                export_pdf(answer, output, title=question)
            else:
                console.print(f"[bold red]Unsupported export format: {export}[/bold red]")
                return
            console.print(f"[bold green]✔ Successfully exported answer to {output}[/bold green]")
        except Exception as e:
            console.print(f"[bold red]Failed to export:[/bold red] {e}")


# ==========================================
# QUIZ COMMAND
# ==========================================
@app.command(name="quiz")
def quiz(
    subject: Optional[str] = typer.Option(None, "--subject", "-s", help="The academic subject."),
    limit: int = typer.Option(5, "--limit", "-l", help="Number of questions.")
):
    """Launch an interactive, multiple-choice quiz session."""
    print_welcome()
    
    if not subject:
        subject = select_subject_interactively()
        
    subject_row = db.get_subject_by_name(subject)
    if not subject_row:
        console.print("[bold red]Invalid subject selected![/bold red]")
        return
    subject_id = subject_row["id"]
    
    # Retrieve cached quizzes from DB
    quiz_questions = db.get_quizzes_by_subject(subject_id, limit=limit)
    
    # If no questions cached, generate using AI
    if not quiz_questions:
        with console.status("[bold cyan]🤖 Generating new quiz questions using AI...[/bold cyan]", spinner="dots"):
            try:
                raw_json = prompt_engine.generate_quiz(subject)
                questions_data = json.loads(raw_json)
                for q in questions_data:
                    db.add_quiz_question(
                        question=q["question"],
                        opt_a=q["option_a"],
                        opt_b=q["option_b"],
                        opt_c=q["option_c"],
                        opt_d=q["option_d"],
                        correct=q["correct_option"],
                        explanation=q["explanation"],
                        subject_id=subject_id
                    )
                quiz_questions = db.get_quizzes_by_subject(subject_id, limit=limit)
            except Exception as e:
                console.print(f"[bold red]Failed to generate quiz questions dynamically:[/bold red] {e}")
                logger.error(f"Quiz generation error: {e}")
                return

    if not quiz_questions:
        console.print("[bold red]No quiz questions available for this subject.[/bold red]")
        return
        
    # Run the interactive session
    score = 0
    console.print(Panel(f"[bold green]Starting Quiz on {subject}[/bold green]\nTotal Questions: {len(quiz_questions)}", border_style="cyan"))
    
    for idx, q in enumerate(quiz_questions):
        console.print(f"\n[bold magenta]Question {idx+1}/{len(quiz_questions)}:[/bold magenta] {q['question']}")
        console.print(f"[cyan]A.[/cyan] {q['option_a']}")
        console.print(f"[cyan]B.[/cyan] {q['option_b']}")
        console.print(f"[cyan]C.[/cyan] {q['option_c']}")
        console.print(f"[cyan]D.[/cyan] {q['option_d']}")
        
        while True:
            ans = Prompt.ask("Your Answer (A/B/C/D) or [bold yellow]H[/bold yellow] for Hint", choices=["A", "B", "C", "D", "H", "a", "b", "c", "d", "h"]).upper()
            if ans == "H":
                hint = q["explanation"][:50] + "..."
                console.print(f"[bold yellow]💡 Hint:[/bold yellow] {hint}")
                continue
            break
            
        if ans == q["correct_option"].upper():
            console.print("[bold green]✔ Correct![/bold green]")
            score += 1
        else:
            console.print(f"[bold red]✘ Incorrect.[/bold red] Correct Option was [bold green]{q['correct_option']}[/bold green]")
            
        console.print(f"[dim]{q['explanation']}[/dim]")
        
    console.print(Panel(f"🏆 Quiz Finished! Your Score: [bold green]{score}/{len(quiz_questions)}[/bold green]", border_style="magenta"))
    
    # Save to leaderboard
    save_score = Confirm.ask("Do you want to save your score to the leaderboard?")
    if save_score:
        name = Prompt.ask("Enter your name")
        db.add_leaderboard_entry(name, score, subject_id)
        
        # Display Leaderboard
        leaderboard = db.get_leaderboard(subject_id)
        if leaderboard:
            table = Table(title=f"🏆 {subject} Leaderboard", box=ROUNDED, border_style="cyan")
            table.add_column("Rank", style="bold magenta")
            table.add_column("Student Name", style="bold green")
            table.add_column("Score", style="bold white")
            table.add_column("Date", style="dim white")
            
            for rank, entry in enumerate(leaderboard):
                table.add_row(str(rank+1), entry["user_name"], f"{entry['score']}/{limit}", str(entry["timestamp"])[:16])
            console.print(table)


# ==========================================
# REVISION COMMAND
# ==========================================
@app.command(name="revision")
def revision(
    subject: Optional[str] = typer.Option(None, "--subject", "-s", help="The academic subject.")
):
    """Generate high-yield revision sheets (formulas, keywords, summaries)."""
    print_welcome()
    if not subject:
        subject = select_subject_interactively()
        
    subject_row = db.get_subject_by_name(subject)
    subject_id = subject_row["id"] if subject_row else None
    
    question = f"Generate complete revision notes, including formulas, keywords, concepts, and summaries."
    
    with console.status("[bold cyan]🤖 Generating Revision Sheet...[/bold cyan]", spinner="dots"):
        try:
            result = prompt_engine.generate_exam_answer(
                question=question,
                subject=subject,
                mode="short_notes",
                marks=10
            )
            answer = result["answer"]
        except Exception as e:
            console.print(f"[bold red]Failed to generate revision notes:[/bold red] {e}")
            return
            
    db.add_history(f"Revision Sheet: {subject}", answer, subject_id, "short_notes", 10, f"{subject},revision")
    console.print(f"[bold cyan]⚡ {subject} High-Yield Revision Sheet:[/bold cyan]\n")
    render_exam_answer(answer)


# ==========================================
# FLASHCARDS COMMANDS
# ==========================================
@flash_app.command(name="generate")
def flash_generate(
    subject: Optional[str] = typer.Option(None, "--subject", "-s", help="The subject."),
    topic: str = typer.Option(..., "--topic", "-t", help="Topic to generate cards for (e.g. SQL Joins)."),
    count: int = typer.Option(5, "--count", "-c", help="Number of cards to generate.")
):
    """Generate new flashcards via LLM and save them to database."""
    print_welcome()
    if not subject:
        subject = select_subject_interactively()
        
    subject_row = db.get_subject_by_name(subject)
    if not subject_row:
        console.print("[bold red]Invalid subject![/bold red]")
        return
        
    with console.status(f"[bold cyan]🤖 Generating {count} flashcards for '{topic}'...[/bold cyan]", spinner="dots"):
        try:
            raw_json = prompt_engine.generate_flashcards(subject, topic, count)
            cards = json.loads(raw_json)
            for card in cards:
                db.add_flashcard(card["question"], card["answer"], subject_row["id"])
            console.print(f"[bold green]✔ Successfully generated and saved {len(cards)} flashcards![/bold green]")
        except Exception as e:
            console.print(f"[bold red]Failed to generate flashcards:[/bold red] {e}")
            logger.error(f"Flashcard generation failed: {e}")


@flash_app.command(name="study")
def flash_study(
    subject: Optional[str] = typer.Option(None, "--subject", "-s", help="Filter by subject.")
):
    """Study due flashcards using spaced repetition (Leitner system)."""
    print_welcome()
    
    subject_id = None
    if subject:
        sub_row = db.get_subject_by_name(subject)
        if sub_row:
            subject_id = sub_row["id"]
            
    due_cards = db.get_due_flashcards(subject_id)
    if not due_cards:
        console.print("[bold green]🎉 All caught up! No due flashcards to review.[/bold green]")
        return
        
    console.print(Panel(f"[bold magenta]Spaced Repetition Session[/bold magenta]\nDue Cards: {len(due_cards)}", border_style="cyan"))
    
    for idx, card in enumerate(due_cards):
        console.print(f"\n[bold green]Card {idx+1}/{len(due_cards)}[/bold green] | Subject: [yellow]{card['subject_name']}[/yellow]")
        console.print(Panel(card["question"], border_style="cyan", title="Question"))
        
        Prompt.ask("Press [bold cyan]Enter[/bold cyan] to reveal the answer")
        console.print(Panel(card["answer"], border_style="magenta", title="Answer"))
        
        correct = Confirm.ask("Did you get this correct?")
        db.update_flashcard_leitner(card["id"], correct)
        
    console.print("\n[bold green]✔ Study session completed! Keep up the good work.[/bold green]")


# ==========================================
# PDF COMMANDS
# ==========================================
@pdf_app.command(name="index")
def pdf_index(
    pdf_path: str = typer.Argument(..., help="Path to the PDF textbook/notes file.")
):
    """Extract and index a PDF textbook for Semantic RAG Search."""
    print_welcome()
    path = Path(pdf_path)
    if not path.exists():
        console.print(f"[bold red]File not found at {pdf_path}[/bold red]")
        return
        
    # We run indexer with progress visualizer
    progress = get_progress_bar("Indexing PDF")
    with progress:
        task = progress.add_task("Parsing PDF pages...", total=100)
        try:
            # We can step through task increments manually for visualization
            progress.update(task, completed=20, description="Extracting text...")
            chunks_count = search_manager.index_pdf(str(path))
            progress.update(task, completed=100, description="FAISS index updated!")
            
            console.print(f"\n[bold green]✔ Successfully indexed PDF: {path.name}[/bold green]")
            console.print(f"Total chunks stored: [bold cyan]{chunks_count}[/bold cyan]")
        except Exception as e:
            console.print(f"\n[bold red]Indexing failed:[/bold red] {e}")
            logger.error(f"PDF Indexing failed: {e}")


@pdf_app.command(name="list")
def pdf_list():
    """List all indexed PDF files."""
    print_welcome()
    docs = search_manager.list_indexed_documents()
    if not docs:
        console.print("[yellow]No PDF documents currently indexed.[/yellow]")
        return
        
    table = Table(title="Indexed Textbook Documents", box=ROUNDED, border_style="magenta")
    table.add_column("No.", style="bold cyan")
    table.add_column("Document Name", style="bold green")
    
    for i, doc in enumerate(docs):
        table.add_row(str(i+1), doc)
    console.print(table)


@pdf_app.command(name="clear")
def pdf_clear():
    """Wipe all indexed PDFs from vector database."""
    print_welcome()
    confirm = Confirm.ask("[bold red]Are you sure you want to delete all indexed PDFs and clear FAISS index?[/bold red]")
    if confirm:
        search_manager.clear_index()
        console.print("[bold green]✔ All PDF indexes successfully deleted.[/bold green]")


# ==========================================
# HISTORY COMMANDS
# ==========================================
@hist_app.command(name="list")
def history_list(
    subject: Optional[str] = typer.Option(None, "--subject", "-s", help="Filter by subject."),
    search: str = typer.Option("", "--search", "-q", help="Search keywords."),
    fav: bool = typer.Option(False, "--favorite", help="Show only favorites.")
):
    """View and search previously generated exam answers."""
    print_welcome()
    subject_id = None
    if subject:
        sub_row = db.get_subject_by_name(subject)
        if sub_row:
            subject_id = sub_row["id"]
            
    rows = db.get_history(subject_id=subject_id, search_term=search, favorite_only=fav)
    if not rows:
        console.print("[yellow]No history matching criteria found.[/yellow]")
        return
        
    table = Table(title="Question History", box=ROUNDED, border_style="cyan")
    table.add_column("ID", style="bold magenta")
    table.add_column("Subject", style="bold yellow")
    table.add_column("Question Preview", style="white")
    table.add_column("Fav", style="bold red")
    table.add_column("Date", style="dim white")
    
    for row in rows:
        q_preview = row["question"][:45] + "..." if len(row["question"]) > 45 else row["question"]
        fav_icon = "❤️" if row["favorite"] == 1 else "🤍"
        table.add_row(
            str(row["id"]),
            row["subject_name"] or "None",
            q_preview,
            fav_icon,
            str(row["timestamp"])[:16]
        )
    console.print(table)


@hist_app.command(name="view")
def history_view(
    history_id: int = typer.Argument(..., help="The ID of the history question.")
):
    """View details of a previous generated answer by ID."""
    print_welcome()
    row = db.execute_query(
        "SELECT question, answer, timestamp FROM history WHERE id = %s", (history_id,)
    )
    if not row:
        console.print(f"[bold red]No history item found with ID {history_id}[/bold red]")
        return
        
    console.print(Panel(f"[bold cyan]Question:[/bold cyan] {row[0]['question']}\n[dim]Generated: {row[0]['timestamp']}[/dim]", border_style="magenta"))
    console.print("\n[bold green]Saved Answer:[/bold green]")
    render_exam_answer(row[0]["answer"])


@hist_app.command(name="fav")
def history_fav(
    history_id: int = typer.Argument(..., help="The ID of the history item to favorite.")
):
    """Toggle favorite bookmark state of a question."""
    try:
        new_state = db.toggle_favorite(history_id)
        icon = "❤️" if new_state else "🤍"
        console.print(f"[bold green]✔ Successfully updated bookmark state to {icon}[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Failed to toggle favorite:[/bold red] {e}")


# ==========================================
# BOOKMARKS COMMAND
# ==========================================
@app.command(name="bookmarks")
def bookmarks():
    """List bookmarked (favorited) question/answer entries."""
    print_welcome()
    rows = db.get_bookmarks()
    if not rows:
        console.print("[yellow]No bookmarks saved yet. Use 'examai history fav <id>' to bookmark answers.[/yellow]")
        return
        
    table = Table(title="❤️ Bookmarked Answers", box=ROUNDED, border_style="magenta")
    table.add_column("ID", style="bold cyan")
    table.add_column("Subject", style="bold green")
    table.add_column("Question Preview", style="white")
    table.add_column("Date Bookmarked", style="dim white")
    
    for row in rows:
        q_preview = row["question"][:50] + "..." if len(row["question"]) > 50 else row["question"]
        table.add_row(
            str(row["id"]),
            row["subject_name"] or "None",
            q_preview,
            str(row["timestamp"])[:16]
        )
    console.print(table)


# ==========================================
# SETTINGS COMMANDS
# ==========================================
@sett_app.command(name="view")
def settings_view():
    """Display current LLM API and Database configuration settings."""
    print_welcome()
    settings = get_settings()
    
    table = Table(title="Configuration Settings", box=ROUNDED, border_style="cyan")
    table.add_column("Setting Option", style="bold magenta")
    table.add_column("Value", style="bold white")
    
    # Mask API key for security
    api_key = settings.openrouter_api_key
    masked_key = api_key[:6] + "..." + api_key[-4:] if len(api_key) > 10 else "Not Configured ❌"
    
    table.add_row("Database Host", settings.db_host)
    table.add_row("Database Port", str(settings.db_port))
    table.add_row("Database User", settings.db_user)
    table.add_row("Database Name", settings.db_name)
    table.add_row("OpenRouter Key", masked_key)
    table.add_row("Ollama Host", settings.ollama_host)
    table.add_row("Default Provider", settings.default_provider)
    table.add_row("OpenRouter Model", settings.openrouter_model)
    table.add_row("Ollama Model", settings.ollama_model)
    table.add_row("Theme Style", settings.theme)
    table.add_row("Language", settings.language)
    
    console.print(table)


@sett_app.command(name="set")
def settings_set(
    key: str = typer.Argument(..., help="Setting key to update (e.g. provider, openrouter_api_key, model)."),
    value: str = typer.Argument(..., help="Value to assign.")
):
    """Set or update a configuration setting."""
    key_upper = key.upper()
    valid_keys = [
        "DB_HOST", "DB_PORT", "DB_USER", "DB_PASSWORD", "DB_NAME",
        "OPENROUTER_API_KEY", "OLLAMA_HOST", "DEFAULT_PROVIDER",
        "OPENROUTER_MODEL", "OLLAMA_MODEL", "THEME", "LANGUAGE"
    ]
    
    # Automatically map simple setting names to exact env keys
    key_mapping = {
        "host": "DB_HOST",
        "port": "DB_PORT",
        "user": "DB_USER",
        "password": "DB_PASSWORD",
        "db": "DB_NAME",
        "api_key": "OPENROUTER_API_KEY",
        "openrouter_key": "OPENROUTER_API_KEY",
        "ollama_host": "OLLAMA_HOST",
        "provider": "DEFAULT_PROVIDER",
        "openrouter_model": "OPENROUTER_MODEL",
        "ollama_model": "OLLAMA_MODEL",
        "theme": "THEME",
        "language": "LANGUAGE"
    }
    
    mapped_key = key_mapping.get(key.lower(), key_upper)
    if mapped_key not in valid_keys:
        console.print(f"[bold red]Invalid settings key: '{key}'.[/bold red]\nAllowed keys: {', '.join([k.lower() for k in valid_keys])}")
        return
        
    try:
        update_config_key(mapped_key, value)
        console.print(f"[bold green]✔ Successfully updated setting [yellow]{mapped_key}[/yellow] to '{value}'[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Failed to update setting:[/bold red] {e}")


# ==========================================
# ABOUT COMMAND
# ==========================================
@app.command(name="about")
def about():
    """Show details and credits for ExamAI CLI."""
    print_welcome()
    about_text = (
        "[bold cyan]ExamAI CLI[/bold cyan] is an open-source terminal student companion designed to optimize exam preparation.\n\n"
        "✨ [bold magenta]Features:[/bold magenta] AI answer expansion, dynamic quiz cache, spaced-repetition flashcards, "
        "and offline capability via Ollama local servers.\n\n"
        "👥 [bold green]Developed By:[/bold green] Google DeepMind Advanced Agentic Coding Pair Programmers\n"
        "⚖️ [bold yellow]License:[/bold yellow] MIT License\n"
        "🔗 [bold blue]GitHub Repository:[/bold blue] https://github.com/adityasing9/SettleHub"
    )
    console.print(Panel(about_text, border_style="magenta", box=ROUNDED, title="🎓 About ExamAI CLI"))


if __name__ == "__main__":
    app()
