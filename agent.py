import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from tools import get_stock_price, get_portfolio_summary, get_company_news, explain_financial_term

load_dotenv()

TOOLS = [get_stock_price, get_portfolio_summary, get_company_news, explain_financial_term]

SYSTEM_PROMPT = """You are a stock research assistant. You have access to tools that fetch real live data.

CRITICAL RULES:
- When a tool returns data, copy the ENTIRE tool output into your response word for word
- NEVER say "please check a reliable source" - you ARE the reliable source
- NEVER summarize or shorten tool results
- Always call a tool when asked about stocks, prices, news, or financial terms
- After showing the tool data, you may add one short sentence of context
"""

_agent = None

def build_agent():
    global _agent
    llm = ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=os.getenv("GROQ_API_KEY"))
    _agent = create_react_agent(llm, TOOLS, prompt=SYSTEM_PROMPT)
    return _agent

def run_agent(user_message: str, chat_history: list):
    global _agent
    if _agent is None:
        build_agent()
    result = _agent.invoke({"messages": [("user", user_message)]})
    return result["messages"][-1].content
