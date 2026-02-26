## tools.py
import os
from dotenv import load_dotenv
load_dotenv()

from crewai.tools import tool
from langchain_community.document_loaders import PyPDFLoader

## Search tool
try:
    from crewai_tools import SerperDevTool
    search_tool = SerperDevTool()
except Exception:
    @tool("Web Search")
    def search_tool(query: str) -> str:
        """Search the web for financial information."""
        return f"Search unavailable. Configure SERPER_API_KEY for web search."

## PDF Reader Tool
class FinancialDocumentTool:
    @staticmethod
    @tool("Read Financial Document")
    def read_data_tool(path: str = 'data/sample.pdf') -> str:
        """Read and extract text content from a PDF financial document.

        Args:
            path: Path to the PDF file.

        Returns:
            str: Full extracted text from the financial document.
        """
        if not os.path.exists(path):
            return f"Error: File not found at '{path}'."

        try:
            loader = PyPDFLoader(file_path=path)
            docs = loader.load()
            full_report = ""
            for data in docs:
                content = data.page_content
                while "\n\n" in content:
                    content = content.replace("\n\n", "\n")
                full_report += content + "\n"
            return full_report if full_report.strip() else "Error: Could not extract text from PDF."
        except Exception as e:
            return f"Error reading PDF: {str(e)}"