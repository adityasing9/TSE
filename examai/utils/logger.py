import logging
import os
from pathlib import Path

# Create local data directory for ExamAI
DATA_DIR = Path.home() / ".examai"
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = DATA_DIR / "examai.log"

def setup_logger(name: str = "examai") -> logging.Logger:
    """Sets up a file-based logger to keep the console clean for Rich UI."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
        
    logger.setLevel(logging.DEBUG)
    
    # File handler (logs everything)
    try:
        file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        file_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
    except Exception:
        # Fallback if log directory is unwritable
        pass
        
    return logger

logger = setup_logger()
