import re
from typing import Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.box import DOUBLE, ROUNDED
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

# Global Rich Console instance
console = Console()

# Cyberpunk Color System
COLOR_PRIMARY = "cyan"       # `#00f0ff`
COLOR_SECONDARY = "magenta"   # `#ff007f`
COLOR_SUCCESS = "green"       # `#39ff14`
COLOR_WARNING = "yellow"      # `#ffb000`
COLOR_INFO = "blue"          # `#00a8ff`
COLOR_MUTED = "grey50"

def get_header_banner() -> Panel:
    """Returns a cyberpunk themed ASCII art header panel."""
    ascii_art = (
        " ███████╗██╗  ██╗ █████╗ ███╗   ███╗ █████╗ ██╗     ██████╗██╗     ██╗\n"
        " ██╔════╝╚██╗██╔╝██╔══██╗████╗ ████║██╔══██╗██║    ██╔════╝██║     ██║\n"
        " █████╗   ╚███╔╝ ███████║██╔████╔██║███████║██║    ██║     ██║     ██║\n"
        " ██╔══╝   ██╔██╗ ██╔══██║██║╚██╔╝██║██╔══██║██║    ██║     ██║     ██║\n"
        " ███████╗██╔╝ ██╗██║  ██║██║ ╚═╝ ██║██║  ██║██║    ╚██████╗███████╗██║\n"
        " ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝     ╚═════╝╚══════╝╚═╝"
    )
    banner_text = Text()
    banner_text.append(ascii_art, style="bold cyan")
    banner_text.append("\n\n  ⚡ An AI-powered Terminal Assistant for Engineering Students ⚡", style="bold magenta")
    
    return Panel(
        banner_text,
        border_style="bold magenta",
        box=DOUBLE,
        subtitle="[bold cyan]v1.0.0[/bold cyan]",
        subtitle_align="right"
    )

def print_welcome():
    """Prints the welcome banner to the terminal."""
    console.print(get_header_banner())

def parse_markdown_sections(md_text: str) -> Dict[str, str]:
    """
    Parses a markdown string and splits it into sections based on '##' headers.
    Returns a dictionary of {section_title: section_content}.
    """
    sections = {}
    # Find all headings starting with '##'
    pattern = r"^##\s+(.+)$"
    lines = md_text.splitlines()
    
    current_section = "Intro"
    current_content = []
    
    for line in lines:
        match = re.match(pattern, line.strip())
        if match:
            # Save previous section
            if current_content:
                sections[current_section] = "\n".join(current_content).strip()
            current_section = match.group(1).strip()
            current_content = []
        else:
            # Don't keep the main # heading if it's there
            if not line.strip().startswith("# "):
                current_content.append(line)
                
    # Save the last section
    if current_content:
        sections[current_section] = "\n".join(current_content).strip()
        
    return sections

def render_section_panel(title: str, content: str):
    """Renders a single content section in a stylized Panel based on its title."""
    title_lower = title.lower()
    
    # Select colors and icons based on section topic
    if "definition" in title_lower:
        border = f"bold {COLOR_PRIMARY}"
        title_styled = f"📖 {title}"
    elif "explanation" in title_lower:
        border = COLOR_SECONDARY
        title_styled = f"📘 {title}"
    elif "example" in title_lower:
        border = f"bold {COLOR_SECONDARY}"
        title_styled = f"💡 {title}"
    elif "keyword" in title_lower:
        border = f"bold {COLOR_SUCCESS}"
        title_styled = f"⭐ {title}"
    elif "exam ready" in title_lower or "ready answer" in title_lower:
        border = f"bold {COLOR_PRIMARY}"
        title_styled = f"📝 {title}"
    elif "memory trick" in title_lower or "mnemonic" in title_lower:
        border = f"bold {COLOR_WARNING}"
        title_styled = f"🧠 {title}"
    elif "expected marks" in title_lower or "marks breakdown" in title_lower:
        border = "dim white"
        title_styled = f"📊 {title}"
    elif "revision" in title_lower:
        border = f"bold {COLOR_INFO}"
        title_styled = f"⚡ {title}"
    elif "question" in title_lower:
        border = COLOR_INFO
        title_styled = f"❓ {title}"
    else:
        border = "white"
        title_styled = title
        
    panel = Panel(
        content,
        title=f"[bold]{title_styled}[/bold]",
        title_align="left",
        border_style=border,
        box=ROUNDED,
        padding=(1, 2)
    )
    console.print(panel)
    console.print()

def render_exam_answer(md_answer: str):
    """Parses and renders the full structured exam answer into beautiful panels."""
    sections = parse_markdown_sections(md_answer)
    
    # If parsing returned nothing or just Intro (meaning not formatted as ## sections),
    # print the raw markdown directly inside a single Panel
    if not sections or (len(sections) == 1 and "Intro" in sections):
        console.print(Panel(md_answer, border_style="cyan", box=ROUNDED, title="🤖 AI Answer"))
        return
        
    # Render Intro if any
    if "Intro" in sections and sections["Intro"]:
        console.print(sections["Intro"])
        console.print()
        
    # Order sections logically to guarantee standard flow
    # Definition -> Explanation -> Example -> Keywords -> Exam Ready Answer -> Memory Trick -> Expected Marks -> Previous Related Questions -> Revision Tips
    preferred_order = [
        "definition",
        "explanation",
        "example",
        "keywords",
        "exam ready answer",
        "memory trick",
        "expected marks",
        "previous related questions",
        "revision tips"
    ]
    
    rendered_keys = set()
    
    # Render known sections first in preferred order
    for pref in preferred_order:
        for key in list(sections.keys()):
            if pref in key.lower():
                render_section_panel(key, sections[key])
                rendered_keys.add(key)
                break
                
    # Render any remaining sections
    for key, content in sections.items():
        if key not in rendered_keys and key != "Intro":
            render_section_panel(key, content)

def get_progress_bar(description: str) -> Progress:
    """Returns a pre-configured, styled Rich Progress bar instance."""
    return Progress(
        SpinnerColumn(spinner_name="dots"),
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(bar_width=40, complete_style="magenta", finished_style="green"),
        TaskProgressColumn(),
        console=console
    )
