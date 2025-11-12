import sqlite3
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
import threading

__version__ = "2.0.0"

# Get parent directory
current_file_path = Path(__file__)
db_path = current_file_path.parent / "stocks.db"

# Thread-local storage for database connections
_thread_local = threading.local()


def get_connection():
    """Get a thread-local database connection."""
    if not hasattr(_thread_local, "conn"):
        _thread_local.conn = sqlite3.connect(str(db_path), check_same_thread=False)
        _thread_local.conn.row_factory = sqlite3.Row
    return _thread_local.conn


def get_cursor():
    """Get a cursor from the thread-local connection."""
    return get_connection().cursor()


def init_DB():
    """Initialize the database schema if needed."""
    conn = get_connection()
    c = conn.cursor()

    # Create stocks table with full schema
    c.execute("""
        CREATE TABLE IF NOT EXISTS stocks (
            symbol TEXT PRIMARY KEY,
            name TEXT,
            account TEXT DEFAULT '',
            amount REAL DEFAULT 0,
            override INTEGER DEFAULT 0,
            alpaca_data TEXT
        )
    """)

    # Create index for faster queries
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_account ON stocks(account)
    """)

    conn.commit()


def add_stock(symbol: str, name: str, account: str = "", amount: float = 0,
              override: bool = False, alpaca_data: Dict[str, Any] = None) -> None:
    """Add or update a stock in the database."""
    conn = get_connection()
    c = conn.cursor()

    # Store additional Alpaca data as JSON
    alpaca_json = json.dumps(alpaca_data) if alpaca_data else "{}"

    c.execute("""
        INSERT OR REPLACE INTO stocks (symbol, name, account, amount, override, alpaca_data)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (symbol.upper(), name, account, amount, int(override), alpaca_json))

    conn.commit()


def get_stock(symbol: str) -> Optional[Dict[str, Any]]:
    """Get a single stock by symbol."""
    c = get_cursor()
    c.execute("SELECT * FROM stocks WHERE symbol = ?", (symbol.upper(),))
    row = c.fetchone()

    if row:
        stock = dict(row)
        # Parse alpaca_data from JSON
        if stock.get('alpaca_data'):
            alpaca_data = json.loads(stock['alpaca_data'])
            stock.update(alpaca_data)
        stock['override'] = bool(stock['override'])
        del stock['alpaca_data']
        return stock
    return None


def get_all_stocks() -> List[Dict[str, Any]]:
    """Get all stocks from the database."""
    c = get_cursor()
    c.execute("SELECT * FROM stocks ORDER BY symbol")
    rows = c.fetchall()

    stocks = []
    for row in rows:
        stock = dict(row)
        # Parse alpaca_data from JSON
        if stock.get('alpaca_data'):
            alpaca_data = json.loads(stock['alpaca_data'])
            stock.update(alpaca_data)
        stock['override'] = bool(stock['override'])
        del stock['alpaca_data']
        stocks.append(stock)

    return stocks


def update_stock_account(symbol: str, account: str) -> bool:
    """Update the account preference for a stock."""
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        UPDATE stocks SET account = ? WHERE symbol = ?
    """, (account, symbol.upper()))

    conn.commit()
    return c.rowcount > 0


def update_stock_amount(symbol: str, amount: float) -> bool:
    """Update the amount for a stock."""
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        UPDATE stocks SET amount = ? WHERE symbol = ?
    """, (amount, symbol.upper()))

    conn.commit()
    return c.rowcount > 0


def update_stock_override(symbol: str, override: bool) -> bool:
    """Update the override preference for a stock."""
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        UPDATE stocks SET override = ? WHERE symbol = ?
    """, (int(override), symbol.upper()))

    conn.commit()
    return c.rowcount > 0


def remove_stock(symbol: str) -> bool:
    """Remove a stock from the database."""
    conn = get_connection()
    c = conn.cursor()

    c.execute("DELETE FROM stocks WHERE symbol = ?", (symbol.upper(),))

    conn.commit()
    return c.rowcount > 0


def stock_exists(symbol: str) -> bool:
    """Check if a stock exists in the database."""
    c = get_cursor()
    c.execute("SELECT 1 FROM stocks WHERE symbol = ?", (symbol.upper(),))
    return c.fetchone() is not None


def close_DB():
    """Close the database connection."""
    if hasattr(_thread_local, "conn"):
        _thread_local.conn.close()
        del _thread_local.conn


if __name__ == "__main__":
    init_DB()
    print("Database initialized successfully")
    close_DB()
