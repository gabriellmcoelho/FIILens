"""
Data validation module
Validates incoming data according to quality rules
"""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class DataValidator:
    """Validates FII data according to quality rules"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_fund(self, fund: Dict) -> bool:
        """Validate fund data"""
        is_valid = True
        
        # Required fields
        required_fields = ['ticker', 'name', 'cnpj', 'segment', 'manager']
        for field in required_fields:
            if not fund.get(field):
                self.errors.append(f"Missing required field: {field}")
                is_valid = False
        
        # Ticker format
        ticker = fund.get('ticker', '')
        if len(ticker) != 6 or not ticker[:-2].isalpha() or not ticker[-2:].isdigit():
            self.warnings.append(f"Invalid ticker format: {ticker}")
        
        # CNPJ format (basic check)
        cnpj = fund.get('cnpj', '')
        if cnpj and len(cnpj.replace('.', '').replace('/', '').replace('-', '')) != 14:
            self.warnings.append(f"Invalid CNPJ format: {cnpj}")
        
        return is_valid
    
    def validate_indicators(self, indicators: Dict) -> bool:
        """Validate indicator data"""
        is_valid = True
        
        # Price should be positive
        price = indicators.get('price', 0)
        if price and price < 0:
            self.errors.append(f"Price cannot be negative: {price}")
            is_valid = False
        
        # Dividend yield should be between 0 and 100
        dy = indicators.get('dividendYield', 0)
        if dy and (dy < 0 or dy > 100):
            self.errors.append(f"Invalid dividend yield: {dy}")
            is_valid = False
        
        # P/VP should be positive
        pvp = indicators.get('pvp', 0)
        if pvp and pvp < 0:
            self.errors.append(f"P/VP cannot be negative: {pvp}")
            is_valid = False
        
        # Market cap should be positive
        market_cap = indicators.get('marketCap', 0)
        if market_cap and market_cap < 0:
            self.errors.append(f"Market cap cannot be negative: {market_cap}")
            is_valid = False
        
        # Vacancy should be between 0 and 100
        vacancy = indicators.get('vacancy', 0)
        if vacancy and (vacancy < 0 or vacancy > 100):
            self.errors.append(f"Invalid vacancy rate: {vacancy}")
            is_valid = False
        
        return is_valid
    
    def get_validation_report(self) -> Dict:
        """Get validation report"""
        return {
            'errors': self.errors,
            'warnings': self.warnings,
            'is_valid': len(self.errors) == 0
        }

def validate_data(fiis: List[Dict]) -> Dict:
    """Validate collected FII data"""
    logger.info("Validating FII data...")
    
    validator = DataValidator()
    valid_fiis = []
    
    for fii in fiis:
        fund_valid = validator.validate_fund(fii)
        indicators_valid = validator.validate_indicators(fii.get('indicators', {}))
        
        if fund_valid and indicators_valid:
            valid_fiis.append(fii)
    
    report = validator.get_validation_report()
    report['valid_count'] = len(valid_fiis)
    report['total_count'] = len(fiis)
    
    logger.info(f"Validation complete: {report['valid_count']}/{report['total_count']} valid")
    
    return {
        'valid_fiis': valid_fiis,
        'report': report
    }
