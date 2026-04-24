import re
import gradio as gr
from agent import run_agent
from logger import log_exchange, detect_tool, export_readable_log
from tools import get_stock_price, get_portfolio_summary, get_company_news, explain_financial_term
from portfolio_manager import add_to_portfolio, view_portfolio, remove_from_portfolio, generate_pie_chart

EXAMPLE_PROMPTS = [
    "What is the stock price of AAPL right now",
    "Show me prices for MSFT and TSLA",
    "What's the latest news on AAPL?",
    "Explain what a P/E ratio is",
    "Add AAPL with $2000",
    "Show my portfolio",
    "Remove AAPL from my portfolio",
    "What does beta mean in investing?",
]

def extract_tickers(message):
    return re.findall(r'\b[A-Z]{2,5}\b', message)

def chat(user_message: str, history: list):
    if not user_message.strip():
        return "", history, None

    msg_lower = user_message.lower()
    tickers = extract_tickers(user_message)
    chart = None

    try:
        # Add to portfolio — "Add AAPL with $2000" or "Add AAPL $2000"
        if any(w in msg_lower for w in ["add ", "save ", "invest "]) and "$" in user_message and tickers:
            amount_match = re.search(r'\$(\d+[\d,]*\.?\d*)', user_message)
            ticker = tickers[0]
            if amount_match:
                invested = float(amount_match.group(1).replace(",", ""))
                response = add_to_portfolio(ticker, invested)
            else:
                response = "Please include a dollar amount. Example: 'Add AAPL with $2000'"

        # View portfolio
        elif any(w in msg_lower for w in ["show my portfolio", "view portfolio", "my portfolio", "my holdings"]):
            response = view_portfolio()
            chart = generate_pie_chart()

        # Remove from portfolio
        elif any(w in msg_lower for w in ["remove", "delete"]) and tickers:
            response = remove_from_portfolio(tickers[0])
            chart = generate_pie_chart()

        # Multi-stock price
        elif len(tickers) >= 2:
            response = get_portfolio_summary.invoke({"tickers": ",".join(tickers)})

        # News
        elif "news" in msg_lower or "headline" in msg_lower:
            ticker = tickers[0] if tickers else re.sub(r'[^A-Z]', '', user_message.split()[-1].upper())
            response = get_company_news.invoke({"ticker": ticker})

        # Single stock price
        elif len(tickers) == 1 and any(w in msg_lower for w in ["price", "trading", "stock", "range", "worth", "cost"]):
            response = get_stock_price.invoke({"ticker": tickers[0]})

        # Financial term explainer
        elif any(term in msg_lower for term in ["p/e", "market cap", "etf", "dividend", "beta", "short selling", "options", "eps", "bull market", "bear market", "volatility", "index fund", "diversification", "52-week"]):
            term = re.sub(r'(explain|what is|what\'s a|what does|define|mean)', '', msg_lower).strip()
            response = explain_financial_term.invoke({"term": term})

        else:
            response = run_agent(user_message, history)

    except Exception as e:
        response = f"Something went wrong: {str(e)}"

    tool = detect_tool(user_message, response)
    log_exchange(user_message, response, tool)
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": response})
    return "", history, chart

def clear_chat():
    return [], [], None

def export_logs():
    return export_readable_log()

with gr.Blocks(title="Stock Research Chatbot") as demo:
    gr.HTML("""
    <div style='text-align:center; padding: 1rem 0 0.5rem;'>
        <h1 style='font-size:1.6rem; font-weight:600; margin:0;'>📈 Stock Research Chatbot</h1>
        <p style='color:#64748b; margin:0.25rem 0 0; font-size:0.95rem;'>
            Powered by Groq + LangChain · Live prices via yfinance · Portfolio tracking
        </p>
    </div>
    """)

    with gr.Row():
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(label="", height=480)
            with gr.Row():
                msg_input = gr.Textbox(
                    placeholder="Ask about a stock, add to portfolio, or explain a term...",
                    label="", scale=9, autofocus=True, lines=1,
                )
                send_btn = gr.Button("Send", variant="primary", scale=1)
            with gr.Row():
                clear_btn = gr.Button("🗑️ Clear chat", size="sm", variant="secondary")
                export_btn = gr.Button("💾 Export logs", size="sm", variant="secondary")

        with gr.Column(scale=1):
            chart_display = gr.Image(label="Portfolio Diversification", height=300)

    gr.HTML("<p style='text-align:center; color:#94a3b8; font-size:0.8rem; margin:0.5rem 0;'>Try an example:</p>")

    with gr.Row():
        for prompt in EXAMPLE_PROMPTS[:4]:
            gr.Button(prompt, size="sm").click(fn=lambda p=prompt: p, outputs=msg_input)

    with gr.Row():
        for prompt in EXAMPLE_PROMPTS[4:]:
            gr.Button(prompt, size="sm").click(fn=lambda p=prompt: p, outputs=msg_input)

    gr.HTML("<p style='text-align:center; color:#94a3b8; font-size:0.75rem; margin-top:1rem;'>Not financial advice · Data may be delayed</p>")

    msg_input.submit(chat, [msg_input, chatbot], [msg_input, chatbot, chart_display])
    send_btn.click(chat, [msg_input, chatbot], [msg_input, chatbot, chart_display])
    clear_btn.click(clear_chat, outputs=[msg_input, chatbot, chart_display])
    export_btn.click(export_logs)

if __name__ == "__main__":
    demo.launch(share=True)
