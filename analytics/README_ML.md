# 🤖 FIILens Machine Learning System

Sistema inteligente de análise e scoring de Fundos Imobiliários usando Machine Learning.

## 📊 Overview

O FIILens ML Score é um sistema de pontuação de 0-100 que avalia FIIs baseado em múltiplos indicadores fundamentalistas, fornecendo uma métrica consolidada de qualidade do investimento.

## ⭐ FIILens Score

### Metodologia

O score é calculado através de uma média ponderada de 6 componentes principais:

```
FIILens Score = Σ(Score_i × Peso_i)

onde i = {DY, P/VP, Liquidez, Consistência, Valorização, Patrimônio}
```

### Componentes e Pesos

| Componente                     | Peso | Descrição                                  |
| ------------------------------ | ---- | ------------------------------------------ |
| **Dividend Yield**             | 25%  | Rendimento anual de dividendos             |
| **P/VP**                       | 20%  | Relação Preço/Valor Patrimonial            |
| **Liquidez**                   | 15%  | Volume médio de negociação                 |
| **Consistência de Dividendos** | 15%  | Regularidade e estabilidade dos pagamentos |
| **Valorização da Cota**        | 15%  | Retorno de capital nos últimos 12 meses    |
| **Patrimônio Líquido**         | 10%  | Tamanho e solidez do fundo                 |

### Benchmarks de Normalização

Cada métrica é normalizada para 0-100 usando benchmarks do mercado de FIIs:

#### Dividend Yield

- **100 pontos**: ≥ 12% a.a.
- **70-100**: 8-12% a.a. (bom)
- **40-70**: 4-8% a.a. (regular)
- **0-40**: < 4% a.a. (baixo)

#### P/VP

- **100 pontos**: ≤ 0.85 (desconto)
- **80-100**: 0.85-1.00 (justo)
- **50-80**: 1.00-1.15 (premium moderado)
- **< 50**: > 1.15 (caro)

#### Liquidez (Volume Diário)

- **100 pontos**: ≥ R$ 500k/dia
- **70-100**: R$ 100k-500k/dia
- **40-70**: R$ 10k-100k/dia
- **< 40**: < R$ 10k/dia

#### Consistência de Dividendos

- Avalia frequência de pagamento (últimos 12 meses)
- Avalia estabilidade dos valores (coeficiente de variação)
- Score = 60% frequência + 40% estabilidade

#### Valorização da Cota (12 meses)

- **100 pontos**: ≥ +20%
- **50 pontos**: 0%
- **0 pontos**: ≤ -20%

#### Patrimônio Líquido

- **100 pontos**: ≥ R$ 1 bilhão
- **75-100**: R$ 500M-1B
- **50-75**: R$ 100M-500M
- **< 50**: < R$ 100M

## 📈 Features Disponíveis (Implementadas)

### ✅ Dados Coletados e Disponíveis

| Feature               | Fonte                        | Status        | Uso no Score       |
| --------------------- | ---------------------------- | ------------- | ------------------ |
| Dividend Yield        | Calculado (dividendos/preço) | ✅ Disponível | 25% peso           |
| P/VP                  | StatusInvest                 | ✅ Disponível | 20% peso           |
| Volume/Liquidez       | Yahoo Finance                | ✅ Disponível | 15% peso           |
| Preço Atual           | Yahoo Finance                | ✅ Disponível | Indireta           |
| Preços Históricos     | Yahoo Finance                | ✅ Disponível | Calc. valorização  |
| Dividendos Históricos | Yahoo Finance                | ✅ Disponível | Calc. consistência |
| Patrimônio Líquido    | Indicadores                  | ✅ Disponível | 10% peso           |
| Market Cap            | Calculado                    | ✅ Disponível | Futuro             |
| Segmento              | StatusInvest                 | ✅ Disponível | Futuro             |
| CNPJ                  | StatusInvest                 | ✅ Disponível | Metadata           |
| Administrador         | StatusInvest                 | ✅ Disponível | Metadata           |

### 🔄 Features Calculadas

| Feature                 | Cálculo                                           | Status          |
| ----------------------- | ------------------------------------------------- | --------------- |
| Valorização 12M         | (preço_atual - preço_12m_atrás) / preço_12m_atrás | ✅ Implementado |
| Consistência Dividendos | Frequência + Estabilidade (CV)                    | ✅ Implementado |
| Dividend Yield          | (Σ dividendos 12M / preço atual) × 100            | ✅ Implementado |

## 📋 Checklist: Dados Futuros

### 🎯 Alta Prioridade

- [ ] **Vacância** (% de imóveis vagos)
  - Fonte: Relatórios mensais dos FIIs
  - Peso sugerido: 15%
  - Impacto: Risco de inadimplência e queda de rendimento
  - Dificuldade: Média (requer parsing de PDFs)

- [ ] **Número de Cotistas**
  - Fonte: CVM ou relatórios do fundo
  - Peso sugerido: 5%
  - Impacto: Liquidez e governança
  - Dificuldade: Média

- [ ] **Performance vs IFIX**
  - Fonte: B3 (Índice IFIX)
  - Peso sugerido: 10%
  - Impacto: Benchmark de mercado
  - Dificuldade: Baixa (API disponível)

### 🎯 Média Prioridade

- [ ] **Diversificação Geográfica**
  - Fonte: Relatórios dos fundos
  - Peso sugerido: 5%
  - Impacto: Redução de risco geográfico
  - Dificuldade: Alta (parsing de PDFs)

- [ ] **Qualidade dos Inquilinos**
  - Fonte: Relatórios dos fundos
  - Peso sugerido: 8%
  - Impacto: Risco de crédito
  - Dificuldade: Alta (análise qualitativa)

- [ ] **Taxa de Administração**
  - Fonte: Regulamento do fundo
  - Peso sugerido: 5%
  - Impacto: Custo operacional
  - Dificuldade: Média

- [ ] **Prazo Médio de Contratos**
  - Fonte: Relatórios dos fundos
  - Peso sugerido: 5%
  - Impacto: Previsibilidade de receita
  - Dificuldade: Alta

### 🎯 Baixa Prioridade (Enhancement)

- [ ] **Área Construída (GLA - Gross Leasable Area)**
  - Fonte: Relatórios dos fundos
  - Impacto: Tamanho do portfólio
  - Dificuldade: Média

- [ ] **Idade Média dos Imóveis**
  - Fonte: Relatórios dos fundos
  - Impacto: Risco de obsolescência
  - Dificuldade: Alta

- [ ] **Distribuição por Setor de Inquilinos**
  - Fonte: Relatórios dos fundos
  - Impacto: Diversificação setorial
  - Dificuldade: Alta

- [ ] **Histórico de Gestão**
  - Fonte: Análise de desempenho histórico
  - Impacto: Track record do gestor
  - Dificuldade: Alta (subjetivo)

## 🧠 Roadmap de Machine Learning

### Fase 1: Scoring Heurístico (Atual) ✅

- [x] Modelo baseado em regras e pesos fixos
- [x] Normalização de features com benchmarks
- [x] Score ponderado 0-100
- [x] Sistema de ranking

**Status**: Implementado

### Fase 2: Feature Engineering Avançado

- [ ] Criar features técnicas (médias móveis, RSI, volatilidade)
- [ ] Features de séries temporais (tendências, sazonalidade)
- [ ] Correlação entre FIIs do mesmo segmento
- [ ] Features de sentimento (notícias, relatórios)

**Prazo estimado**: 2-3 meses

### Fase 3: Aprendizado Supervisionado

- [ ] Coletar labels (classificação manual de FIIs "bons" vs "ruins")
- [ ] Treinar modelos de classificação:
  - Random Forest
  - Gradient Boosting (XGBoost, LightGBM)
  - Neural Networks
- [ ] Validação cruzada e otimização de hiperparâmetros
- [ ] A/B testing: modelo heurístico vs ML

**Prazo estimado**: 4-6 meses
**Requisitos**: Histórico de pelo menos 2 anos de dados

### Fase 4: Deep Learning & Time Series

- [ ] LSTM para previsão de dividendos
- [ ] Transformer para análise de séries temporais
- [ ] Autoencoder para detecção de anomalias
- [ ] Reinforcement Learning para otimização de carteira

**Prazo estimado**: 6-12 meses
**Requisitos**: GPU, grande volume de dados históricos

### Fase 5: Recomendação Personalizada

- [ ] Sistema de recomendação baseado em perfil do investidor
- [ ] Clustering de FIIs similares
- [ ] Otimização de carteira (Markowitz, Black-Litterman)
- [ ] Análise de risco vs retorno personalizada

**Prazo estimado**: 12+ meses

## 🔬 Metodologia Científica

### Validação do Modelo

1. **Backtesting**
   - Testar performance histórica do score
   - Comparar FIIs top score vs bottom score
   - Métricas: Sharpe Ratio, retorno acumulado, volatilidade

2. **Walk-Forward Validation**
   - Treinar com dados de N meses
   - Testar nos M meses seguintes
   - Retreinar periodicamente

3. **Cross-Validation**
   - K-fold para evitar overfitting
   - Validação em diferentes períodos (bull/bear market)

### Métricas de Avaliação

- **Precisão**: % de FIIs top score que performaram bem
- **Recall**: % de FIIs que performaram bem e estavam no top score
- **ROC-AUC**: Capacidade de discriminação do modelo
- **Retorno acumulado**: Performance real dos portfolios selecionados

## 🛠️ Estrutura de Arquivos

```
analytics/
├── ml/
│   ├── fii_scoring.py         # Modelo de scoring principal
│   ├── feature_engineering.py # Feature extraction (futuro)
│   ├── model_training.py      # Treinamento supervisionado (futuro)
│   ├── backtesting.py         # Validação histórica (futuro)
│   └── utils.py               # Utilitários
├── collectors/
│   ├── dividend_collector.py
│   ├── metadata_collector.py
│   └── vacancy_collector.py   # Futuro
└── README_ML.md               # Este arquivo
```

## 🚀 Como Usar

### Calcular Scores

```bash
cd analytics
python ml/fii_scoring.py
```

### Output Exemplo

```
======================================================================
FIILens ML Scoring System
======================================================================
Calculating FIILens Score for HGLG11...
  ✓ HGLG11 FIILens Score: 78.5/100

======================================================================
FIILENS SCORES - RANKING
======================================================================

1. ⭐ XPML11: 81.2/100
   ├─ Dividend Yield: 92.5/100
   ├─ P/VP: 85.0/100
   ├─ Liquidez: 75.0/100
   ├─ Consistência: 88.0/100
   ├─ Valorização: 65.0/100
   └─ Patrimônio: 80.0/100

2. ⭐ HGLG11: 78.5/100
   ...
```

## 📚 Referências

### Papers & Artigos

- **Real Estate Investment Trusts**: Fundamentals and analysis
- **Modern Portfolio Theory**: Markowitz, H. (1952)
- **Machine Learning for Asset Management**: Marcos López de Prado

### Datasets & APIs

- [B3 - Bolsa de Valores](https://www.b3.com.br)
- [Yahoo Finance API](https://finance.yahoo.com)
- [StatusInvest](https://statusinvest.com.br)
- [CVM - Comissão de Valores Mobiliários](https://www.gov.br/cvm)

### Frameworks & Tools

- **scikit-learn**: Modelos tradicionais de ML
- **XGBoost/LightGBM**: Gradient Boosting
- **PyTorch/TensorFlow**: Deep Learning
- **pandas/numpy**: Análise de dados
- **statsmodels**: Análise estatística

## 📝 Notas Importantes

1. **Disclaimer**: O FIILens Score é uma ferramenta de análise e não constitui recomendação de investimento.

2. **Atualização**: Os scores devem ser recalculados periodicamente (sugerido: semanalmente) para refletir novos dados.

3. **Limitações Atuais**:
   - Não considera aspectos qualitativos (qualidade dos imóveis, gestão)
   - Não analisa relatórios textuais dos fundos
   - Não incorpora notícias e sentimento de mercado

4. **Evolução Contínua**: Este é um sistema vivo que será aprimorado continuamente com novos dados, features e modelos mais sofisticados.

## 🤝 Contribuindo

Para adicionar novas features ou melhorar o modelo:

1. Identificar fonte de dados confiável
2. Criar collector específico
3. Adicionar normalização no modelo
4. Testar impacto no score final
5. Documentar metodologia
6. Submeter pull request

---

**Versão**: 1.0.0  
**Última atualização**: 2026-07-10  
**Autor**: FIILens Team
