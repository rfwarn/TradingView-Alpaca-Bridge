import sqlite3
# import os, sys
from pathlib import Path

__version__ = "1.0.0"

# Get parent directory
current_file_path = Path(__file__)
# path = os.path.dirname(__file__)
# parent = os.path.abspath(os.path.join(path, os.pardir))
# sys.path.append(parent)

# conn = sqlite3.connect(os.path.join(path + os.sep + "stocks.db"))
conn = sqlite3.connect(current_file_path.parent / "stocks.db")

c = conn.cursor()


def init_DB():
    # init DB if needed
    c.execute(
        """ CREATE TABLE IF NOT EXISTS stocks (symbol TEXT PRIMARY KEY, name TEXT)"""
    )
    conn.commit()


def close_DB():
    conn.close()


if __name__ == "__main__":
    init_DB()
    close_DB()
