"""
Repopulate dividends table with real data from Funds Explorer
Replaces random dividend data with actual historical dividends
"""

import os
import sys
import logging
from datetime import datetime
from typing import List, Dict

from sqlalchemy import create_engine, text
from collectors.dividend_collector import DividendCollector

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set. Please set it before running this script.")

engine = create_engine(DATABASE_URL)

# FIIs to process
TRACKED_FIIS = ['HGLG11', 'KNRI11', 'XPML11', 'VISC11', 'PVBI11']

class DividendRepopulator:
    """Repopulate dividends table with real data"""
    
    def __init__(self):
        self.collector = DividendCollector()
        self.engine = engine
    
    def repopulate_dividends(self, tickers: List[str], months: int = 12) -> int:
        """
        Delete random dividends and insert real ones
        
        Args:
            tickers: List of FII tickers to process
            months: Number of months of history to collect
            
        Returns:
            Number of dividend records inserted
        """
        logger.info("="*60)
        logger.info("Starting Dividend Repopulation")
        logger.info("="*60)
        
        # Collect real dividend data
        logger.info(f"\n📊 Collecting real dividend data for {len(tickers)} FIIs...")
        dividend_data = self.collector.collect_all_fiis(tickers, months)
        
        # Display summary
        total_dividends = sum(len(divs) for divs in dividend_data.values())
        logger.info(f"\n✅ Collected {total_dividends} real dividend records")
        for ticker, divs in dividend_data.items():
            logger.info(f"  {ticker}: {len(divs)} dividends")
        
        if total_dividends == 0:
            logger.warning("❌ No dividend data collected. Scraping may have failed.")
            logger.warning("   Check if Funds Explorer website structure has changed.")
            return 0
        
        # Repopulate database
        inserted_count = 0
        
        logger.info(f"\n🗑️  Deleting old random dividend data...")
        
        # Get fund IDs first
        fund_ids = {}
        with self.engine.connect() as conn:
            for ticker in tickers:
                result = conn.execute(
                    text("SELECT id FROM funds WHERE ticker = :ticker"),
                    {"ticker": ticker}
                ).fetchone()
                
                if result:
                    fund_ids[ticker] = result[0]
                else:
                    logger.warning(f"⚠️  Fund {ticker} not found in database")
        
        # Delete old dividends (one FII at a time)
        for ticker, fund_id in fund_ids.items():
            with self.engine.begin() as conn:
                result = conn.execute(
                    text("DELETE FROM dividends WHERE fund_id = :fund_id"),
                    {"fund_id": fund_id}
                )
                logger.info(f"  Deleted {result.rowcount} old records for {ticker}")
        
        logger.info(f"\n💾 Inserting real dividend data...")
        
        # Insert real dividends (one FII at a time)
        for ticker, dividends in dividend_data.items():
            if ticker not in fund_ids:
                continue
            
            fund_id = fund_ids[ticker]
            fii_inserted = 0
            
            with self.engine.begin() as conn:
                for div in dividends:
                    conn.execute(
                        text("""
                            INSERT INTO dividends (id, fund_id, payment_date, ex_date, value)
                            VALUES (gen_random_uuid(), :fund_id, :payment_date, :ex_date, :value)
                        """),
                        {
                            "fund_id": fund_id,
                            "payment_date": div['payment_date'],
                            "ex_date": div['ex_date'],
                            "value": div['value']
                        }
                    )
                    fii_inserted += 1
            
            inserted_count += fii_inserted
            logger.info(f"  ✅ {ticker}: {fii_inserted} real dividends inserted")
        
        # Recalculate dividend yield for each FII
        logger.info(f"\n📊 Recalculating dividend yields...")
        
        for ticker, fund_id in fund_ids.items():
            with self.engine.begin() as conn:
                # Get current price
                price_result = conn.execute(
                    text("SELECT price FROM indicators WHERE fund_id = :fund_id"),
                    {"fund_id": fund_id}
                ).fetchone()
                
                if not price_result or not price_result[0]:
                    logger.warning(f"  ⚠️  {ticker}: No price found, skipping dividend yield calculation")
                    continue
                
                current_price = float(price_result[0])
                
                # Calculate 12-month dividend sum
                dividend_sum_result = conn.execute(
                    text("""
                        SELECT COALESCE(SUM(value), 0)
                        FROM dividends
                        WHERE fund_id = :fund_id
                        AND payment_date >= NOW() - INTERVAL '12 months'
                    """),
                    {"fund_id": fund_id}
                ).fetchone()
                
                dividend_sum = float(dividend_sum_result[0])
                
                # Calculate yield
                if current_price > 0:
                    dividend_yield = (dividend_sum / current_price) * 100
                else:
                    dividend_yield = 0
                
                # Update indicators table
                conn.execute(
                    text("""
                        UPDATE indicators
                        SET dividend_yield = :dividend_yield,
                            last_update = NOW()
                        WHERE fund_id = :fund_id
                    """),
                    {
                        "fund_id": fund_id,
                        "dividend_yield": round(dividend_yield, 2)
                    }
                )
                
                logger.info(f"  ✅ {ticker}: Dividend Yield = {dividend_yield:.2f}% (Price: R$ {current_price:.2f}, 12m Dividends: R$ {dividend_sum:.2f})")
        
        logger.info("\n" + "="*60)
        logger.info(f"✅ Dividend Repopulation Complete!")
        logger.info(f"   Total real dividends inserted: {inserted_count}")
        logger.info("="*60)
        
        return inserted_count


def main():
    """Main execution function"""
    try:
        repopulator = DividendRepopulator()
        
        # Repopulate dividends with 12 months of history
        inserted = repopulator.repopulate_dividends(TRACKED_FIIS, months=12)
        
        if inserted > 0:
            logger.info("\n✅ SUCCESS: Database repopulated with real dividend data")
            sys.exit(0)
        else:
            logger.warning("\n⚠️  WARNING: No dividends were inserted")
            logger.warning("    This may indicate scraping issues")
            logger.warning("    Check logs above for details")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
