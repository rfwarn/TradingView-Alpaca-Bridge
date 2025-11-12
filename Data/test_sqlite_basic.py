#!/usr/bin/env python3
"""
Basic test to verify SQLite functionality works correctly.
This test doesn't require API keys or external dependencies.
"""

import sys
import os

# Add parent directory to path
path = os.path.dirname(__file__)
parent = os.path.abspath(os.path.join(path, os.pardir))
sys.path.append(parent)

from Data import sql


def test_database_init():
    """Test that database initializes correctly."""
    print("Test 1: Initialize database...")
    sql.init_DB()
    print("✓ Database initialized")


def test_add_stock():
    """Test adding a stock."""
    print("\nTest 2: Add a stock...")
    sql.add_stock(
        symbol="MSFT",
        name="Microsoft Corporation",
        account="paper",
        amount=1000.0,
        override=False,
        alpaca_data={
            "fractionable": True,
            "shortable": True,
            "easy_to_borrow": True
        }
    )
    print("✓ Stock added")


def test_get_stock():
    """Test retrieving a stock."""
    print("\nTest 3: Get a stock...")
    stock = sql.get_stock("MSFT")
    assert stock is not None, "Stock should exist"
    assert stock['symbol'] == "MSFT", "Symbol should match"
    assert stock['name'] == "Microsoft Corporation", "Name should match"
    assert stock['account'] == "paper", "Account should match"
    assert stock['amount'] == 1000.0, "Amount should match"
    assert stock['override'] == False, "Override should match"
    assert stock['fractionable'] == True, "Alpaca data should be preserved"
    print(f"✓ Stock retrieved: {stock['symbol']} - {stock['name']}")


def test_update_account():
    """Test updating stock account."""
    print("\nTest 4: Update stock account...")
    result = sql.update_stock_account("MSFT", "real")
    assert result == True, "Update should succeed"
    stock = sql.get_stock("MSFT")
    assert stock['account'] == "real", "Account should be updated"
    print(f"✓ Account updated to: {stock['account']}")


def test_update_amount():
    """Test updating stock amount."""
    print("\nTest 5: Update stock amount...")
    result = sql.update_stock_amount("MSFT", 2000.0)
    assert result == True, "Update should succeed"
    stock = sql.get_stock("MSFT")
    assert stock['amount'] == 2000.0, "Amount should be updated"
    print(f"✓ Amount updated to: {stock['amount']}")


def test_update_override():
    """Test updating stock override."""
    print("\nTest 6: Update stock override...")
    result = sql.update_stock_override("MSFT", True)
    assert result == True, "Update should succeed"
    stock = sql.get_stock("MSFT")
    assert stock['override'] == True, "Override should be updated"
    print(f"✓ Override updated to: {stock['override']}")


def test_add_multiple_stocks():
    """Test adding multiple stocks."""
    print("\nTest 7: Add multiple stocks...")
    stocks_to_add = [
        ("AAPL", "Apple Inc.", "paper", 1500.0),
        ("GOOGL", "Alphabet Inc.", "real", 2500.0),
        ("TSLA", "Tesla Inc.", "", 0.0),
    ]

    for symbol, name, account, amount in stocks_to_add:
        sql.add_stock(symbol, name, account, amount, False, {})

    print("✓ Multiple stocks added")


def test_get_all_stocks():
    """Test retrieving all stocks."""
    print("\nTest 8: Get all stocks...")
    stocks = sql.get_all_stocks()
    assert len(stocks) >= 4, f"Should have at least 4 stocks, got {len(stocks)}"
    symbols = [s['symbol'] for s in stocks]
    assert "MSFT" in symbols, "MSFT should be in list"
    assert "AAPL" in symbols, "AAPL should be in list"
    assert "GOOGL" in symbols, "GOOGL should be in list"
    assert "TSLA" in symbols, "TSLA should be in list"
    print(f"✓ Retrieved {len(stocks)} stocks: {', '.join(symbols)}")


def test_stock_exists():
    """Test checking if stock exists."""
    print("\nTest 9: Check if stock exists...")
    assert sql.stock_exists("MSFT") == True, "MSFT should exist"
    assert sql.stock_exists("INVALID") == False, "INVALID should not exist"
    print("✓ Stock existence check works")


def test_remove_stock():
    """Test removing a stock."""
    print("\nTest 10: Remove a stock...")
    result = sql.remove_stock("TSLA")
    assert result == True, "Remove should succeed"
    assert sql.stock_exists("TSLA") == False, "TSLA should not exist after removal"
    print("✓ Stock removed")


def test_transaction_safety():
    """Test that changes are properly committed."""
    print("\nTest 11: Test transaction safety...")
    # Close and reopen connection to ensure data is persisted
    sql.close_DB()
    stock = sql.get_stock("MSFT")
    assert stock is not None, "Stock should persist after reconnecting"
    assert stock['amount'] == 2000.0, "Amount should persist"
    print("✓ Transactions properly committed")


def main():
    print("=" * 60)
    print("SQLite Database Functionality Tests")
    print("=" * 60)

    try:
        test_database_init()
        test_add_stock()
        test_get_stock()
        test_update_account()
        test_update_amount()
        test_update_override()
        test_add_multiple_stocks()
        test_get_all_stocks()
        test_stock_exists()
        test_remove_stock()
        test_transaction_safety()

        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        return 0

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # Cleanup
        sql.close_DB()


if __name__ == "__main__":
    sys.exit(main())
