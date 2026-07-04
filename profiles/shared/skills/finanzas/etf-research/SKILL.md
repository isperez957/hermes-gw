---
name: etf-research
description: "Investigación y comparación de ETFs: rentabilidad, gastos, tracking error, holdings, réplica. Usar cuando el usuario pregunta por ETFs concretos, busca alternativas, o compara ETFs para invertir."
version: 1.0.0
---

# ETF Research — Análisis de ETFs

Investigación de ETFs usando `yfinance` para datos de mercado y web_search para composición de cartera.

## Cuando usar
- "analiza el ETF X", "información del SPY"
- "compara ETFs de inteligencia artificial"
- "mejores ETFs de dividendos en Europa"
- "tracking error del ETF de X"
- "qué ETFs siguen al IBEX"
- "alternativas al ETF X más baratas"

## Pasos

### 1. Información básica del ETF
```python
import yfinance as yf

etf = yf.Ticker("VUSA.L")  # Vanguard S&P 500 UCITS
info = etf.info

# Métricas clave
print(f"Nombre: {info.get('longName')}")
print(f"TER: {info.get('annualReportExpenseRatio', 'N/D')}")
print(f"AUM: {info.get('totalAssets', 'N/D')}")
print(f"Yield: {info.get('yield', 'N/D')}")
print(f"Beta 3Y: {info.get('beta3Year', 'N/D')}")
print(f"Fund Inception: {info.get('fundInceptionDate', 'N/D')}")
```

### 2. Comparativa de ETFs similares
```python
# ETFs que siguen al S&P 500 disponibles en Europa
sp500_etfs = {
    'VUSA.L': 'Vanguard S&P 500 UCITS',
    'CSPX.L': 'iShares Core S&P 500 UCITS',
    'SPXS.L': 'Invesco S&P 500 UCITS',
    'SPY5.L': 'SPDR S&P 500 UCITS',
}

for ticker, name in sp500_etfs.items():
    try:
        t = yf.Ticker(ticker)
        i = t.info
        print(f"{ticker}: TER {i.get('annualReportExpenseRatio','?')}, "
              f"AUM {i.get('totalAssets','?')}, "
              f"YTD {i.get('ytdReturn','?')}")
    except:
        pass
```

### 3. Formato de salida
```
📊 Análisis ETF: [Nombre] ([Ticker])

📋 Ficha Técnica
   Nombre: [nombre completo]
   Gestora: [Vanguard, BlackRock, Amundi...]
   Índice subyacente: [S&P 500, MSCI World...]
   Tipo réplica: Física / Sintética
   Divisa: [USD, EUR, GBP...]
   Fecha creación: [año]
   Domicilio: [Irlanda, Luxemburgo...]

💰 Costes
   TER: X.XX% anual
   Diferencia con media categoría: ±X pb
   Coste total estimado (5 años, 10k€): XXX€

📈 Rentabilidad
   YTD: ±X.X%  |  1 año: ±X.X%  |  3 años: ±X.X%  |  5 años: ±X.X%
   Tracking Error 3Y: ±X.XX%
   Tracking Difference: ±X.XX%

📦 Datos de Mercado
   AUM: X,XXXM
   Precio: XX.XX
   Volumen medio diario: X.XM
   Spread bid-ask: X.XX%

🏢 Top 10 Holdings (si disponible)
   1. AAPL (X.X%)   6. ...
   2. MSFT (X.X%)    ...
   ...

🔍 Alternativas con menor TER
   [tabla comparativa si hay]
```

### 4. Para ETFs temáticos/de sector
Añadir análisis específico:
- ¿Exposición real al tema? (ej: "ETF de IA" puede tener 30% en Apple)
- Concentración: % top 5 holdings
- Riesgo de burbuja temática
- Comparar con índice broad market

## Pitfalls
- ETFs UCITS (europeos) llevan sufijos: `.L` (Londres), `.AS` (Ámsterdam), `.DE` (Xetra), `.SW` (Suiza), `.MI` (Milán)
- El TER no incluye todos los costes (spreads, comisiones, fiscalidad)
- ETFs sintéticos tienen riesgo de contraparte
- AUM pequeño (<100M) = riesgo de cierre
- Domicilio fiscal importa: Irlanda > Luxemburgo para dividendos US (tax treaty)