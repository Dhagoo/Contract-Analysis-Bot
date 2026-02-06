import pdfplumber
import docx
import os

class ContractParser:
    """
    Handles extraction of text from various file formats (PDF, DOCX, TXT).
    """
    
    @staticmethod
    def parse_pdf(file_path):
        """Extracts text from a PDF file using pdfplumber."""
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            text = f"Error parsing PDF: {str(e)}"
        return text

    @staticmethod
    def parse_docx(file_path):
        """Extracts text from a DOCX file."""
        try:
            doc = docx.Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            return f"Error parsing DOCX: {str(e)}"

    @staticmethod
    def parse_txt(file_path):
        """Read text from a plain text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error parsing TXT: {str(e)}"

    def get_text(self, file_path):
        """Determines file type and extracts text."""
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            return self.parse_pdf(file_path)
        elif ext == '.docx':
            return self.parse_docx(file_path)
        elif ext == '.txt':
            return self.parse_txt(file_path)
        else:
            return "Unsupported file format."
