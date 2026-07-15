"""
FIILens ML Scoring System
=========================

Score inteligente de FIIs usando Machine Learning
Gera um score de 0-100 baseado em múltiplas variáveis fundamentalistas
"""

import os
import sys
from typing import Dict, List, Optional, Tuple
import logging
import numpy as np
from datetime import datetime, timedelta
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
# Try multiple paths for .env file
env_paths = [
    os.path.join(os.path.dirname(__file__), '..', '..', 'backend', '.env'),
    os.path.join(os.path.dirname(__file__), '..', '.env'),
    '.env'
]

for env_path in env_paths:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        break

DATABASE_URL = os.getenv('DATABASE_URL')


class FIIScoringModel:
    """
    FIILens Scoring Model
    
    Calcula score de 0-100 para FIIs baseado em indicadores fundamentalistas
    
    Features Disponíveis:
    - Dividend Yield (peso: 25%)
    - P/VP (peso: 20%)
    - Liquidez/Volume (peso: 15%)
    - Consistência de Dividendos (peso: 15%)
    - Valorização da Cota (peso: 15%)
    - Patrimônio Líquido (peso: 10%)
    
    Features Futuras (checklist):
    - Vacância
    - Número de Cotistas
    - Performance vs IFIX
    - Diversificação do Portfólio
    """
    
    def __init__(self):
        self.weights = {
            'dividend_yield': 0.25,
            'pvp': 0.20,
            'liquidity': 0.15,
            'dividend_consistency': 0.15,
            'price_appreciation': 0.15,
            'net_asset_value': 0.10
        }
        
        # Benchmarks para normalização (baseado no mercado de FIIs)
        self.benchmarks = {
            'dividend_yield_excellent': 12.0,  # > 12% = excelente
            'dividend_yield_good': 8.0,        # 8-12% = bom
            'dividend_yield_min': 4.0,         # < 4% = ruim
            'pvp_excellent': 0.85,             # < 0.85 = excelente (desconto)
            'pvp_fair': 1.0,                   # ~1.0 = justo
            'pvp_expensive': 1.15,             # > 1.15 = caro
            'liquidity_excellent': 500000,     # > 500k/dia = excelente
            'liquidity_good': 100000,          # 100k-500k = bom
            'liquidity_min': 10000,            # < 10k = baixa
            'nav_excellent': 1000000000,       # > 1B = grande porte
            'nav_good': 500000000,             # 500M-1B = médio
            'nav_min': 100000000,              # < 100M = pequeno
        }
    
    def normalize_dividend_yield(self, dy: float) -> float:
        """Normaliza Dividend Yield para score 0-100"""
        if dy is None or dy <= 0:
            return 0.0
        
        if dy >= self.benchmarks['dividend_yield_excellent']:
            return 100.0
        elif dy >= self.benchmarks['dividend_yield_good']:
            # Linear entre 70-100
            return 70 + 30 * (dy - self.benchmarks['dividend_yield_good']) / (
                self.benchmarks['dividend_yield_excellent'] - self.benchmarks['dividend_yield_good']
            )
        elif dy >= self.benchmarks['dividend_yield_min']:
            # Linear entre 40-70
            return 40 + 30 * (dy - self.benchmarks['dividend_yield_min']) / (
                self.benchmarks['dividend_yield_good'] - self.benchmarks['dividend_yield_min']
            )
        else:
            # Linear entre 0-40
            return 40 * dy / self.benchmarks['dividend_yield_min']
    
    def normalize_pvp(self, pvp: float) -> float:
        """Normaliza P/VP para score 0-100 (menor é melhor)"""
        if pvp is None or pvp <= 0:
            return 0.0
        
        if pvp <= self.benchmarks['pvp_excellent']:
            return 100.0
        elif pvp <= self.benchmarks['pvp_fair']:
            # Linear entre 80-100
            return 80 + 20 * (1 - (pvp - self.benchmarks['pvp_excellent']) / (
                self.benchmarks['pvp_fair'] - self.benchmarks['pvp_excellent']
            ))
        elif pvp <= self.benchmarks['pvp_expensive']:
            # Linear entre 50-80
            return 50 + 30 * (1 - (pvp - self.benchmarks['pvp_fair']) / (
                self.benchmarks['pvp_expensive'] - self.benchmarks['pvp_fair']
            ))
        else:
            # Exponencial decay para valores muito altos
            return max(0, 50 * np.exp(-0.5 * (pvp - self.benchmarks['pvp_expensive'])))
    
    def normalize_liquidity(self, volume: float) -> float:
        """Normaliza liquidez (volume médio) para score 0-100"""
        if volume is None or volume <= 0:
            return 0.0
        
        if volume >= self.benchmarks['liquidity_excellent']:
            return 100.0
        elif volume >= self.benchmarks['liquidity_good']:
            # Linear entre 70-100
            return 70 + 30 * (volume - self.benchmarks['liquidity_good']) / (
                self.benchmarks['liquidity_excellent'] - self.benchmarks['liquidity_good']
            )
        elif volume >= self.benchmarks['liquidity_min']:
            # Linear entre 40-70
            return 40 + 30 * (volume - self.benchmarks['liquidity_min']) / (
                self.benchmarks['liquidity_good'] - self.benchmarks['liquidity_min']
            )
        else:
            # Linear entre 0-40
            return 40 * volume / self.benchmarks['liquidity_min']
    
    def normalize_net_asset_value(self, nav: float) -> float:
        """Normaliza patrimônio líquido para score 0-100"""
        if nav is None or nav <= 0:
            return 50.0  # Neutral se não disponível
        
        if nav >= self.benchmarks['nav_excellent']:
            return 100.0
        elif nav >= self.benchmarks['nav_good']:
            # Linear entre 75-100
            return 75 + 25 * (nav - self.benchmarks['nav_good']) / (
                self.benchmarks['nav_excellent'] - self.benchmarks['nav_good']
            )
        elif nav >= self.benchmarks['nav_min']:
            # Linear entre 50-75
            return 50 + 25 * (nav - self.benchmarks['nav_min']) / (
                self.benchmarks['nav_good'] - self.benchmarks['nav_min']
            )
        else:
            # Linear entre 25-50 para fundos pequenos
            return 25 + 25 * nav / self.benchmarks['nav_min']
    
    def calculate_dividend_consistency(self, dividends: List[Dict]) -> float:
        """
        Calcula consistência de pagamento de dividendos
        Retorna score 0-100 baseado em:
        - Número de meses com pagamento (últimos 12 meses)
        - Variação entre pagamentos (menor variação = melhor)
        """
        if not dividends or len(dividends) < 6:
            return 30.0  # Score baixo se poucos dados
        
        # Últimos 12 meses
        one_year_ago = datetime.now() - timedelta(days=365)
        recent_divs = [d for d in dividends if d['payment_date'] >= one_year_ago]
        
        if len(recent_divs) < 6:
            return 40.0
        
        # Score por frequência (12 meses = 100%)
        frequency_score = min(100, (len(recent_divs) / 12.0) * 100)
        
        # Score por consistência (baixa variação = melhor)
        values = [d['value'] for d in recent_divs]
        mean_val = np.mean(values)
        std_val = np.std(values)
        
        if mean_val > 0:
            cv = std_val / mean_val  # Coeficiente de variação
            # CV < 0.2 = excelente, CV > 0.5 = ruim
            consistency_score = max(0, 100 - (cv * 200))
        else:
            consistency_score = 0
        
        # Média ponderada: 60% frequência, 40% consistência
        return 0.6 * frequency_score + 0.4 * consistency_score
    
    def calculate_price_appreciation(self, historical_prices: List[Dict]) -> float:
        """
        Calcula valorização da cota nos últimos 12 meses
        Retorna score 0-100
        """
        if not historical_prices or len(historical_prices) < 2:
            return 50.0  # Neutral se poucos dados
        
        # Ordenar por data
        sorted_prices = sorted(historical_prices, key=lambda x: x['date'])
        
        # Pegar preço de 12 meses atrás e atual
        one_year_ago = datetime.now() - timedelta(days=365)
        old_prices = [p for p in sorted_prices if p['date'] <= one_year_ago]
        recent_prices = [p for p in sorted_prices if p['date'] >= datetime.now() - timedelta(days=30)]
        
        if not old_prices or not recent_prices:
            return 50.0
        
        old_price = old_prices[-1]['price']
        current_price = recent_prices[-1]['price']
        
        # Calcular retorno percentual
        return_pct = ((current_price - old_price) / old_price) * 100
        
        # Normalizar: +20% = 100, 0% = 50, -20% = 0
        if return_pct >= 20:
            return 100.0
        elif return_pct >= 0:
            return 50 + 2.5 * return_pct
        elif return_pct >= -20:
            return 50 + 2.5 * return_pct
        else:
            return 0.0
    
    def calculate_score(self, features: Dict) -> Tuple[float, Dict[str, float]]:
        """
        Calcula FIILens Score (0-100)
        
        Args:
            features: Dicionário com indicadores do FII
            
        Returns:
            (score_final, breakdown_por_feature)
        """
        scores = {}
        
        # 1. Dividend Yield (25%)
        dy_score = self.normalize_dividend_yield(features.get('dividend_yield'))
        scores['dividend_yield'] = dy_score
        
        # 2. P/VP (20%)
        pvp_score = self.normalize_pvp(features.get('pvp'))
        scores['pvp'] = pvp_score
        
        # 3. Liquidez (15%)
        liquidity_score = self.normalize_liquidity(features.get('volume'))
        scores['liquidity'] = liquidity_score
        
        # 4. Consistência de Dividendos (15%)
        div_consistency = self.calculate_dividend_consistency(features.get('dividends', []))
        scores['dividend_consistency'] = div_consistency
        
        # 5. Valorização da Cota (15%)
        price_apprec = self.calculate_price_appreciation(features.get('historical_prices', []))
        scores['price_appreciation'] = price_apprec
        
        # 6. Patrimônio Líquido (10%)
        nav_score = self.normalize_net_asset_value(features.get('net_asset_value'))
        scores['net_asset_value'] = nav_score
        
        # Score final ponderado
        final_score = sum(scores[k] * self.weights[k] for k in scores.keys())
        
        return round(final_score, 2), scores


class FIIScoringService:
    """Service para calcular e salvar scores de FIIs no banco"""
    
    def __init__(self):
        self.model = FIIScoringModel()
        self.conn = psycopg2.connect(DATABASE_URL)
    
    def get_fund_features(self, fund_id: str) -> Dict:
        """Busca todas as features necessárias para um FII"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Buscar indicadores
            cur.execute("""
                SELECT dividend_yield, pvp, volume, net_asset_value
                FROM indicators
                WHERE fund_id = %s
            """, (fund_id,))
            indicators = cur.fetchone()
            
            # Buscar dividendos dos últimos 18 meses
            cur.execute("""
                SELECT payment_date, value
                FROM dividends
                WHERE fund_id = %s
                  AND payment_date >= NOW() - INTERVAL '18 months'
                ORDER BY payment_date DESC
            """, (fund_id,))
            dividends = cur.fetchall()
            
            # Buscar preços históricos dos últimos 18 meses
            cur.execute("""
                SELECT date, price
                FROM historical_prices
                WHERE fund_id = %s
                  AND date >= NOW() - INTERVAL '18 months'
                ORDER BY date ASC
            """, (fund_id,))
            historical_prices = cur.fetchall()
            
            return {
                'dividend_yield': indicators['dividend_yield'] if indicators else None,
                'pvp': indicators['pvp'] if indicators else None,
                'volume': indicators['volume'] if indicators else None,
                'net_asset_value': indicators['net_asset_value'] if indicators else None,
                'dividends': dividends,
                'historical_prices': historical_prices
            }
    
    def calculate_and_save_score(self, fund_id: str, ticker: str) -> Tuple[float, Dict]:
        """Calcula score e salva no banco"""
        logger.info(f"Calculating FIILens Score for {ticker}...")
        
        # Buscar features
        features = self.get_fund_features(fund_id)
        
        # Calcular score
        score, breakdown = self.model.calculate_score(features)
        
        # Salvar no banco (usando a estrutura correta de quality_scores)
        with self.conn.cursor() as cur:
            # Atualizar ou inserir score
            cur.execute("""
                SELECT id FROM quality_scores WHERE fund_id = %s
            """, (fund_id,))
            existing = cur.fetchone()
            
            if existing:
                # UPDATE
                cur.execute("""
                    UPDATE quality_scores
                    SET completeness = %s,
                        consistency = %s,
                        accuracy = %s,
                        overall_score = %s,
                        measured_at = NOW()
                    WHERE fund_id = %s
                """, (
                    score,  # Usar score como completeness
                    breakdown.get('dividend_consistency', 0),
                    score,  # Usar score como accuracy
                    score,  # overall_score
                    fund_id
                ))
            else:
                # INSERT
                cur.execute("""
                    INSERT INTO quality_scores 
                    (id, fund_id, completeness, consistency, accuracy, uniqueness, validity, timeliness, overall_score, measured_at)
                    VALUES (gen_random_uuid(), %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                """, (
                    fund_id,
                    score,  # completeness
                    breakdown.get('dividend_consistency', 0),  # consistency
                    score,  # accuracy
                    50.0,   # uniqueness (neutral)
                    50.0,   # validity (neutral)
                    50.0,   # timeliness (neutral)
                    score   # overall_score
                ))
            
            self.conn.commit()
        
        logger.info(f"  ✓ {ticker} FIILens Score: {score}/100")
        
        return score, breakdown
    
    def calculate_all_scores(self, tickers: List[str]):
        """Calcula scores para todos os FIIs"""
        logger.info("=" * 70)
        logger.info("FIILens ML Scoring System")
        logger.info("=" * 70)
        
        results = {}
        
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            for ticker in tickers:
                # Buscar fund_id
                cur.execute("SELECT id FROM funds WHERE ticker = %s", (ticker,))
                result = cur.fetchone()
                
                if not result:
                    logger.warning(f"⚠️  {ticker} not found in database")
                    continue
                
                fund_id = result['id']
                score, breakdown = self.calculate_and_save_score(fund_id, ticker)
                results[ticker] = {'score': score, 'breakdown': breakdown}
        
        # Exibir resultados
        logger.info("\n" + "=" * 70)
        logger.info("FIILENS SCORES - RANKING")
        logger.info("=" * 70)
        
        sorted_results = sorted(results.items(), key=lambda x: x[1]['score'], reverse=True)
        
        for i, (ticker, data) in enumerate(sorted_results, 1):
            score = data['score']
            breakdown = data['breakdown']
            
            # Emoji baseado no score
            if score >= 80:
                emoji = "🏆"
            elif score >= 70:
                emoji = "⭐"
            elif score >= 60:
                emoji = "✓"
            else:
                emoji = "⚠️"
            
            print(f"\n{i}. {emoji} {ticker}: {score}/100")
            print(f"   ├─ Dividend Yield: {breakdown.get('dividend_yield', 0):.1f}/100")
            print(f"   ├─ P/VP: {breakdown.get('pvp', 0):.1f}/100")
            print(f"   ├─ Liquidez: {breakdown.get('liquidity', 0):.1f}/100")
            print(f"   ├─ Consistência: {breakdown.get('dividend_consistency', 0):.1f}/100")
            print(f"   ├─ Valorização: {breakdown.get('price_appreciation', 0):.1f}/100")
            print(f"   └─ Patrimônio: {breakdown.get('net_asset_value', 0):.1f}/100")
        
        return results
    
    def close(self):
        """Fecha conexão com banco"""
        self.conn.close()


if __name__ == '__main__':
    if not DATABASE_URL:
        logger.error("DATABASE_URL not found!")
        sys.exit(1)
    
    # Import FIIs from centralized config
    from config_fiis import TRACKED_FIIS
    
    service = FIIScoringService()
    
    try:
        service.calculate_all_scores(TRACKED_FIIS)
    finally:
        service.close()
