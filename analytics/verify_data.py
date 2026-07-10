"""
Quick verification script to check updated metadata and P/VP
"""

import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))
DATABASE_URL = os.getenv('DATABASE_URL')

conn = psycopg2.connect(DATABASE_URL)

print("\n" + "="*80)
print("FUNDS METADATA (from StatusInvest)")
print("="*80)

with conn.cursor(cursor_factory=RealDictCursor) as cur:
    cur.execute("""
        SELECT ticker, cnpj, segment, administrator
        FROM funds
        WHERE ticker IN ('HGLG11', 'KNRI11', 'XPML11', 'VISC11', 'PVBI11')
        ORDER BY ticker
    """)
    
    for row in cur.fetchall():
        print(f"\n{row['ticker']}:")
        print(f"  CNPJ: {row['cnpj']}")
        print(f"  Segmento: {row['segment']}")
        print(f"  Administrador: {row['administrator']}")

print("\n" + "="*80)
print("P/VP INDICATORS (from StatusInvest)")
print("="*80)

with conn.cursor(cursor_factory=RealDictCursor) as cur:
    cur.execute("""
        SELECT f.ticker, i.pvp, i.dividend_yield
        FROM indicators i
        JOIN funds f ON f.id = i.fund_id
        WHERE f.ticker IN ('HGLG11', 'KNRI11', 'XPML11', 'VISC11', 'PVBI11')
        ORDER BY f.ticker
    """)
    
    for row in cur.fetchall():
        print(f"\n{row['ticker']}:")
        print(f"  P/VP: {row['pvp']:.2f}" if row['pvp'] else "  P/VP: None")
        print(f"  Dividend Yield: {row['dividend_yield']:.2f}%" if row['dividend_yield'] else "  Dividend Yield: None")

print("\n" + "="*80)

conn.close()
