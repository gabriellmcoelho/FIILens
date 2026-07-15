"""
Configuração centralizada de FIIs monitorados
Para adicionar novos FIIs, basta incluir nesta lista
"""

# Lista completa de FIIs com informações detalhadas
FIIS_DATABASE = [
    {
        'ticker': 'HGLG11',
        'name': 'CSHG Logística',
        'cnpj': '28.757.546/0001-00',
        'segment': 'Logística',
        'manager': 'Credit Suisse Hedging-Griffo',
        'administrator': 'Credit Suisse'
    },
    {
        'ticker': 'KNRI11',
        'name': 'Kinea Rendimentos Imobiliários',
        'cnpj': '11.152.141/0001-52',
        'segment': 'Híbrido',
        'manager': 'Kinea',
        'administrator': 'Itaú Unibanco'
    },
    {
        'ticker': 'XPML11',
        'name': 'XP Malls',
        'cnpj': '28.757.421/0001-86',
        'segment': 'Shopping',
        'manager': 'XP Asset',
        'administrator': 'XP Investimentos'
    },
    {
        'ticker': 'VISC11',
        'name': 'Vinci Shopping Centers',
        'cnpj': '14.864.934/0001-28',
        'segment': 'Shopping',
        'manager': 'Vinci Partners',
        'administrator': 'BNY Mellon'
    },
    {
        'ticker': 'BTHF11',
        'name': 'BTG PACTUAL REAL ESTATE HEDGE FUND FII - RESP LTDA',
        'cnpj': '45.188.176/0001-57',
        'segment': 'Híbrido',
        'manager': 'BTG Pactual Gestora de Recursos Ltda.',
        'administrator': 'BTG Pactual Serviços Financeiros S.A. DTVM'
    },
    {
        'ticker': 'PVBI11',
        'name': 'VBI Prime Properties',
        'cnpj': '36.341.371/0001-52',
        'segment': 'Lajes Corporativas',
        'manager': 'VBI',
        'administrator': 'Vórtx'
    }
]

# Lista de tickers (para uso simples)
TRACKED_FIIS = [fii['ticker'] for fii in FIIS_DATABASE]

# Função auxiliar para obter dados completos de um FII
def get_fii_info(ticker: str):
    """Retorna as informações completas de um FII pelo ticker"""
    for fii in FIIS_DATABASE:
        if fii['ticker'] == ticker:
            return fii
    return None

# Função auxiliar para adicionar um novo FII
def add_fii(ticker: str, name: str, cnpj: str, segment: str, manager: str, administrator: str):
    """
    Adiciona um novo FII à lista (em memória)
    Para persistir, adicione diretamente em FIIS_DATABASE acima
    """
    new_fii = {
        'ticker': ticker,
        'name': name,
        'cnpj': cnpj,
        'segment': segment,
        'manager': manager,
        'administrator': administrator
    }
    FIIS_DATABASE.append(new_fii)
    TRACKED_FIIS.append(ticker)
    return new_fii
