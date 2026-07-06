"""
Main analytics engine
Orchestrates data collection, validation, quality checks and persistence
"""

import logging
import sys
from sqlalchemy import text
from config import get_db, logger
from collectors.real_time_collector import get_collector
from validators.data_validator import validate_data
from quality.quality_scorer import calculate_quality_scores

# FII tickers to track
TRACKED_FIIS = ['HGLG11', 'KNRI11', 'XPML11', 'VISC11', 'PVBI11']

def update_real_time_data():
    """Update FII data from real-time sources"""
    logger.info("Starting real-time data update...")
    
    collector = get_collector()
    
    # Collect real-time data
    fiis_data = collector.collect_fii_data(TRACKED_FIIS)
    
    if not fiis_data:
        logger.error("No data collected from APIs")
        return
    
    # Get database session
    db = next(get_db())
    
    try:
        for fii_data in fiis_data:
            ticker = fii_data['ticker']
            logger.info(f"Updating {ticker}...")
            
            # Update or insert fund
            fund_query = text("""
                INSERT INTO funds (id, ticker, name, created_at, updated_at)
                VALUES (gen_random_uuid(), :ticker, :name, NOW(), NOW())
                ON CONFLICT (ticker) DO UPDATE 
                SET name = EXCLUDED.name, 
                    updated_at = NOW()
                RETURNING id
            """)
            
            result = db.execute(fund_query, {
                'ticker': ticker,
                'name': fii_data.get('name', ticker)
            })
            
            fund_id = result.fetchone()[0]
            
            # Update indicators
            indicators_query = text("""
                INSERT INTO indicators (
                    id, fund_id, price, dividend_yield, pvp, liquidity,
                    market_cap, volume, created_at, updated_at
                )
                VALUES (
                    gen_random_uuid(), :fund_id, :price, :dividend_yield, :pvp,
                    :liquidity, :market_cap, :volume, NOW(), NOW()
                )
                ON CONFLICT (fund_id) DO UPDATE SET
                    price = EXCLUDED.price,
                    dividend_yield = EXCLUDED.dividend_yield,
                    pvp = EXCLUDED.pvp,
                    liquidity = EXCLUDED.liquidity,
                    market_cap = EXCLUDED.market_cap,
                    volume = EXCLUDED.volume,
                    updated_at = NOW()
            """)
            
            db.execute(indicators_query, {
                'fund_id': fund_id,
                'price': fii_data.get('price', 0),
                'dividend_yield': fii_data.get('dividendYield', 0),
                'pvp': fii_data.get('pvp', 1.0),
                'liquidity': fii_data.get('volume', 0),
                'market_cap': fii_data.get('marketCap', 0),
                'volume': fii_data.get('volume', 0)
            })
            
            # Insert historical price
            historical_query = text("""
                INSERT INTO historical_prices (
                    id, fund_id, date, price, volume, created_at
                )
                VALUES (
                    gen_random_uuid(), :fund_id, CURRENT_DATE, :price, :volume, NOW()
                )
                ON CONFLICT (fund_id, date) DO UPDATE SET
                    price = EXCLUDED.price,
                    volume = EXCLUDED.volume
            """)
            
            db.execute(historical_query, {
                'fund_id': fund_id,
                'price': fii_data.get('price', 0),
                'volume': fii_data.get('volume', 0)
            })
            
            logger.info(f"✅ {ticker} updated: R$ {fii_data.get('price', 0):.2f}")
        
        db.commit()
        logger.info("✅ Real-time data update completed successfully!")
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error updating data: {e}")
        raise
    finally:
        db.close()

def seed_sample_data():
    """Seed database with sample FII data for MVP"""
    logger.info("Starting data seeding process...")
    
    # Collect data
    fiis = collect_fii_data()
    
    # Validate data
    validation_result = validate_data(fiis)
    valid_fiis = validation_result['valid_fiis']
    
    logger.info(f"Validation report: {validation_result['report']}")
    
    # Get database session
    db = next(get_db())
    
    try:
        for fii_data in valid_fiis:
            ticker = fii_data['ticker']
            logger.info(f"Processing {ticker}...")
            
            # Insert Fund
            fund_query = text("""
                INSERT INTO funds (id, ticker, name, cnpj, segment, manager, administrator, created_at, updated_at)
                VALUES (gen_random_uuid(), :ticker, :name, :cnpj, :segment, :manager, :administrator, NOW(), NOW())
                ON CONFLICT (ticker) DO UPDATE 
                SET name = EXCLUDED.name, 
                    segment = EXCLUDED.segment,
                    manager = EXCLUDED.manager,
                    updated_at = NOW()
                RETURNING id
            """)
            
            result = db.execute(fund_query, {
                'ticker': ticker,
                'name': fii_data['name'],
                'cnpj': fii_data['cnpj'],
                'segment': fii_data['segment'],
                'manager': fii_data['manager'],
                'administrator': fii_data['administrator']
            })
            
            fund_id = result.fetchone()[0]
            
            # Insert Indicators
            indicators = fii_data['indicators']
            indicator_query = text("""
                INSERT INTO indicators (
                    id, fund_id, dividend_yield, pvp, liquidity, market_cap,
                    net_asset_value, vacancy, price, volume, last_update
                )
                VALUES (
                    gen_random_uuid(), :fund_id, :dividend_yield, :pvp, :liquidity,
                    :market_cap, :net_asset_value, :vacancy, :price, :volume, NOW()
                )
            """)
            
            db.execute(indicator_query, {
                'fund_id': fund_id,
                'dividend_yield': indicators['dividendYield'],
                'pvp': indicators['pvp'],
                'liquidity': indicators['liquidity'],
                'market_cap': indicators['marketCap'],
                'net_asset_value': indicators['netAssetValue'],
                'vacancy': indicators['vacancy'],
                'price': indicators['price'],
                'volume': indicators['volume']
            })
            
            # Insert Historical Prices
            historical_prices = collect_historical_prices(ticker)
            for hp in historical_prices:
                hp_query = text("""
                    INSERT INTO historical_prices (id, fund_id, date, price, volume)
                    VALUES (gen_random_uuid(), :fund_id, :date, :price, :volume)
                    ON CONFLICT (fund_id, date) DO NOTHING
                """)
                
                db.execute(hp_query, {
                    'fund_id': fund_id,
                    'date': hp['date'],
                    'price': hp['price'],
                    'volume': hp['volume']
                })
            
            # Insert Dividends
            dividends = collect_dividends(ticker)
            for div in dividends:
                div_query = text("""
                    INSERT INTO dividends (id, fund_id, payment_date, ex_date, value)
                    VALUES (gen_random_uuid(), :fund_id, :payment_date, :ex_date, :value)
                """)
                
                db.execute(div_query, {
                    'fund_id': fund_id,
                    'payment_date': div['paymentDate'],
                    'ex_date': div['exDate'],
                    'value': div['value']
                })
            
            # Calculate and insert quality scores
            quality_scores = calculate_quality_scores(fii_data)
            quality_query = text("""
                INSERT INTO quality_scores (
                    id, fund_id, completeness, consistency, accuracy,
                    uniqueness, validity, timeliness, overall_score, measured_at
                )
                VALUES (
                    gen_random_uuid(), :fund_id, :completeness, :consistency,
                    :accuracy, :uniqueness, :validity, :timeliness, :overall_score, NOW()
                )
            """)
            
            db.execute(quality_query, {
                'fund_id': fund_id,
                'completeness': quality_scores['completeness'],
                'consistency': quality_scores['consistency'],
                'accuracy': quality_scores['accuracy'],
                'uniqueness': quality_scores['uniqueness'],
                'validity': quality_scores['validity'],
                'timeliness': quality_scores['timeliness'],
                'overall_score': quality_scores['overallScore']
            })
            
            logger.info(f"Successfully processed {ticker}")
        
        # Insert sample glossary terms
        glossary_terms = [
            {
                'term': 'Dividend Yield',
                'definition': 'Distribuição anual de dividendos dividida pelo preço atual da cota.',
                'category': 'Indicadores Financeiros',
                'example': 'Um FII com DY de 10% paga R$ 10 de dividendos por ano para cada R$ 100 investidos.'
            },
            {
                'term': 'P/VP',
                'definition': 'Relação entre o preço de mercado da cota e o valor patrimonial por cota.',
                'category': 'Indicadores Financeiros',
                'example': 'P/VP de 0,95 indica que o FII está negociando abaixo do valor patrimonial.'
            },
            {
                'term': 'Vacância',
                'definition': 'Percentual de imóveis ou áreas não locadas no portfólio do fundo.',
                'category': 'Indicadores Operacionais',
                'example': 'Vacância de 5% significa que 95% do portfólio está ocupado.'
            }
        ]
        
        for term in glossary_terms:
            glossary_query = text("""
                INSERT INTO glossary (id, term, business_definition, category, example, created_at, updated_at)
                VALUES (gen_random_uuid(), :term, :definition, :category, :example, NOW(), NOW())
                ON CONFLICT (term) DO NOTHING
            """)
            
            db.execute(glossary_query, {
                'term': term['term'],
                'definition': term['definition'],
                'category': term['category'],
                'example': term['example']
            })
        
        # Insert sample metadata
        metadata_entries = [
            {
                'entity_type': 'Fund',
                'entity_name': 'FII Master Data',
                'business_description': 'Dados mestres dos Fundos de Investimento Imobiliário',
                'data_owner': 'Financial Analytics Team',
                'data_steward': 'Data Engineering',
                'source': 'B3/CVM',
                'refresh_frequency': 'Real-time',
                'classification': 'Public',
                'sensitivity': 'Low',
                'version': '1.0.0'
            },
            {
                'entity_type': 'Indicator',
                'entity_name': 'Financial Indicators',
                'business_description': 'Indicadores financeiros calculados para análise de FIIs',
                'data_owner': 'Analytics Team',
                'data_steward': 'Data Quality Team',
                'source': 'Analytics Engine',
                'refresh_frequency': 'Daily',
                'classification': 'Public',
                'sensitivity': 'Low',
                'version': '1.0.0'
            }
        ]
        
        for meta in metadata_entries:
            metadata_query = text("""
                INSERT INTO metadata (
                    id, entity_type, entity_name, business_description,
                    data_owner, data_steward, source, refresh_frequency,
                    classification, sensitivity, version, created_at, updated_at
                )
                VALUES (
                    gen_random_uuid(), :entity_type, :entity_name, :business_description,
                    :data_owner, :data_steward, :source, :refresh_frequency,
                    :classification, :sensitivity, :version, NOW(), NOW()
                )
            """)
            
            db.execute(metadata_query, meta)
        
        db.commit()
        logger.info("Data seeding completed successfully!")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding data: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='FIILens Analytics Engine')
    parser.add_argument('--mode', choices=['seed', 'update'], default='update',
                       help='Mode: seed (initial data) or update (real-time refresh)')
    args = parser.parse_args()
    
    try:
        if args.mode == 'seed':
            logger.info("Running in SEED mode...")
            seed_sample_data()
        else:
            logger.info("Running in UPDATE mode (real-time data)...")
            update_real_time_data()
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)
