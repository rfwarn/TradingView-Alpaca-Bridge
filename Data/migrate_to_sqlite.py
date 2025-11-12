#!/usr/bin/env python3
"""
Migration script to migrate stock data from stocks.json to SQLite database.
This script will:
1. Check if stocks.json exists
2. Read all stocks from stocks.json
3. Import them into the SQLite database
4. Create a backup of stocks.json
5. Optionally remove the old JSON file

Usage:
    python migrate_to_sqlite.py [--remove-json] [--backup-path PATH]
"""

import json
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
import shutil

# Add parent directory to path
path = os.path.dirname(__file__)
parent = os.path.abspath(os.path.join(path, os.pardir))
sys.path.append(parent)

from Data import sql


def backup_json(json_file, backup_path=None):
    """Create a backup of the JSON file."""
    if not os.path.exists(json_file):
        return None

    if backup_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{json_file}.backup_{timestamp}"

    shutil.copy2(json_file, backup_path)
    print(f"✓ Backed up {json_file} to {backup_path}")
    return backup_path


def migrate_json_to_sqlite(json_file, remove_json=False, backup_path=None):
    """Migrate stock data from JSON to SQLite."""
    print("=" * 60)
    print("Stock Data Migration: JSON → SQLite")
    print("=" * 60)

    # Check if JSON file exists
    if not os.path.exists(json_file):
        print(f"\n⚠ No JSON file found at {json_file}")
        print("This is normal if you're starting fresh.")
        print("Initializing empty SQLite database...")
        sql.init_DB()
        print("✓ Database initialized successfully")
        return 0

    # Read JSON data
    print(f"\n📖 Reading data from {json_file}...")
    try:
        with open(json_file, 'r') as f:
            stocks_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"✗ Error reading JSON file: {e}")
        return 1
    except Exception as e:
        print(f"✗ Unexpected error reading JSON: {e}")
        return 1

    if not stocks_data:
        print("⚠ JSON file is empty, nothing to migrate")
        sql.init_DB()
        print("✓ Database initialized successfully")
        return 0

    print(f"✓ Found {len(stocks_data)} stocks to migrate")

    # Initialize database
    print("\n🔧 Initializing SQLite database...")
    sql.init_DB()
    print("✓ Database initialized")

    # Migrate each stock
    print("\n📦 Migrating stocks...")
    success_count = 0
    error_count = 0

    for stock in stocks_data:
        try:
            symbol = stock.get('symbol', '')
            name = stock.get('name', '')
            account = stock.get('account', '')
            amount = stock.get('amount', 0)
            override = stock.get('override', False)

            # Extract Alpaca-specific data
            alpaca_data = {k: v for k, v in stock.items()
                          if k not in ['symbol', 'name', 'account', 'amount', 'override']}

            # Add to database
            sql.add_stock(
                symbol=symbol,
                name=name,
                account=account,
                amount=amount,
                override=override,
                alpaca_data=alpaca_data
            )

            print(f"  ✓ Migrated {symbol}")
            success_count += 1

        except Exception as e:
            print(f"  ✗ Error migrating {stock.get('symbol', 'UNKNOWN')}: {e}")
            error_count += 1

    # Print summary
    print("\n" + "=" * 60)
    print("Migration Summary")
    print("=" * 60)
    print(f"Successfully migrated: {success_count} stocks")
    if error_count > 0:
        print(f"Errors: {error_count} stocks")

    # Verify migration
    print("\n🔍 Verifying migration...")
    db_stocks = sql.get_all_stocks()
    print(f"✓ Database now contains {len(db_stocks)} stocks")

    # Create backup
    if success_count > 0:
        print("\n💾 Creating backup of JSON file...")
        backup_file = backup_json(json_file, backup_path)

        if remove_json and backup_file:
            print(f"\n🗑️  Removing original JSON file...")
            os.remove(json_file)
            print(f"✓ Removed {json_file}")
            print(f"  (Backup preserved at {backup_file})")

    print("\n✅ Migration complete!")
    print("=" * 60)

    return 0 if error_count == 0 else 1


def main():
    parser = argparse.ArgumentParser(
        description='Migrate stock data from JSON to SQLite database'
    )
    parser.add_argument(
        '--remove-json',
        action='store_true',
        help='Remove the JSON file after successful migration (backup will be kept)'
    )
    parser.add_argument(
        '--backup-path',
        type=str,
        help='Custom path for the JSON backup file'
    )
    parser.add_argument(
        '--json-file',
        type=str,
        default=os.path.join(path, 'stocks.json'),
        help='Path to the JSON file to migrate (default: Data/stocks.json)'
    )

    args = parser.parse_args()

    try:
        return migrate_json_to_sqlite(
            args.json_file,
            remove_json=args.remove_json,
            backup_path=args.backup_path
        )
    except KeyboardInterrupt:
        print("\n\n⚠ Migration cancelled by user")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error during migration: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
