import json
import os
from datetime import datetime

LOG_FILE = "conversation_logs.jsonl"


def log_exchange(user_message: str, bot_response: str, tool_used: str = None):
    """Append a single conversation exchange to the log file as a JSON line."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "user": user_message,
        "bot": bot_response,
        "tool_used": tool_used,
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def detect_tool(user_message: str, bot_response: str) -> str:
    """Heuristically label which tool was likely triggered, for the log."""
    msg = user_message.lower()
    resp = bot_response.lower()

    if "📊" in bot_response and ("," in user_message or "and" in msg):
        return "get_portfolio_summary"
    if "📈" in bot_response or "price" in msg or "trading" in msg or "52-week" in resp:
        return "get_stock_price"
    if "📰" in bot_response or "news" in msg or "headline" in msg:
        return "get_company_news"
    if "💡" in bot_response or "explain" in msg or "what is" in msg or "what does" in msg or "what's a" in msg:
        return "explain_financial_term"
    return "general"


def export_readable_log(output_file: str = "conversation_logs_readable.txt"):
    """Convert the JSONL log into a human-readable text file for the README."""
    if not os.path.exists(LOG_FILE):
        return "No log file found."

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if not lines:
        return "Log file is empty."

    sessions = []
    current_session = []
    prev_time = None

    for line in lines:
        entry = json.loads(line.strip())
        ts = datetime.fromisoformat(entry["timestamp"])

        # Start a new session if gap > 30 minutes
        if prev_time and (ts - prev_time).seconds > 1800:
            sessions.append(current_session)
            current_session = []

        current_session.append(entry)
        prev_time = ts

    if current_session:
        sessions.append(current_session)

    output_lines = []
    for i, session in enumerate(sessions, 1):
        output_lines.append(f"{'='*60}")
        output_lines.append(f"Session {i}  —  {session[0]['timestamp'][:16]}")
        output_lines.append(f"{'='*60}\n")
        for entry in session:
            output_lines.append(f"[Tool: {entry.get('tool_used', 'general')}]")
            output_lines.append(f"User: {entry['user']}")
            output_lines.append(f"Bot:  {entry['bot']}")
            output_lines.append("")
        output_lines.append("")

    text = "\n".join(output_lines)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(text)

    return f"Exported {sum(len(s) for s in sessions)} exchanges across {len(sessions)} sessions to {output_file}"
