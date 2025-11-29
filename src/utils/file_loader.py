import os
from pathlib import Path
from typing import Optional, Dict, Any
import PyPDF2
import docx
from .logger import logger

class FileLoader:
    """Load and parse various file formats"""
    
    @staticmethod
    def load_text(file_path: str) -> str:
        """Load plain text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error loading text file {file_path}: {e}")
            return ""
    
    @staticmethod
    def load_pdf(file_path: str) -> str:
        """Extract text from PDF"""
        try:
            text = ""
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    text += page.extract_text()
            return text
        except Exception as e:
            logger.error(f"Error loading PDF {file_path}: {e}")
            return ""
    
    @staticmethod
    def load_docx(file_path: str) -> str:
        """Extract text from DOCX"""
        try:
            doc = docx.Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            logger.error(f"Error loading DOCX {file_path}: {e}")
            return ""
    
    @staticmethod
    def load_file(file_path: str) -> str:
        """Auto-detect and load file"""
        ext = Path(file_path).suffix.lower()
        
        if ext == '.pdf':
            return FileLoader.load_pdf(file_path)
        elif ext in ['.docx', '.doc']:
            return FileLoader.load_docx(file_path)
        elif ext in ['.txt', '.md']:
            return FileLoader.load_text(file_path)
        else:
            logger.warning(f"Unsupported file type: {ext}")
            return ""
    
    @staticmethod
    def load_directory(dir_path: str, extension: Optional[str] = None) -> Dict[str, str]:
        """Load all files from directory"""
        files = {}
        path = Path(dir_path)
        
        if not path.exists():
            logger.warning(f"Directory not found: {dir_path}")
            return files
        
        for file in path.iterdir():
            if file.is_file():
                if extension is None or file.suffix == extension:
                    files[file.name] = FileLoader.load_file(str(file))
        
        return files