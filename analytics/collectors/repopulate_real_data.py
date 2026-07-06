"""
Repopulate database with real historical data from Yahoo Finance
Cleans old random data and inserts real market data
"""

import logging
import requests
import sys
import os
from datetime import datetime
from typing import List, Dict
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://neondb_owner:npg_71rnXEbqQvGV@ep-small-mode-acmvis8n.sa-east-1.aws.neon.tech/neondb?sslmode=require')
engine = create_engine(DATABASE_URL)

TRACKED_FIIS = ['HGLG11', 'KNRI11', 'XPML11', 'VISC11', 'PVBI11']

class RealDataRepopulator:
    """Repopulate database with real historical data"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.yahoo_base_url = "https://query1.finance.yahoo.com/v8/finance/chart"
        
    def fetch_historical_data(self, ticker: str, range_period: str = '3mo') -> List[Dict]:
        """
        Fetch historical price data from Yahoo Finance
        
        Args:
            ticker: FII ticker (e.g., 'HGLG11')
            range_period: Time range ('1mo', '3mo', '6mo', '1y', etc.)
            
        Returns:
            List of dicts with date and price
        """
        try:
            yahoo_ticker = f"{ticker}.SA"
            url = f"{self.yahoo_base_url}/{yahoo_ticker}"
            
            params = {
                'range': range_period,
                'interval': '1d',
                'includePrePost': 'false'
            }
            
            response = self.session.get(url, params=params, timeout=15)
            
            if response.status_code != 200:
                logger.error(f"❌ Yahoo Finance returned {response.status_code} for {ticker}")
                return []
            
            data = response.json()
            
            if 'chart' not in data or 'result' not in data['chart']:
                logger.error(f"❌ Invalid response structure for {ticker}")
                return []
            
            result = data['chart']['result'][0]
            timestamps = result.get('timestamp', [])
            quotes = result.get('indicators', {}).get('quote', [{}])[0]
            
            close_prices = quotes.get('close', [])
            volumes = quotes.get('volume', [])
            
            historical_data = []
            
            for i, timestamp in enumerate(timestamps):
                if i < len(close_prices) and close_prices[i] is not None:
                    date = datetime.fromtimestamp(timestamp)
                    price = close_prices[i]
                    volume = volumes[i] if i < len(volumes) and volumes[i] is not None else 0
                    
                    historical_data.append({
                        'date': date.strftime('%Y-%m-%d'),
                        'price': round(price, 2),
                        'volume': int(volume) if volume else 0
                    })
            
            logger.info(f"✅ {ticker}: Fetched {len(historical_data)} days of historical data")
            return historical_data
            
        except Exception as e:
            logger.error(f"❌ Error fetching historical data for {ticker}: {e}")
            return []
    
    def repopulate_database(self, tickers: List[str]):
        """
        Clean old data and repopulate with real historical data
        
        Args:
            tickers: List of FII tickers to repopulate
        """
        logger.info("=" * 60)
        logger.info("🔄 STARTING DATABASE REPOPULATION WITH REAL DATA")
        logger.info("=" * 60)
        
        with engine.begin() as db:
            try:
                for ticker in tickers:
                    logger.info(f"\n📊 Processing {ticker}...")
                    
                    # 1. Get fund_id
                    fund_query = text("SELECT id FROM funds WHERE ticker = :ticker")
                    result = db.execute(fund_query, {'ticker': ticker})
                    fund_row = result.fetchone()
                    
                    if not fund_row:
                        logger.warning(f"⚠️  Fund {ticker} not found in database, skipping...")
                        continue
                    
                    fund_id = fund_row[0]
                    
                    # 2. Fetch real historical data
                    historical_data = self.fetch_historical_data(ticker, range_period='3mo')
                    
                    if not historical_data:
                        logger.error(f"❌ No data fetched for {ticker}, skipping...")
                        continue
                    
                    # 3. Delete old historical prices
                    delete_query = text("DELETE FROM historical_prices WHERE fund_id = :fund_id")
                    result = db.execute(delete_query, {'fund_id': fund_id})
                    deleted_count = result.rowcount
                    logger.info(f"🗑️  Deleted {deleted_count} old price records")
                    
                    # 4. Insert real historical prices
                    insert_query = text("""
                        INSERT INTO historical_prices (id, fund_id, date, price, volume)
                        VALUES (gen_random_uuid(), :fund_id, :date, :price, :volume)
                    """)
                    
                    inserted = 0
                    for data_point in historical_data:
                        db.execute(insert_query, {
                            'fund_id': fund_id,
                            'date': data_point['date'],
                            'price': data_point['price'],
                            'volume': data_point['volume']
                        })
                        inserted += 1
                    
                    logger.info(f"✅ Inserted {inserted} real price records")
                    
                    # 5. Update indicators with latest price
                    latest = historical_data[-1]  # Most recent data point
                    
                    # Calculate dividend yield and P/VP (using estimates for now)
                    dividend_yield = self._estimate_dividend_yield(ticker)
                    pvp = self._estimate_pvp(ticker)
                    market_cap = self._estimate_market_cap(ticker, latest['price'])
                    
                    update_indicators = text("""
                        UPDATE indicators
                        SET price = :price,
                            volume = :volume,
                            dividend_yield = :dividend_yield,
                            pvp = :pvp,
                            liquidity = :liquidity,
                            market_cap = :market_cap,
                            last_update = NOW()
                        WHERE fund_id = :fund_id
                    """)
                    
                    db.execute(update_indicators, {
                        'fund_id': fund_id,
                        'price': latest['price'],
                        'volume': latest['volume'],
                        'dividend_yield': dividend_yield,
                        'pvp': pvp,
                        'liquidity': latest['volume'],
                        'market_cap': market_cap
                    })
                    
                    logger.info(f"✅ Updated indicators: R$ {latest['price']}")
                    
                logger.info("\n" + "=" * 60)
                logger.info("✅ DATABASE REPOPULATION COMPLETED SUCCESSFULLY!")
                logger.info("=" * 60)
                
            except Exception as e:
                logger.error(f"❌ Error during repopulation: {e}")
                raise
    
    def _estimate_dividend_yield(self, ticker: str) -> float:
        """Estimate dividend yield (placeholder until real data available)"""
        typical_yields = {
            'HGLG11': 10.5,
            'KNRI11': 9.8,
            'XPML11': 9.2,
            'VISC11': 8.7,
            'PVBI11': 8.9
        }
        return typical_yields.get(ticker, 9.0)
    
    def _estimate_pvp(self, ticker: str) -> float:
        """Estimate P/VP ratio (placeholder until real data available)"""
        typical_pvp = {
            'HGLG11': 1.02,
            'KNRI11': 0.98,
            'XPML11': 1.05,
            'VISC11': 0.96,
            'PVBI11': 1.01
        }
        return typical_pvp.get(ticker, 1.00)
    
    def _estimate_market_cap(self, ticker: str, price: float) -> int:
        """Estimate market cap based on typical FII size"""
        estimated_shares = {
            'HGLG11': 11.0,
            'KNRI11': 15.0,
            'XPML11': 35.0,
            'VISC11': 18.0,
            'PVBI11': 22.0
        }
        shares = estimated_shares.get(ticker, 10.0) * 1_000_000
        return int(price * shares)


if __name__ == '__main__':
    repopulator = RealDataRepopulator()
    repopulator.repopulate_database(TRACKED_FIIS)
