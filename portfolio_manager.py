import csv
import os
import matplotlib.pyplot as plt
from datetime import datetime
import yfinance as yf

PORTFOLIO_FILE = "portfolio.csv"

def get_current_price(ticker: str) -> float:
    try:
        info = yf.Ticker(ticker).info
        return info.get("currentPrice") or info.get("regularMarketPrice") or 0
    except:
        return 0

def load_portfolio():
    if not os.path.exists(PORTFOLIO_FILE):
        return []
    with open(PORTFOLIO_FILE, "r") as f:
        reader = csv.DictReader(f)
        return list(reader)

def save_portfolio(holdings):
    with open(PORTFOLIO_FILE, "w", newline="") as f:
        fieldnames = ["ticker", "target_price", "shares", "invested", "added_date"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(holdings)

def add_to_portfolio(ticker: str, invested: float) -> str:
    ticker = ticker.upper().strip()
    current_price = get_current_price(ticker)
    
    if not current_price:
        return f"Could not fetch current price for {ticker}. Please check the ticker symbol."
    
    shares = invested / current_price
    holdings = load_portfolio()

    for h in holdings:
        if h["ticker"] == ticker:
            h["target_price"] = str(round(current_price, 2))
            h["shares"] = str(round(shares, 4))
            h["invested"] = str(round(invested, 2))
            save_portfolio(holdings)
            return (
                f"✅ Updated {ticker} in your portfolio\n"
                f"   Investment: ${invested:,.2f}\n"
                f"   Current price: ${current_price:.2f}\n"
                f"   Shares you'd get: {shares:.4f}"
            )

    holdings.append({
        "ticker": ticker,
        "target_price": str(round(current_price, 2)),
        "shares": str(round(shares, 4)),
        "invested": str(round(invested, 2)),
        "added_date": datetime.now().strftime("%Y-%m-%d"),
    })
    save_portfolio(holdings)
    return (
        f"✅ Added {ticker} to your portfolio\n"
        f"   Investment: ${invested:,.2f}\n"
        f"   Current price: ${current_price:.2f}\n"
        f"   Shares you'd get: {shares:.4f}"
    )

def view_portfolio() -> str:
    holdings = load_portfolio()
    if not holdings:
        return "Your portfolio is empty. Add stocks with: 'Add AAPL with $2000'"

    lines = ["📊 Your Portfolio:\n"]
    lines.append(f"{'TICKER':<8} {'INVESTED':>10} {'PRICE':>8} {'SHARES':>8} {'VALUE':>10} {'GAIN/LOSS':>10}")
    lines.append("-" * 60)

    total_invested = 0
    total_value = 0

    for h in holdings:
        ticker = h["ticker"]
        invested = float(h.get("invested", 0))
        shares = float(h["shares"])
        current_price = get_current_price(ticker)
        current_value = shares * current_price if current_price else 0
        gain_loss = current_value - invested
        gain_pct = (gain_loss / invested * 100) if invested else 0
        arrow = "▲" if gain_loss >= 0 else "▼"

        total_invested += invested
        total_value += current_value

        lines.append(
            f"{ticker:<8} ${invested:>9,.2f} ${current_price:>7.2f} {shares:>8.4f} ${current_value:>9,.2f} {arrow}{abs(gain_pct):>7.1f}%"
        )

    lines.append("-" * 60)
    total_gain = total_value - total_invested
    total_pct = (total_gain / total_invested * 100) if total_invested else 0
    arrow = "▲" if total_gain >= 0 else "▼"
    lines.append(f"{'TOTAL':<8} ${total_invested:>9,.2f} {'':>8} {'':>8} ${total_value:>9,.2f} {arrow}{abs(total_pct):>7.1f}%")

    return "\n".join(lines)

def remove_from_portfolio(ticker: str) -> str:
    holdings = load_portfolio()
    ticker = ticker.upper().strip()
    new_holdings = [h for h in holdings if h["ticker"] != ticker]
    if len(new_holdings) == len(holdings):
        return f"{ticker} not found in your portfolio."
    save_portfolio(new_holdings)
    return f"✅ Removed {ticker} from your portfolio."

def generate_pie_chart() -> str:
    holdings = load_portfolio()
    if not holdings:
        return None

    labels = [h["ticker"] for h in holdings]
    sizes = [float(h.get("invested", 0)) for h in holdings]

    if sum(sizes) == 0:
        return None

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90,
           colors=plt.cm.Set3.colors[:len(labels)])
    ax.set_title("Portfolio Diversification\n(by $ invested)", fontsize=13, fontweight='bold')
    plt.tight_layout()

    chart_path = "portfolio_chart.png"
    plt.savefig(chart_path, dpi=150, bbox_inches='tight')
    plt.close()
    return chart_path
