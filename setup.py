from setuptools import setup, find_packages

setup(
    name="tse",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "typer[all]>=0.9.0",
        "rich>=13.0.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "httpx>=0.24.0",
        "pymupdf>=1.22.0",
        "sentence-transformers>=2.2.0",
        "faiss-cpu>=1.7.4",
        "numpy>=1.20.0",
        "python-docx>=0.8.11",
        "fpdf2>=2.7.0",
        "pymysql>=1.1.0",
        "cryptography>=41.0.0",
    ],
    entry_points={
        "console_scripts": [
            "tse=tse.main:app",
        ],
    },
)
