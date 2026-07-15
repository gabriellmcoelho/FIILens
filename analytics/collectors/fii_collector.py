"""
Data collection module for FII data
This module collects FII data from various sources
For MVP, we'll use sample data
"""

import logging
from typing import List, Dict
import random
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config_fiis import FIIS_DATABASE as SAMPLE_FIIS

logger = logging.getLogger(__name__)

def collect_fii_data() -> List[Dict]:
    """
    Collect FII data from sources
    For MVP, returns sample data with random indicators
    """
    logger.info("Collecting FII data...")
    
    fiis_with_indicators = []
    
    for fii in SAMPLE_FIIS:
        # Generate random indicators for MVP
        indicators = {
            'price': round(random.uniform(80, 200), 2),
            'dividendYield': round(random.uniform(8, 14), 2),
            'pvp': round(random.uniform(0.85, 1.15), 2),
            'liquidity': round(random.uniform(1000, 50000), 0),
            'marketCap': round(random.uniform(500000000, 5000000000), 2),
            'netAssetValue': round(random.uniform(90, 220), 2),
            'vacancy': round(random.uniform(0, 15), 2),
            'volume': round(random.uniform(10000, 1000000), 2)
        }
        
        fiis_with_indicators.append({
            **fii,
            'indicators': indicators
        })
    
    logger.info(f"Collected data for {len(fiis_with_indicators)} FIIs")
    return fiis_with_indicators

def collect_historical_prices(ticker: str, days: int = 90) -> List[Dict]:
    """
    Collect historical prices for a FII
    For MVP, generates sample historical data
    """
    logger.info(f"Collecting historical prices for {ticker}...")
    
    base_price = random.uniform(80, 200)
    prices = []
    
    for i in range(days):
        date = datetime.now() - timedelta(days=days - i)
        # Add some random variation
        variation = random.uniform(-0.02, 0.02)
        price = base_price * (1 + variation)
        base_price = price  # Use as base for next day
        
        prices.append({
            'date': date.date().isoformat(),
            'price': round(price, 2),
            'volume': round(random.uniform(10000, 1000000), 2)
        })
    
    return prices

def collect_dividends(ticker: str) -> List[Dict]:
    """
    Collect dividend history for a FII
    For MVP, generates sample dividend data
    """
    logger.info(f"Collecting dividends for {ticker}...")
    
    dividends = []
    
    for i in range(12):  # Last 12 months
        payment_date = datetime.now() - timedelta(days=30 * i)
        ex_date = payment_date - timedelta(days=7)
        
        dividends.append({
            'paymentDate': payment_date.date().isoformat(),
            'exDate': ex_date.date().isoformat(),
            'value': round(random.uniform(0.50, 1.50), 2)
        })
    
    return dividends
