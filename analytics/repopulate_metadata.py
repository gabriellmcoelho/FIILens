"""
Repopulate fund metadata and P/VP from StatusInvest
Automatically collects and updates: CNPJ, segment, administrator, P/VP
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from typing import List, Dict, Optional
from collectors.metadata_collector import StatusInvestCollector

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    logger.error("DATABASE_URL not found in .env file!")
    sys.exit(1)

# FIIs being tracked
TRACKED_FIIS = ['HGLG11', 'KNRI11', 'XPML11', 'VISC11', 'PVBI11']


def get_db_connection():
    """Create database connection"""
    return psycopg2.connect(DATABASE_URL)


def get_fund_id(conn, ticker: str) -> Optional[str]:
    """Get fund ID from database by ticker"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT id FROM funds 
            WHERE ticker = %s
        """, (ticker,))
        result = cur.fetchone()
        return result['id'] if result else None


def update_fund_metadata(conn, fund_id: str, ticker: str, data: Dict):
    """Update fund table with collected metadata"""
    with conn.cursor() as cur:
        # Update funds table
        cur.execute("""
            UPDATE funds
            SET 
                cnpj = %s,
                segment = %s,
                administrator = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (
            data.get('cnpj'),
            data.get('segment'),
            data.get('administrator'),
            fund_id
        ))
        
        logger.info(f"  ✓ Updated fund metadata for {ticker}")


def update_pvp_indicator(conn, fund_id: str, ticker: str, pvp: float):
    """Update or create P/VP indicator in indicators table"""
    with conn.cursor() as cur:
        # Try to update existing indicator first
        cur.execute("""
            UPDATE indicators
            SET 
                pvp = %s,
                last_update = CURRENT_TIMESTAMP
            WHERE fund_id = %s
        """, (pvp, fund_id))
        
        # Check if update affected any rows
        if cur.rowcount == 0:
            # No existing indicator, create one
            cur.execute("""
                INSERT INTO indicators (id, fund_id, pvp, last_update)
                VALUES (gen_random_uuid(), %s, %s, CURRENT_TIMESTAMP)
            """, (fund_id, pvp))
            logger.info(f"  ✓ Created new indicator with P/VP for {ticker}")
        else:
            logger.info(f"  ✓ Updated P/VP indicator for {ticker}")


def main():
    """Main repopulation function"""
    logger.info("=" * 60)
    logger.info("Starting metadata and P/VP repopulation from StatusInvest")
    logger.info("=" * 60)
    
    # Initialize collector
    collector = StatusInvestCollector()
    
    # Collect data for all tracked FIIs
    logger.info(f"\n📊 Collecting data for {len(TRACKED_FIIS)} FIIs...")
    all_data = collector.collect_all_fiis(TRACKED_FIIS)
    
    # Connect to database
    logger.info("\n💾 Connecting to database...")
    conn = get_db_connection()
    conn.autocommit = False  # Use transactions
    
    try:
        updated_funds = 0
        updated_pvp = 0
        
        for ticker, data in all_data.items():
            if not data:
                logger.warning(f"\n⚠️  Skipping {ticker} - no data collected")
                continue
            
            logger.info(f"\n📝 Processing {ticker}...")
            
            # Get fund ID
            fund_id = get_fund_id(conn, ticker)
            if not fund_id:
                logger.warning(f"  ⚠️  Fund {ticker} not found in database, skipping")
                continue
            
            # Update fund metadata
            if any([data.get('cnpj'), data.get('segment'), data.get('administrator')]):
                update_fund_metadata(conn, fund_id, ticker, data)
                updated_funds += 1
            
            # Update P/VP indicator
            if data.get('pvp') is not None:
                update_pvp_indicator(conn, fund_id, ticker, data['pvp'])
                updated_pvp += 1
        
        # Commit transaction
        conn.commit()
        logger.info("\n" + "=" * 60)
        logger.info("✅ Repopulation completed successfully!")
        logger.info(f"   - Updated {updated_funds} fund records")
        logger.info(f"   - Updated {updated_pvp} P/VP indicators")
        logger.info("=" * 60)
        
    except Exception as e:
        conn.rollback()
        logger.error(f"\n❌ Error during repopulation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        conn.close()


if __name__ == '__main__':
    main()
