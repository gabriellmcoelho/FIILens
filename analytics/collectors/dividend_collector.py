"""
Real dividend data collector from Yahoo Finance
Collects actual dividend history from Yahoo Finance API
"""

import logging
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DividendCollector:
    """Collector for real dividend data from Yahoo Finance"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.base_url = "https://query2.finance.yahoo.com/v8/finance/chart"
        
    def collect_dividends(self, ticker: str, months: int = 12) -> List[Dict]:
        """
        Collect dividend history for a FII from Yahoo Finance
        
        Args:
            ticker: FII ticker (e.g., 'HGLG11')
            months: Number of months of history to collect
            
        Returns:
            List of dividend records with payment_date, ex_date, and value
        """
        try:
            yahoo_ticker = f"{ticker}.SA"
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=months * 31)
            
            period1 = int(start_date.timestamp())
            period2 = int(end_date.timestamp())
            
            # Yahoo Finance events endpoint
            url = f"{self.base_url}/{yahoo_ticker}"
            params = {
                'period1': period1,
                'period2': period2,
                'interval': '1d',
                'events': 'div'  # Request dividend events
            }
            
            logger.info(f"Fetching dividends for {ticker} from Yahoo Finance...")
            
            response = self.session.get(url, params=params, timeout=15)
            
            if response.status_code != 200:
                logger.error(f"❌ Failed to fetch {ticker}: HTTP {response.status_code}")
                return []
            
            data = response.json()
            
            # Parse dividend events
            dividends = []
            
            if 'chart' in data and 'result' in data['chart'] and len(data['chart']['result']) > 0:
                result = data['chart']['result'][0]
                
                if 'events' in result and 'dividends' in result['events']:
                    div_events = result['events']['dividends']
                    
                    for timestamp, div_data in div_events.items():
                        try:
                            # Convert timestamp to date
                            payment_date = datetime.fromtimestamp(int(timestamp))
                            
                            # Get dividend amount
                            amount = float(div_data.get('amount', 0))
                            
                            if amount > 0:
                                dividends.append({
                                    'payment_date': payment_date.strftime('%Y-%m-%d'),
                                    'ex_date': payment_date.strftime('%Y-%m-%d'),
                                    'value': amount
                                })
                        except Exception as e:
                            logger.debug(f"Error parsing dividend event: {e}")
                            continue
                    
                    # Sort by date descending
                    dividends.sort(key=lambda x: x['payment_date'], reverse=True)
            
            logger.info(f"✅ {ticker}: Collected {len(dividends)} dividend records from Yahoo Finance")
            return dividends
            
        except requests.RequestException as e:
            logger.error(f"❌ Network error for {ticker}: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Error collecting dividends for {ticker}: {e}")
            return []
    
    def collect_all_fiis(self, tickers: List[str], months: int = 12) -> Dict[str, List[Dict]]:
        """
        Collect dividends for multiple FIIs
        
        Args:
            tickers: List of FII tickers
            months: Number of months of history
            
        Returns:
            Dictionary mapping ticker to dividend list
        """
        logger.info(f"Starting dividend collection for {len(tickers)} FIIs...")
        
        results = {}
        
        for ticker in tickers:
            dividends = self.collect_dividends(ticker, months)
            results[ticker] = dividends
            
            # Rate limiting - be respectful to the server
            time.sleep(1)
        
        total = sum(len(divs) for divs in results.values())
        logger.info(f"✅ Collected {total} total dividend records across {len(tickers)} FIIs")
        
        return results


if __name__ == '__main__':
    # Test the collector
    collector = DividendCollector()
    
    test_tickers = ['HGLG11', 'KNRI11', 'XPML11']
    
    print("\n" + "="*60)
    print("Testing Yahoo Finance Dividend Collector")
    print("="*60)
    
    for ticker in test_tickers:
        dividends = collector.collect_dividends(ticker, months=12)
        print(f"\n{ticker}: {len(dividends)} dividends")
        if dividends:
            total_12m = sum(d['value'] for d in dividends)
            print(f"  Total 12-month dividends: R$ {total_12m:.2f}")
            print(f"  Latest dividends:")
            for div in dividends[:5]:
                print(f"    {div['payment_date']}: R$ {div['value']:.4f}")
        else:
            print(f"  ⚠️  No dividend data available")
