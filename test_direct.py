# test_direct.py
# Run this to test WITHOUT needing Redis or Celery
# Usage: python test_direct.py

import os
from dotenv import load_dotenv
load_dotenv()

from crewai import Crew, Process
from agents import financial_analyst, verifier, investment_advisor, risk_assessor
from task import verification, analyze_financial_document, investment_analysis, risk_assessment

def run_test(query: str, file_path: str):
    print(f"\n{'='*60}")
    print(f"Query : {query}")
    print(f"File  : {file_path}")
    print(f"{'='*60}\n")

    crew = Crew(
        agents=[verifier, financial_analyst, investment_advisor, risk_assessor],
        tasks=[verification, analyze_financial_document, investment_analysis, risk_assessment],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff({"query": query, "file_path": file_path})

    print(f"\n{'='*60}")
    print("RESULT:")
    print('='*60)
    print(result)
    return result


if __name__ == "__main__":
    # Make sure you have a PDF at data/sample.pdf
    # Or change the path below to any financial PDF you have

    PDF_PATH = "data/TSLA-Q2-2025-Update.pdf"
    QUERY    = "What is the revenue and profit margin of this company?"

    if not os.path.exists(PDF_PATH):
        print(f"ERROR: No PDF found at '{PDF_PATH}'")
        print("Please place a financial PDF at data/sample.pdf and try again.")
        print("\nYou can download Tesla Q2 2025 report from:")
        print("https://www.tesla.com/sites/default/files/downloads/TSLA-Q2-2025-Update.pdf")
    else:
        run_test(query=QUERY, file_path=PDF_PATH)