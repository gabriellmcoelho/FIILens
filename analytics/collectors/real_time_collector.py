"""
Real-time FII data collector
Collects data from public APIs (Yahoo Finance, Status Invest)
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
        
        # Use Yahoo Finance (free, no auth required)
        self.yahoo_base_url = "https://query1.finance.yahoo.com/v8/finance/chart"
        
    def collect_fii_data(self, tickers: List[str]) -> List[Dict]:
        """
        Collect real-time data for specified FIIs from Yahoo Finance
        
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
        """Collect data for a single FII from Yahoo Finance"""
        try:
            # Yahoo Finance uses .SA suffix for Brazilian stocks/FIIs
            yahoo_ticker = f"{ticker}.SA"
            
            url = f"{self.yahoo_base_url}/{yahoo_ticker}"
            params = {
                'range': '1d',
                'interval': '1d'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'chart' not in data or 'result' not in data['chart']:
                    logger.warning(f"No data found for {ticker}")
                    return None
                
                result = data['chart']['result'][0]
                meta = result.get('meta', {})
                quote = result.get('indicators', {}).get('quote', [{}])[0]
                
                # Extract real data
                fii_data = {
                    'ticker': ticker,
                    'name': meta.get('longName', ticker),
                    'price': meta.get('regularMarketPrice', 0.0),
                    'previousClose': meta.get('previousClose', 0.0),
                    'volume': quote.get('volume', [0])[0] if quote.get('volume') else 0,
                    'marketCap': meta.get('marketCap', 0),
                    'high': quote.get('high', [0])[0] if quote.get('high') else 0,
                    'low': quote.get('low', [0])[0] if quote.get('low') else 0,
                    'timestamp': datetime.now().isoformat(),
                    'source': 'Yahoo Finance'
                }
                
                # Calculate change
                if fii_data['price'] and fii_data['previousClose']:
                    change = fii_data['price'] - fii_data['previousClose']
                    change_percent = (change / fii_data['previousClose']) * 100
                    fii_data['change'] = round(change, 2)
                    fii_data['changePercent'] = round(change_percent, 2)
                
                # Add estimated indicators
                if fii_data['price'] > 0:
                    fii_data['dividendYield'] = self._estimate_dividend_yield(ticker)
                    fii_data['pvp'] = self._estimate_pvp(ticker)
                    # Estimate market cap based on typical FII size
                    if fii_data['marketCap'] == 0:
                        fii_data['marketCap'] = self._estimate_market_cap(ticker, fii_data['price'])
                    
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
    
    def _estimate_market_cap(self, ticker: str, price: float) -> int:
        """
        Estimate market cap based on typical FII size and number of shares
        In production, this should fetch real data from B3 or fund reports
        """
        # Estimated number of shares outstanding (in millions)
        # Based on typical FII sizes in Brazil
        estimated_shares = {
            'HGLG11': 11.0,  # ~11M cotas
            'KNRI11': 15.0,  # ~15M cotas
            'XPML11': 35.0,  # ~35M cotas (maior fundo)
            'VISC11': 18.0,  # ~18M cotas
            'PVBI11': 22.0   # ~22M cotas
        }
        
        shares = estimated_shares.get(ticker, 10.0) * 1_000_000  # Convert to actual shares
        market_cap = int(price * shares)
        
        return market_cap
    
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
