"""
Real-time FII data collector
Collects data from public APIs (Funds Explorer, B3, etc.)
"""

import logging
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)

class FIIRealTimeCollector:
    """Collector for real-time FII data from public sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # API endpoints (using public sources)
        self.fundsexplorer_url = "https://www.fundsexplorer.com.br/ranking"
        self.brapi_url = "https://brapi.dev/api/quote"
        
    def collect_fii_data(self, tickers: List[str]) -> List[Dict]:
        """
        Collect real-time data for specified FIIs
        
        Args:
            tickers: List of FII tickers (e.g., ['HGLG11', 'KNRI11'])
            
        Returns:
            List of FII data dictionaries
        """
        logger.info(f"Collecting real-time data for {len(tickers)} FIIs...")
        
        fiis_data = []
        
        for ticker in tickers:
            try:
                fii_data = self._collect_single_fii(ticker)
                if fii_data:
                    fiis_data.append(fii_data)
                    logger.info(f"✅ {ticker}: R$ {fii_data.get('price', 'N/A')}")
                time.sleep(0.5)  # Rate limiting
            except Exception as e:
                logger.error(f"❌ Error collecting {ticker}: {e}")
                
        logger.info(f"Successfully collected {len(fiis_data)}/{len(tickers)} FIIs")
        return fiis_data
    
    def _collect_single_fii(self, ticker: str) -> Optional[Dict]:
        """Collect data for a single FII from BRAPI"""
        try:
            # BRAPI - Free Brazilian stocks/FIIs API
            url = f"{self.brapi_url}/{ticker}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'results' not in data or len(data['results']) == 0:
                    logger.warning(f"No data found for {ticker}")
                    return None
                
                result = data['results'][0]
                
                # Extract real data
                fii_data = {
                    'ticker': ticker,
                    'name': result.get('longName', ticker),
                    'price': result.get('regularMarketPrice', 0.0),
                    'previousClose': result.get('regularMarketPreviousClose', 0.0),
                    'volume': result.get('regularMarketVolume', 0),
                    'marketCap': result.get('marketCap', 0),
                    'change': result.get('regularMarketChange', 0.0),
                    'changePercent': result.get('regularMarketChangePercent', 0.0),
                    'high': result.get('regularMarketDayHigh', 0.0),
                    'low': result.get('regularMarketDayLow', 0.0),
                    'timestamp': datetime.now().isoformat(),
                    'source': 'BRAPI'
                }
                
                # Calculate derived indicators
                if fii_data['price'] > 0:
                    # Estimate dividend yield (will be replaced by real data later)
                    fii_data['dividendYield'] = self._estimate_dividend_yield(ticker)
                    fii_data['pvp'] = self._estimate_pvp(ticker)
                    
                return fii_data
            else:
                logger.warning(f"API returned status {response.status_code} for {ticker}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Network error for {ticker}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error for {ticker}: {e}")
            return None
    
    def _estimate_dividend_yield(self, ticker: str) -> float:
        """
        Estimate dividend yield from historical data
        In production, this should fetch real dividend history
        """
        # Placeholder: typical FII dividend yields
        typical_yields = {
            'HGLG11': 10.5,
            'KNRI11': 9.8,
            'XPML11': 9.2,
            'VISC11': 8.7,
            'PVBI11': 8.9
        }
        return typical_yields.get(ticker, 9.0)
    
    def _estimate_pvp(self, ticker: str) -> float:
        """
        Estimate P/VP ratio
        In production, this should fetch real net asset value
        """
        # Placeholder: typical P/VP ratios
        typical_pvp = {
            'HGLG11': 1.02,
            'KNRI11': 0.98,
            'XPML11': 1.05,
            'VISC11': 0.96,
            'PVBI11': 1.01
        }
        return typical_pvp.get(ticker, 1.00)
    
    def collect_historical_prices(self, ticker: str, days: int = 90) -> List[Dict]:
        """
        Collect historical prices for a FII
        Uses BRAPI historical data endpoint
        """
        logger.info(f"Collecting {days} days of historical data for {ticker}...")
        
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # BRAPI historical endpoint
            url = f"{self.brapi_url}/{ticker}"
            params = {
                'range': f'{days}d',
                'interval': '1d'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'results' in data and len(data['results']) > 0:
                    result = data['results'][0]
                    
                    if 'historicalDataPrice' in result:
                        historical = result['historicalDataPrice']
                        
                        prices = []
                        for entry in historical:
                            prices.append({
                                'date': datetime.fromtimestamp(entry['date']).date().isoformat(),
                                'price': entry['close'],
                                'volume': entry.get('volume', 0),
                                'high': entry.get('high', entry['close']),
                                'low': entry.get('low', entry['close'])
                            })
                        
                        logger.info(f"Collected {len(prices)} historical prices for {ticker}")
                        return prices
            
            logger.warning(f"No historical data available for {ticker}")
            return []
            
        except Exception as e:
            logger.error(f"Error collecting historical data for {ticker}: {e}")
            return []
    
    def collect_dividends(self, ticker: str, months: int = 12) -> List[Dict]:
        """
        Collect dividend history
        Note: BRAPI doesn't provide dividend data yet
        This is a placeholder for future implementation
        """
        logger.info(f"Collecting dividend history for {ticker}...")
        
        # Placeholder: In production, this would fetch from:
        # - Funds Explorer API
        # - B3 official data
        # - FII administrator websites
        
        return []


# Singleton instance
_collector_instance = None

def get_collector() -> FIIRealTimeCollector:
    """Get singleton collector instance"""
    global _collector_instance
    if _collector_instance is None:
        _collector_instance = FIIRealTimeCollector()
    return _collector_instance
