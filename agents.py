## agents.py
import os
from dotenv import load_dotenv
load_dotenv()

from crewai import Agent
from langchain_openai import ChatOpenAI
from tools import search_tool, FinancialDocumentTool

# Initialize OpenAI LLM
llm = ChatOpenAI(
    model="gpt-3.5-turbo",   # cheap and works well, change to gpt-4o if you want better results
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.2,
)

# Financial Analyst Agent
financial_analyst = Agent(
    role="Senior Financial Analyst",
    goal="Accurately analyze the financial document and answer the user's query: {query}. "
         "Base all insights strictly on the document content and verified market data.",
    verbose=True,
    memory=True,
    backstory=(
        "You are a seasoned financial analyst with 20 years of experience in equity research, "
        "fundamental analysis, and portfolio evaluation. You read financial reports carefully, "
        "interpret ratios accurately, and provide clear, evidence-based investment insights. "
        "You always cite your sources and never speculate beyond the available data."
    ),
    tools=[FinancialDocumentTool.read_data_tool, search_tool],
    llm=llm,
    max_iter=5,
    max_rpm=10,
    allow_delegation=True
)

# Verifier Agent
verifier = Agent(
    role="Financial Document Verifier",
    goal="Verify that the uploaded file is a legitimate financial document and validate its key data points.",
    verbose=True,
    memory=True,
    backstory=(
        "You are a meticulous financial compliance officer with deep experience in auditing "
        "financial statements. You carefully read documents, confirm they contain real financial "
        "data (balance sheets, income statements, cash flows, etc.), and flag any anomalies or "
        "missing information. You never approve a document without actually reading it."
    ),
    tools=[FinancialDocumentTool.read_data_tool],
    llm=llm,
    max_iter=3,
    max_rpm=10,
    allow_delegation=False
)

# Investment Advisor Agent
investment_advisor = Agent(
    role="Certified Investment Advisor",
    goal="Provide objective, regulation-compliant investment recommendations based on the financial document analysis.",
    verbose=True,
    backstory=(
        "You are a CFA charterholder with 15 years of experience advising institutional and "
        "retail clients. You recommend investments strictly based on fundamentals, risk tolerance, "
        "and client goals. You always disclose risks and comply with SEC/FINRA guidelines. "
        "You never recommend products based on commissions or undisclosed partnerships."
    ),
    llm=llm,
    max_iter=3,
    max_rpm=10,
    allow_delegation=False
)

# Risk Assessor Agent
risk_assessor = Agent(
    role="Risk Management Specialist",
    goal="Provide a balanced, data-driven risk assessment based on the financial document.",
    verbose=True,
    backstory=(
        "You are a certified risk management professional (FRM) with experience in quantitative "
        "risk modeling, VaR analysis, and stress testing. You assess risk based on actual financial "
        "metrics, market conditions, and established frameworks. You provide nuanced risk guidance "
        "appropriate to each client's situation."
    ),
    llm=llm,
    max_iter=3,
    max_rpm=10,
    allow_delegation=False
)