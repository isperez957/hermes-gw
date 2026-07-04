---
name: fixed-income
description: "Análisis de renta fija: bonos soberanos, corporativos, yield curves, spreads de crédito, duración. Usar cuando el usuario pregunta por bonos, tipos de interés, yield curves, o inversiones en renta fija."
version: 1.0.0
---

# Fixed Income — Renta Fija

Análisis de bonos y mercados de deuda usando ETFs como proxy y web search para datos oficiales.

## Cuando usar
- "yield del bono español a 10 años"
- "curva de tipos EEUU"
- "spread de crédito investment grade"
- "compara bonos soberanos de España e Italia"
- "¿qué rentabilidad dan los bonos ahora?"
- "duración de mi cartera de bonos"

## Pasos

### 1. Bonos soberanos vía ETFs proxy
```python
import yfinance as yf

# ETFs de bonos soberanos como proxy
sovereigns = {
    'Bund Alemania 10Y': 'BUND.DE',     # iShares Germany Govt
    'Treasury US 10Y': 'IEF',            # iShares 7-10Y Treasury
    'Treasury US 20Y': 'TLT',            # iShares 20Y Treasury
    'Gilt UK 10Y': 'IGLT.L',            # iShares UK Gilts
    'JGB Japón 10Y': '2563.T',          # Japan Govt Bond ETF
}

for name, ticker in sovereigns.items():
    try:
        t = yf.Ticker(ticker)
        info = t.info
        print(f"{name}: {info.get('yield', 'N/D')}")
        hist = t.history(period="1y")
        print(f"  YTD: {(hist['Close'][-1]/hist['Close'][0]-1)*100:.1f}%")
    except:
        pass

# ETFs de crédito corporativo
credit = {
    'IG EUR': 'IEAC.AS',     # iShares EUR Corp Bond
    'HY EUR': 'IHYG.AS',     # iShares EUR High Yield
    'IG USD': 'LQD',          # iShares USD Invest Grade
    'HY USD': 'HYG',          # iShares USD High Yield
}
```

### 2. Yield curve vía web_search
Para curvas de tipos oficiales usar web_search — los datos en tiempo real no están disponibles vía yfinance:
- BCE: https://www.ecb.europa.eu/stats/financial_markets_and_interest_rates
- Fed: https://home.treasury.gov/resource-center/data-chart-center/interest-rates
- Tesoro España: https://www.tesoro.es/deuda-publica

### 3. Formato de salida
```
🏦 Mercado de Renta Fija | [Fecha]

📈 Curva de Tipos Soberanos
   2Y     5Y     10Y    20Y    30Y
   X.XX%  X.XX%  X.XX%  X.XX%  X.XX%

   Pendiente 2s10s: ±XX pb  ← aplanándose/empinándose
   Pendiente 10s30s: ±XX pb

🌍 Comparativa Soberana 10Y
   Alemania (Bund)  X.XX%
   EEUU (Treasury)  X.XX%
   España (Bono)    X.XX%  (+XX pb vs Bund)
   Italia (BTP)     X.XX%  (+XX pb vs Bund)
   Reino Unido      X.XX%

💳 Crédito Corporativo EUR
   IG: X.XX%  (spread +XX pb vs Bund)
   HY: X.XX%  (spread +XXX pb vs Bund)

📊 Rendimiento ETFs de Bonos (YTD)
   TLT (US 20Y):   ±X.X%
   IEF (US 7-10Y): ±X.X%
   LQD (US IG):    ±X.X%
```

### 4. Interpretación
- Curva invertida (2Y > 10Y) → señal de recesión
- Spreads elevados vs Bund → riesgo percibido del país
- HY spread ampliándose → aversión al riesgo
- Duración alta → sensibilidad a subidas de tipos

## Pitfalls
- Los ETFs de bonos no reflejan exactamente el yield del bono subyacente
- Datos en tiempo real de yields requieren terminal profesional (Bloomberg, Reuters)
- Usar web_search como fuente principal para yields oficiales
- Los spreads pueden variar intra-día
- Para análisis de duración/modified duration, advertir que es aproximado

## Regla de oro
**NUNCA** muestres el output crudo de las herramientas (print de Python, volcados de diccionarios, resultados de terminal). Usa las tools para obtener datos en silencio y luego redacta TÚ la respuesta formateada. El usuario solo debe ver tu texto final, nunca `{''longName'': ''...''}`.
