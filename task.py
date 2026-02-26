from crewai import Task
from agents import financial_analyst, verifier, investment_advisor, risk_assessor
from tools import search_tool, FinancialDocumentTool

verification = Task(
    description="Read and verify the uploaded financial document for the query: {query}.\n"
                "Confirm it is a valid financial document (annual report, 10-K, balance sheet, etc.).\n"
                "Identify the company name, reporting period, and key financial sections present.",
    expected_output="A structured verification report confirming:\n"
                    "- Document type and legitimacy\n"
                    "- Company name and reporting period\n"
                    "- Sections found (income statement, balance sheet, cash flow, notes)\n"
                    "- Any missing or suspicious data",
    agent=verifier,
    tools=[FinancialDocumentTool.read_data_tool],
    async_execution=False
)

analyze_financial_document = Task(
    description="Analyze the verified financial document to answer the user's query: {query}.\n"
                "Extract and interpret key financial metrics: revenue, profit margins, EPS, debt ratios, "
                "liquidity ratios, and growth trends. Use search to benchmark against industry peers if needed.",
    expected_output="A comprehensive financial analysis including:\n"
                    "- Executive summary\n"
                    "- Key financial metrics with interpretation\n"
                    "- Year-over-year trends\n"
                    "- Industry benchmarking (if applicable)\n"
                    "- Specific answer to the user's query\n"
                    "- Data sources cited",
    agent=financial_analyst,
    tools=[FinancialDocumentTool.read_data_tool, search_tool],
    async_execution=False,
    context=[verification]
)

investment_analysis = Task(
    description="Based on the financial analysis, provide investment recommendations relevant to: {query}.\n"
                "Recommendations must be grounded in the document's financials and clearly state assumptions, "
                "risks, and suitability for different investor profiles.",
    expected_output="Investment recommendations including:\n"
                    "- Buy/Hold/Sell assessment with rationale\n"
                    "- Valuation assessment (P/E, P/B, DCF if data available)\n"
                    "- Suitable investor profile\n"
                    "- Key risks to the thesis\n"
                    "- Regulatory disclaimer",
    agent=investment_advisor,
    async_execution=False,
    context=[analyze_financial_document]
)

risk_assessment = Task(
    description="Perform a risk assessment based on the financial document and query: {query}.\n"
                "Use standard risk frameworks. Identify financial, market, operational, and regulatory risks "
                "specific to the company's actual financial position.",
    expected_output="A risk assessment report including:\n"
                    "- Overall risk rating (Low/Medium/High) with justification\n"
                    "- Key risk categories with specific evidence from the document\n"
                    "- Suggested risk mitigation strategies\n"
                    "- Liquidity and solvency risk analysis",
    agent=risk_assessor,
    async_execution=False,
    context=[analyze_financial_document]
)