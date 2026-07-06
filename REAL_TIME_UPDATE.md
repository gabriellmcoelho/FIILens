# 🔄 Sistema de Atualização em Tempo Real

## Mudanças Implementadas

### ✅ Antes (Dados Aleatórios)

- Dados gerados com `random.uniform()`
- Valores não correspondiam à realidade
- Sem atualização automática

### ✅ Agora (Dados Reais)

- **BRAPI**: API pública gratuita para cotações brasileiras
- Preços reais da B3
- Atualização sob demanda via API
- Histórico de preços real

---

## 🚀 Como Atualizar os Dados

### 1. Atualização Manual (Terminal)

```bash
# Atualizar dados em tempo real
cd analytics
/usr/bin/python3 main.py --mode update

# Seed inicial (primeira vez)
/usr/bin/python3 main.py --mode seed
```

### 2. Atualização via API (Recomendado)

```bash
# Endpoint POST para forçar atualização
curl -X POST https://fiilens.onrender.com/api/v1/data/update

# Ver última atualização
curl https://fiilens.onrender.com/api/v1/data/last-update
```

### 3. Atualização Automática no Frontend

Adicionar botão "Atualizar Dados" que chama:

```typescript
await axios.post("/data/update");
```

---

## 📊 Fonte dos Dados

### BRAPI (brapi.dev)

- ✅ Gratuita
- ✅ Sem necessidade de API key
- ✅ Cotações em tempo real da B3
- ✅ Dados históricos
- ✅ Volume e market cap

**Endpoint exemplo:**

```
GET https://brapi.dev/api/quote/HGLG11
```

**Resposta:**

```json
{
  "results": [
    {
      "symbol": "HGLG11",
      "longName": "CSHG Logística FII",
      "regularMarketPrice": 165.82,
      "regularMarketChange": 2.15,
      "regularMarketVolume": 125000,
      "marketCap": 2450000000
    }
  ]
}
```

---

## 🔧 Configuração no Render

### Variáveis de Ambiente (já configuradas)

```env
DATABASE_URL=postgresql://...
JWT_SECRET=...
NODE_ENV=production
PORT=3333
```

### Trigger Atualização Automática (Opcional)

**Opção 1: Cron Job no Render**

```bash
# Render → Settings → Cron Jobs
# Schedule: Every 15 minutes
# Command: cd analytics && /usr/bin/python3 main.py --mode update
```

**Opção 2: Node Scheduler no Backend**

```typescript
import schedule from "node-schedule";

// Atualizar a cada 15 minutos
schedule.scheduleJob("*/15 * * * *", async () => {
  await execAsync("cd analytics && /usr/bin/python3 main.py --mode update");
});
```

---

## 📈 Próximas Melhorias

### Curto Prazo

1. ✅ Implementar botão "Atualizar" no dashboard
2. ✅ Mostrar timestamp da última atualização
3. ✅ Loading indicator durante atualização

### Médio Prazo

1. 🔄 Buscar dividendos reais (Funds Explorer API)
2. 🔄 Calcular P/VP real (Net Asset Value da B3)
3. 🔄 Adicionar mais FIIs (top 50 por liquidez)
4. 🔄 Cache inteligente (Redis)

### Longo Prazo

1. ⏳ WebSocket para atualizações em tempo real
2. ⏳ Notificações push de variações
3. ⏳ ML para predições de preço
4. ⏳ Integração com corretoras

---

## 🧪 Testar Localmente

```bash
# 1. Backend
cd backend
npm run dev

# 2. Atualizar dados (em outro terminal)
cd analytics
/usr/bin/python3 main.py --mode update

# 3. Frontend
cd frontend
npm run dev

# 4. Abrir navegador
open http://localhost:5173
```

---

## 🐛 Troubleshooting

### Erro: "Cannot find module 'requests'"

```bash
/usr/bin/python3 -m pip install requests
```

### Erro: "BRAPI timeout"

- API pode estar temporariamente indisponível
- Tente novamente em alguns segundos
- Verifique: https://brapi.dev/docs

### Dados não aparecem no frontend

1. Verifique se backend está rodando
2. Rode atualização: `python3 main.py --mode update`
3. Verifique console do navegador (F12)
4. Teste endpoint: `curl http://localhost:3333/api/v1/funds`

---

## 📝 Endpoints Criados

| Método | Endpoint                   | Descrição                       |
| ------ | -------------------------- | ------------------------------- |
| `POST` | `/api/v1/data/update`      | Força atualização dos dados     |
| `GET`  | `/api/v1/data/last-update` | Timestamp da última atualização |

---

## ✅ Checklist de Deploy

- [x] Collector real implementado
- [x] Endpoint de atualização criado
- [x] Modo update no main.py
- [ ] Atualizar dados no Render (rodar update)
- [ ] Adicionar botão no frontend
- [ ] Configurar cron job (opcional)
- [ ] Documentar no README principal
