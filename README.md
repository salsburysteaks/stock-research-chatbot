# Stock Research Chatbot

## Overview

A conversational stock research assistant built with LangChain, Groq, and Gradio. It lets you look up live stock prices, read company news, understand financial terms, and track a personal investment portfolio — all in one place, without switching between tabs.

## The Problem

Before buying a stock, I found myself jumping between Yahoo Finance for the price, Google News for headlines, Investopedia for terms I did not recognize, and some random forum trying to figure out if the valuation made sense. It was slow, scattered, and I would still feel unsure. I built this bot to collapse all of that into one conversation so I can go from "should I look into AAPL?" to actually understanding it in under two minutes. The portfolio tracker adds a layer that apps like Robinhood do not have: you can set a dollar amount you want to invest and instantly see how many shares that buys at the current price.

## How It Works

The bot uses a routing system in app.py that reads the user message and decides which tool to call directly, without relying on the LLM to route correctly. Here is the decision flow:

```
User message
     |
     v
Does it contain 2+ tickers?         --> get_portfolio_summary (live prices for multiple stocks)
Does it mention "news"?             --> get_company_news (headlines via yfinance)
Does it mention a price keyword?    --> get_stock_price (live price, P/E, market cap, 52wk range)
Does it mention a financial term?   --> explain_financial_term (plain English definitions)
Does it say "add" + dollar amount?  --> add_to_portfolio (CSV write, calculates shares)
Does it say "show my portfolio"?    --> view_portfolio + pie chart (CSV read, current values)
Does it say "remove"?               --> remove_from_portfolio (CSV delete)
Everything else                     --> LLM via Groq (general questions)
```

Tools and data sources:

1. get_stock_price: yfinance API, returns live price, daily change, 52 week range, market cap, P/E ratio
2. get_company_news: yfinance news feed, returns up to 5 recent headlines with source and date
3. explain_financial_term: local glossary with plain English definitions for 14 common investing terms
4. get_portfolio_summary: yfinance API, returns a side by side price comparison for multiple tickers
5. portfolio_manager: reads and writes to portfolio.csv, calculates share count from dollar investment, tracks gain/loss, generates a pie chart showing portfolio diversification

## Key Findings and What I Learned

The biggest surprise was how much LangChain has changed across versions. Functions like AgentExecutor and ConversationBufferWindowMemory that appear in most tutorials were removed or moved in the latest releases, which caused a lot of debugging. I ended up bypassing the LLM for tool routing entirely and writing direct routing logic in app.py instead. This actually made the bot more reliable and faster because the LLM was summarizing tool output instead of displaying it.

The most interesting thing I learned is that free LLMs like Llama via Groq are not great at following structured output instructions. They tend to paraphrase results rather than display them verbatim. For a production app I would use a stronger model. I would also swap yfinance news for a real time API like Finnhub or NewsAPI to get more current headlines.

## Sample Conversations

### Tool 1: Live Stock Price Lookup

User: What is the stock price of AAPL right now

Bot: 📈 Apple Inc. (AAPL)
Price: $270.07 ▼ -3.36 (-1.23% today)
52-week range: $193.25 – $288.62
Market cap: $3,964.9B | P/E ratio: 34.2

---

### Tool 2: Company News

User: What's the latest news on AAPL?

Bot: 📰 Latest news for Apple Inc.:

1. [24/7 Wall St.] Apple vs. Microsoft: One Quietly Grew Its Dividend 900% in 10 Years (2026-04-24)
2. [Barrons.com] Apple Got the CEO It Wants. The Stock Gets the One It Needs. (2026-04-24)
3. [Investor's Business Daily] Stock Market Holds Near Highs As Intel Leads Chip Surge; Apple, Tesla, ServiceNow In Focus (2026-04-24)

---

### Tool 3: Financial Term Explainer

User: Explain what a P/E ratio is

Bot: 💡 P/E RATIO

P/E ratio (Price-to-Earnings) measures how much investors pay per dollar of earnings. A P/E of 20 means you're paying $20 for every $1 the company earns annually. High P/E can mean investors expect strong growth; low P/E may mean the stock is undervalued or struggling.

---

### Tool 4: Portfolio Tracker

User: Add AAPL with $2000

Bot: ✅ Added AAPL to your portfolio
   Investment: $2,000.00
   Current price: $270.21
   Shares you'd get: 7.4017

User: Add TSLA with $1500

Bot: ✅ Added TSLA to your portfolio
   Investment: $1,500.00
   Current price: $375.63
   Shares you'd get: 3.9933

User: Show my portfolio

Bot: 📊 Your Portfolio:

TICKER     INVESTED    PRICE   SHARES      VALUE  GAIN/LOSS
------------------------------------------------------------
AAPL     $ 2,000.00 $ 270.19   7.4017 $ 1,999.87 ▼    0.0%
TSLA     $ 1,500.00 $ 375.55   3.9933 $ 1,499.69 ▼    0.0%
------------------------------------------------------------
TOTAL    $ 3,500.00                   $ 3,499.56 ▼    0.0%

## How to Run

### Requirements

Python 3.12 and a Groq API key (free at console.groq.com)

### Setup

```bash
git clone https://github.com/your-username/stock-chatbot.git
cd stock-chatbot
python -m venv ~/stock-env
source ~/stock-env/bin/activate
pip install langchain langchain-core langchain-community langchain-google-genai langgraph langchain-groq yfinance gradio requests python-dotenv matplotlib
cp .env.example .env
```

Open .env and add your key:

```
GROQ_API_KEY=your_key_here
```

### Launch

```bash
source ~/stock-env/bin/activate
python app.py
```

Open http://127.0.0.1:7860 in your browser. To get a public shareable link, the app already runs with share=True.

### Deploy to Hugging Face Spaces

1. Create a new Gradio Space at huggingface.co/spaces
2. Push this repo to the Space
3. Add GROQ_API_KEY as a secret in Settings > Variables and secrets
4. The Space auto-builds from requirements.txt and launches app.py

## Who Would Care

This bot is useful for anyone who is learning to invest and feels overwhelmed by the number of tools and terms involved. It is especially relevant for college students, young professionals, or anyone just getting started with individual stock research who wants a single conversational interface instead of five open browser tabs. Financial advisors or educators could also use it as a teaching tool to explain concepts like P/E ratios or portfolio diversification in real time.

---

Live demo: [Add your Hugging Face Spaces link here]

Not financial advice. Data may be delayed. Built with LangChain and Groq.
