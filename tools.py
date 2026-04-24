import yfinance as yf
import requests
import os
from langchain.tools import tool
from datetime import datetime, timedelta


@tool
def get_stock_price(ticker: str) -> str:
    """Get the current stock price and key stats for a given ticker symbol (e.g. AAPL, TSLA, MSFT)."""
    try:
        stock = yf.Ticker(ticker.upper().strip())
        info = stock.info

        name = info.get("longName", ticker.upper())
        price = info.get("currentPrice") or info.get("regularMarketPrice")
        prev_close = info.get("previousClose")
        market_cap = info.get("marketCap")
        pe_ratio = info.get("trailingPE")
        week_high = info.get("fiftyTwoWeekHigh")
        week_low = info.get("fiftyTwoWeekLow")

        if not price:
            return f"Could not retrieve price for {ticker.upper()}. Make sure it's a valid ticker symbol."

        change = price - prev_close if prev_close else 0
        change_pct = (change / prev_close * 100) if prev_close else 0
        direction = "▲" if change >= 0 else "▼"

        mc_str = f"${market_cap / 1e9:.1f}B" if market_cap else "N/A"
        pe_str = f"{pe_ratio:.1f}" if pe_ratio else "N/A"

        return (
            f"📈 {name} ({ticker.upper()})\n"
            f"Price: ${price:.2f}  {direction} {change:+.2f} ({change_pct:+.2f}% today)\n"
            f"52-week range: ${week_low:.2f} – ${week_high:.2f}\n"
            f"Market cap: {mc_str}  |  P/E ratio: {pe_str}"
        )
    except Exception as e:
        return f"Error fetching price for {ticker}: {str(e)}"


@tool
def get_portfolio_summary(tickers: str) -> str:
    """Get a summary of multiple stocks at once. Pass a comma-separated list of ticker symbols (e.g. 'AAPL,MSFT,GOOGL')."""
    ticker_list = [t.strip().upper() for t in tickers.split(",") if t.strip()]
    if not ticker_list:
        return "Please provide at least one ticker symbol."

    results = []
    for ticker in ticker_list[:8]:  # cap at 8 to avoid rate limits
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            price = info.get("currentPrice") or info.get("regularMarketPrice")
            prev_close = info.get("previousClose")
            name = info.get("shortName", ticker)

            if price and prev_close:
                change_pct = (price - prev_close) / prev_close * 100
                direction = "▲" if change_pct >= 0 else "▼"
                results.append(f"  {ticker:<6}  ${price:>8.2f}  {direction} {change_pct:+.2f}%  ({name})")
            else:
                results.append(f"  {ticker:<6}  Price unavailable")
        except Exception:
            results.append(f"  {ticker:<6}  Error fetching data")

    return "Here are the current prices:\n" + "\n".join(results)


@tool
def get_company_news(ticker: str) -> str:
    """Fetch the latest news headlines for a company by ticker symbol (e.g. AAPL, TSLA)."""
    api_key = os.getenv("NEWS_API_KEY")

    try:
        stock = yf.Ticker(ticker.upper().strip())
        company_name = stock.info.get("longName", ticker.upper())
    except Exception:
        company_name = ticker.upper()

    # Try NewsAPI if key is available
    if api_key:
        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": company_name,
                "sortBy": "publishedAt",
                "pageSize": 5,
                "language": "en",
                "apiKey": api_key,
            }
            resp = requests.get(url, params=params, timeout=8)
            data = resp.json()
            articles = data.get("articles", [])
            if articles:
                lines = [f"📰 Latest news for {company_name}:\n"]
                for i, a in enumerate(articles[:5], 1):
                    title = a.get("title", "No title")
                    source = a.get("source", {}).get("name", "Unknown")
                    published = a.get("publishedAt", "")[:10]
                    lines.append(f"{i}. [{source}] {title} ({published})")
                return "\n".join(lines)
        except Exception:
            pass  # fall through to yfinance news

    # Fallback: yfinance built-in news
    try:
        stock = yf.Ticker(ticker.upper().strip())
        news = stock.news
        if not news:
            return f"No recent news found for {ticker.upper()}."

        lines = [f"📰 Latest news for {company_name}:\n"]
        for i, item in enumerate(news[:5], 1):
            content = item.get("content", {})
            title = content.get("title", "No title")
            provider = content.get("provider", {}).get("displayName", "Unknown")
            pub_date = content.get("pubDate", "")[:10]
            lines.append(f"{i}. [{provider}] {title} ({pub_date})")
        return "\n".join(lines)
    except Exception as e:
        return f"Error fetching news for {ticker}: {str(e)}"


@tool
def explain_financial_term(term: str) -> str:
    """Explain a financial or investing term in plain English. Examples: P/E ratio, market cap, ETF, short selling, dividend yield, beta, options, etc."""
    glossary = {
        "p/e ratio": (
            "P/E ratio (Price-to-Earnings) measures how much investors pay per dollar of earnings. "
            "A P/E of 20 means you're paying $20 for every $1 the company earns annually. "
            "High P/E can mean investors expect strong growth; low P/E may mean the stock is undervalued — or struggling."
        ),
        "market cap": (
            "Market capitalization is the total value of all a company's shares. "
            "Formula: share price × total shares outstanding. "
            "Large-cap: >$10B | Mid-cap: $2–10B | Small-cap: <$2B."
        ),
        "etf": (
            "An ETF (Exchange-Traded Fund) is a basket of securities (stocks, bonds, etc.) that trades on an exchange like a single stock. "
            "It gives you instant diversification. For example, SPY tracks the S&P 500 — buying one share gives you exposure to 500 companies."
        ),
        "dividend yield": (
            "Dividend yield = annual dividend per share ÷ stock price, shown as a percentage. "
            "A 3% yield on a $100 stock means you receive $3/year per share just for holding it. "
            "Income investors often prioritize high-yield stocks."
        ),
        "beta": (
            "Beta measures a stock's volatility relative to the overall market. "
            "Beta = 1.0 means it moves with the market. Beta > 1 means more volatile (e.g., beta 1.5 = 50% more volatile). "
            "Beta < 1 means more stable. Negative beta means it tends to move opposite the market (e.g., gold miners)."
        ),
        "short selling": (
            "Short selling is borrowing shares and selling them, hoping to buy them back cheaper later. "
            "If stock is at $100 and you short it, you profit if it drops to $80 (you keep the $20 difference). "
            "Risk: if the price rises, your losses are theoretically unlimited."
        ),
        "options": (
            "Options are contracts giving you the right (not obligation) to buy or sell a stock at a set price before a deadline. "
            "A call option profits when the stock rises. A put option profits when it falls. "
            "They're used for hedging risk or leveraged speculation."
        ),
        "52-week range": (
            "The 52-week range shows a stock's highest and lowest price over the past year. "
            "It gives context for where the current price sits — near its highs, lows, or somewhere in between."
        ),
        "eps": (
            "EPS (Earnings Per Share) = net income ÷ total shares. "
            "It tells you how much profit the company generated per share. "
            "Rising EPS is generally a positive sign; it's used to calculate the P/E ratio."
        ),
        "bull market": (
            "A bull market is a prolonged period of rising stock prices, typically defined as a 20%+ rise from a recent low. "
            "Bull markets reflect investor optimism, strong economic growth, and rising corporate earnings."
        ),
        "bear market": (
            "A bear market is a prolonged decline in stock prices — typically 20%+ from recent highs. "
            "They're often tied to recessions, rising unemployment, or economic uncertainty."
        ),
        "diversification": (
            "Diversification means spreading investments across different assets, sectors, or geographies to reduce risk. "
            "The idea: if one holding drops, others may hold steady or rise, cushioning the blow. "
            "'Don't put all your eggs in one basket.'"
        ),
        "index fund": (
            "An index fund passively tracks a market index like the S&P 500. "
            "It holds all (or most) stocks in that index in proportion to their weight. "
            "Lower fees than actively managed funds; historically outperforms most active managers over time."
        ),
        "volatility": (
            "Volatility measures how much a stock's price fluctuates. "
            "High volatility = big price swings (more risk, more potential reward). "
            "Low volatility = more stable, predictable returns. It's often measured using standard deviation or the VIX index."
        ),
    }

    key = term.lower().strip()
    # exact match
    if key in glossary:
        return f"💡 {term.upper()}\n\n{glossary[key]}"

    # partial match
    for k, v in glossary.items():
        if key in k or k in key:
            return f"💡 {k.upper()}\n\n{v}"

    # fallback — let the LLM handle it via its own knowledge
    return (
        f"I don't have a pre-written definition for '{term}', but here's what it means:\n\n"
        f"(The LLM will fill this in based on its training knowledge — this fallback triggers "
        f"when the term isn't in the local glossary.)"
    )
