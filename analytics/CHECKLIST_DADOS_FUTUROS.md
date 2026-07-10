# 📋 Checklist de Dados Futuros - FIILens

Lista de dados que ainda precisam ser coletados para melhorar o sistema de scoring.

---

## 🎯 Alta Prioridade

### ✅ Implementados

- [x] Dividend Yield
- [x] P/VP
- [x] Liquidez (Volume)
- [x] Dividendos Históricos
- [x] Preços Históricos
- [x] Valorização da Cota (calculado)
- [x] Consistência de Dividendos (calculado)
- [x] Patrimônio Líquido

### 🔴 Pendentes - Alta Prioridade

#### 1. Vacância (% de imóveis vagos)

- **Status**: ❌ Não implementado
- **Fonte**: Relatórios mensais dos FIIs (PDFs)
- **Peso sugerido**: 15%
- **Dificuldade**: 🟡 Média
- **Impacto**: 🔴 Alto
- **Estratégia de coleta**:
  - Baixar relatórios mensais de cada FII
  - Fazer parsing de PDF para extrair taxa de vacância
  - Alternativa: Alguns sites agregadores (Status Invest, Funds Explorer)
- **Notas**: Essencial para avaliar risco de receita

#### 2. Número de Cotistas

- **Status**: ❌ Não implementado
- **Fonte**: CVM ou relatórios mensais
- **Peso sugerido**: 5%
- **Dificuldade**: 🟡 Média
- **Impacto**: 🟡 Médio
- **Estratégia de coleta**:
  - API da CVM (se disponível)
  - Web scraping de relatórios
  - Sites agregadores
- **Notas**: Indicador de liquidez e governança

#### 3. Performance vs IFIX

- **Status**: ❌ Não implementado
- **Fonte**: B3 (Índice IFIX)
- **Peso sugerido**: 10%
- **Dificuldade**: 🟢 Baixa
- **Impacto**: 🔴 Alto
- **Estratégia de coleta**:
  - API da B3 ou Yahoo Finance para IFIX
  - Calcular beta e correlação
  - Comparar retorno relativo (12M, 24M, 36M)
- **Notas**: Benchmark fundamental para comparação

---

## 🎯 Média Prioridade

#### 4. Diversificação Geográfica

- **Status**: ❌ Não implementado
- **Fonte**: Relatórios dos fundos
- **Peso sugerido**: 5%
- **Dificuldade**: 🔴 Alta
- **Impacto**: 🟡 Médio
- **Estratégia de coleta**:
  - Parsing de PDFs de relatórios
  - Extrair localização dos imóveis
  - Calcular índice de Herfindahl-Hirschman (HHI) para diversificação
- **Notas**: Reduz risco de concentração regional

#### 5. Qualidade dos Inquilinos

- **Status**: ❌ Não implementado
- **Fonte**: Relatórios dos fundos + análise de crédito
- **Peso sugerido**: 8%
- **Dificuldade**: 🔴 Alta
- **Impacto**: 🔴 Alto
- **Estratégia de coleta**:
  - Extrair lista de inquilinos dos relatórios
  - Cruzar com ratings de crédito (Serasa, S&P, Moody's)
  - Classificar por porte e solidez financeira
- **Notas**: Fundamental para avaliar risco de inadimplência

#### 6. Taxa de Administração

- **Status**: ❌ Não implementado
- **Fonte**: Regulamento do fundo
- **Peso sugerido**: 5%
- **Dificuldade**: 🟡 Média
- **Impacto**: 🟡 Médio
- **Estratégia de coleta**:
  - Parsing do regulamento (PDF)
  - Sites agregadores podem ter essa informação
- **Notas**: Custo direto que impacta o DY líquido

#### 7. Prazo Médio de Contratos

- **Status**: ❌ Não implementado
- **Fonte**: Relatórios dos fundos
- **Peso sugerido**: 5%
- **Dificuldade**: 🔴 Alta
- **Impacto**: 🟡 Médio
- **Estratégia de coleta**:
  - Extrair informações de contratos dos relatórios
  - Calcular média ponderada por valor
- **Notas**: Previsibilidade de receita futura

#### 8. Gestora (Informação Completa)

- **Status**: ⚠️ Parcialmente implementado
- **Fonte**: StatusInvest (incompleto)
- **Dificuldade**: 🟡 Média
- **Impacto**: 🟡 Médio
- **Estratégia de coleta**:
  - Testar outras fontes: CVM, Funds Explorer
  - Relatórios do fundo como fallback
- **Notas**: Útil para análise de track record

---

## 🎯 Baixa Prioridade (Enhancement)

#### 9. Área Construída (GLA - Gross Leasable Area)

- **Status**: ❌ Não implementado
- **Fonte**: Relatórios dos fundos
- **Dificuldade**: 🟡 Média
- **Impacto**: 🟢 Baixo
- **Notas**: Indicador de tamanho do portfólio

#### 10. Idade Média dos Imóveis

- **Status**: ❌ Não implementado
- **Fonte**: Relatórios dos fundos
- **Dificuldade**: 🔴 Alta
- **Impacto**: 🟢 Baixo
- **Notas**: Risco de obsolescência e necessidade de CAPEX

#### 11. Distribuição por Setor de Inquilinos

- **Status**: ❌ Não implementado
- **Fonte**: Relatórios dos fundos
- **Dificuldade**: 🔴 Alta
- **Impacto**: 🟡 Médio
- **Notas**: Diversificação setorial reduz risco

#### 12. Histórico de Gestão / Track Record

- **Status**: ❌ Não implementado
- **Fonte**: Análise histórica de performance
- **Dificuldade**: 🔴 Alta (subjetivo)
- **Impacto**: 🟡 Médio
- **Notas**: Reputação e competência do gestor

---

## 📊 Resumo de Status

| Categoria            | Total | ✅ Implementado | ⚠️ Parcial | ❌ Pendente |
| -------------------- | ----- | --------------- | ---------- | ----------- |
| **Alta Prioridade**  | 11    | 8               | 0          | 3           |
| **Média Prioridade** | 5     | 0               | 1          | 4           |
| **Baixa Prioridade** | 4     | 0               | 0          | 4           |
| **TOTAL**            | 20    | 8 (40%)         | 1 (5%)     | 11 (55%)    |

---

## 🎯 Roadmap de Implementação

### Fase 1 (Próximos 1-2 meses)

1. ✅ ~~Sistema de Scoring Heurístico~~ - **CONCLUÍDO**
2. 🔜 Coletar dados do IFIX (API B3/Yahoo Finance)
3. 🔜 Implementar comparação vs IFIX no modelo
4. 🔜 Coletar número de cotistas (CVM ou agregadores)

### Fase 2 (3-4 meses)

1. 🔜 Coletar vacância dos FIIs (parsing de PDFs)
2. 🔜 Implementar web scraping robusto para relatórios mensais
3. 🔜 Adicionar taxa de administração
4. 🔜 Completar dados de gestora

### Fase 3 (5-6 meses)

1. 🔜 Qualidade de inquilinos (cruzamento com ratings)
2. 🔜 Diversificação geográfica
3. 🔜 Prazo médio de contratos
4. 🔜 Modelo de ML supervisionado com features completas

### Fase 4 (6+ meses)

1. 🔜 Features de enhancement (GLA, idade, distribuição setorial)
2. 🔜 Deep Learning para análise de séries temporais
3. 🔜 NLP para análise de relatórios textuais
4. 🔜 Sistema de recomendação personalizado

---

## 📝 Notas de Implementação

### Desafios Técnicos

1. **Parsing de PDFs**:
   - Usar bibliotecas: `pdfplumber`, `PyPDF2`, `camelot`
   - PDFs podem ter layouts variados entre fundos
   - Considerar OCR para PDFs escaneados (`pytesseract`)

2. **Rate Limiting**:
   - Respeitar limites de requisições de cada fonte
   - Implementar backoff exponencial
   - Cache de dados para evitar requisições duplicadas

3. **Qualidade de Dados**:
   - Validar dados coletados (ranges esperados)
   - Detectar outliers e anomalias
   - Implementar sistema de alertas para dados suspeitos

4. **Atualização Periódica**:
   - Scheduler para rodar coletores automaticamente
   - Priorizar dados mais críticos (DY, P/VP, vacância)
   - Notificar em caso de falhas

### Fontes de Dados Potenciais

| Fonte              | Tipo         | Dados Disponíveis                 | Dificuldade  |
| ------------------ | ------------ | --------------------------------- | ------------ |
| **B3**             | API          | Preços, IFIX, volume              | 🟢 Baixa     |
| **Yahoo Finance**  | API          | Preços históricos, dividendos     | 🟢 Baixa     |
| **StatusInvest**   | Web Scraping | P/VP, indicadores, relatórios     | 🟡 Média     |
| **Funds Explorer** | Web Scraping | Indicadores completos             | 🔴 Alta (JS) |
| **CVM**            | Portal       | Documentos oficiais, regulamentos | 🟡 Média     |
| **Relatórios PDF** | Parsing      | Vacância, inquilinos, contratos   | 🔴 Alta      |

---

## 🎬 Próximos Passos

1. **Imediato** (esta semana):
   - ✅ Sistema de scoring implementado
   - ✅ README ML criado
   - ✅ Checklist documentado
2. **Curto Prazo** (próximas 2 semanas):
   - [ ] Implementar coleta de dados do IFIX
   - [ ] Adicionar comparação vs IFIX no score
   - [ ] Criar scheduler para atualização automática de scores
3. **Médio Prazo** (próximo mês):
   - [ ] Implementar coleta de vacância
   - [ ] Testar parsing de PDFs de relatórios
   - [ ] Adicionar número de cotistas

---

**Última atualização**: 2026-07-10  
**Responsável**: Gabriel Coelho  
**Revisão**: Trimestral
