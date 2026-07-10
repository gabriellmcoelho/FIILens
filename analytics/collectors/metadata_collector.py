"""
FII Metadata and P/VP collector from StatusInvest
Collects CNPJ, manager, administrator, segment, and P/VP from StatusInvest
StatusInvest has simpler HTML structure, better for web scraping
"""

import logging
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional, List
import time
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StatusInvestCollector:
    """Collector for FII data from StatusInvest"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://statusinvest.com.br/'
        })
        self.base_url = "https://statusinvest.com.br/fundos-imobiliarios"
        
    def collect_all_data(self, ticker: str) -> Optional[Dict]:
        """
        Collect comprehensive data for a FII from StatusInvest
        
        Args:
            ticker: FII ticker (e.g., 'HGLG11')
            
        Returns:
            Dictionary with cnpj, segment, manager, administrator, pvp
        """
        try:
            url = f"{self.base_url}/{ticker.lower()}"
            
            logger.info(f"Fetching data for {ticker} from StatusInvest...")
            
            response = self.session.get(url, timeout=15)
            
            if response.status_code != 200:
                logger.error(f"❌ Failed to fetch {ticker}: HTTP {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Initialize data
            data = {
                'ticker': ticker,
                'cnpj': None,
                'segment': None,
                'manager': None,
                'administrator': None,
                'pvp': None
            }
            
            # StatusInvest has structured data in indicator cards
            # P/VP is in <h3 class="title m-0">P/VP</h3> with value in next sibling
            try:
                # Find h3 with "title" class containing "P/VP"
                titles = soup.find_all('h3', class_='title')
                for title in titles:
                    if re.search(r'P/VP', title.get_text(), re.IGNORECASE):
                        # Value is in next sibling
                        next_sib = title.find_next_sibling()
                        if next_sib:
                            value_text = next_sib.get_text(strip=True)
                            # Parse value like "0,90" or "1.05"
                            match = re.search(r'(\d+[.,]\d{1,3})', value_text)
                            if match:
                                pvp_str = match.group(1).replace(',', '.')
                                try:
                                    pvp_val = float(pvp_str)
                                    if 0.1 <= pvp_val <= 5.0:  # Realistic range
                                        data['pvp'] = pvp_val
                                        logger.info(f"  ✓ P/VP: {pvp_val:.2f}")
                                        break
                                except ValueError:
                                    pass
            except Exception as e:
                logger.debug(f"  Error parsing P/VP: {e}")
            
            # Look for CNPJ in <h3 class="title m-0">CNPJ</h3> followed by <strong class="value">
            try:
                titles = soup.find_all('h3', class_='title')
                for title in titles:
                    if 'CNPJ' in title.get_text():
                        # Value is in next sibling or in same parent
                        parent = title.find_parent()
                        if parent:
                            value_elem = parent.find('strong', class_='value')
                            if value_elem:
                                cnpj_text = value_elem.get_text(strip=True)
                                cnpj_match = re.search(r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}', cnpj_text)
                                if cnpj_match:
                                    data['cnpj'] = cnpj_match.group(0)
                                    logger.info(f"  ✓ CNPJ: {data['cnpj']}")
                                    break
            except Exception as e:
                logger.debug(f"  Error parsing CNPJ: {e}")
            
            # Look for segment in JSON-LD schema or in <strong class="value"> with segment link
            try:
                # Method 1: JSON-LD schema
                script_tags = soup.find_all('script', type='application/ld+json')
                for script in script_tags:
                    try:
                        import json
                        data_json = json.loads(script.string)
                        if isinstance(data_json, dict) and 'category' in data_json:
                            segment = data_json['category']
                            if segment and len(segment) > 3:
                                data['segment'] = segment
                                logger.info(f"  ✓ Segmento: {segment}")
                                break
                    except:
                        pass
                
                # Method 2: Look for segment in link with "setor"
                if not data['segment']:
                    segment_links = soup.find_all('a', href=re.compile(r'/setor/'))
                    for link in segment_links:
                        strong = link.find('strong', class_='value')
                        if strong:
                            segment_text = strong.get_text(strip=True)
                            # Clean up arrows and icons
                            segment_text = re.sub(r'arrow_\w+|▶|►|»', '', segment_text).strip()
                            if 5 < len(segment_text) < 60:
                                data['segment'] = segment_text
                                logger.info(f"  ✓ Segmento: {segment_text}")
                                break
            except Exception as e:
                logger.debug(f"  Error parsing segment: {e}")
            
            # Look for administrator in <strong class="fw-700">
            try:
                # Administrator is in <strong class="fw-700"> near CNPJ pattern
                strong_elements = soup.find_all('strong', class_='fw-700')
                for strong in strong_elements:
                    text = strong.get_text(strip=True)
                    # Administrator names are typically long and contain bank/institution keywords
                    if len(text) > 10 and any(keyword in text.upper() for keyword in ['BANCO', 'S.A.', 'DTVM', 'ADMINISTRA']):
                        # Verify there's a CNPJ nearby (administrator CNPJ)
                        parent = strong.find_parent()
                        if parent:
                            parent_text = parent.get_text()
                            if re.search(r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}', parent_text):
                                data['administrator'] = text
                                logger.info(f"  ✓ Administrador: {text}")
                                break
                
                # Fallback: look for common administrator names
                if not data['administrator']:
                    admin_patterns = [
                        r'((?:PLURAL|BTG|ITAÚ|BRADESCO|SANTANDER|VÓRTX|INTRAG)[^<]{5,60})',
                        r'([A-Z][A-Za-z\s.]+(?:BANCO|DTVM|S\.A\.)[^<]{0,30})'
                    ]
                    page_text = soup.get_text()
                    for pattern in admin_patterns:
                        match = re.search(pattern, page_text)
                        if match:
                            admin_name = match.group(1).strip()
                            if 10 < len(admin_name) < 80:
                                data['administrator'] = admin_name
                                logger.info(f"  ✓ Administrador: {admin_name}")
                                break
                
            except Exception as e:
                logger.debug(f"  Error parsing administrator: {e}")
            
            # Manager (Gestor) - StatusInvest may not show this prominently
            # Will be None if not found
            try:
                # Try to find in text patterns
                gestor_patterns = [
                    r'Gestor[a]?\s*:?\s*([A-Z][A-Za-z\s&.-]{5,60})',
                ]
                page_text = soup.get_text()
                for pattern in gestor_patterns:
                    match = re.search(pattern, page_text, re.IGNORECASE)
                    if match:
                        manager_name = match.group(1).strip()
                        if 5 < len(manager_name) < 80:
                            data['manager'] = manager_name
                            logger.info(f"  ✓ Gestora: {manager_name}")
                            break
            except Exception as e:
                logger.debug(f"  Error parsing manager: {e}")
            
            # Count how many fields were found
            found_fields = sum(1 for k, v in data.items() if v is not None and k != 'ticker')
            
            if found_fields > 0:
                logger.info(f"✅ {ticker}: Found {found_fields}/5 data fields from StatusInvest")
                return data
            else:
                logger.warning(f"⚠️  {ticker}: No data found on StatusInvest")
                return None
            
        except requests.RequestException as e:
            logger.error(f"❌ Network error for {ticker}: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error collecting data for {ticker}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def collect_all_fiis(self, tickers: List[str]) -> Dict[str, Optional[Dict]]:
        """
        Collect data for multiple FIIs
        
        Args:
            tickers: List of FII tickers
            
        Returns:
            Dictionary mapping ticker to data
        """
        logger.info(f"Starting StatusInvest data collection for {len(tickers)} FIIs...")
        
        results = {}
        
        for ticker in tickers:
            data = self.collect_all_data(ticker)
            results[ticker] = data
            
            # Rate limiting - be respectful to the server
            time.sleep(3)  # StatusInvest may have rate limits
        
        successful = sum(1 for v in results.values() if v is not None)
        logger.info(f"✅ Successfully collected data for {successful}/{len(tickers)} FIIs")
        
        return results


if __name__ == '__main__':
    # Test the collector
    collector = StatusInvestCollector()
    
    test_tickers = ['HGLG11', 'KNRI11', 'XPML11']  # Test with multiple tickers
    
    print("\n" + "="*60)
    print("Testing StatusInvest Data Collector")
    print("="*60)
    
    for ticker in test_tickers:
        data = collector.collect_all_data(ticker)
        print(f"\n{ticker}:")
        if data:
            print(f"  CNPJ: {data.get('cnpj', 'Not found')}")
            print(f"  Segmento: {data.get('segment', 'Not found')}")
            print(f"  Gestora: {data.get('manager', 'Not found')}")
            print(f"  Administrador: {data.get('administrator', 'Not found')}")
            print(f"  P/VP: {data.get('pvp', 'Not found')}")
        else:
            print(f"  ⚠️  No data available")
        
        # Small delay between requests
        if ticker != test_tickers[-1]:
            import time
            time.sleep(2)

