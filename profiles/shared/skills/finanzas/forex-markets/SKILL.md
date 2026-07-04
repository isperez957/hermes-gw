---
name: forex-markets
description: "Análisis de mercados de divisas: tipos de cambio, cruces, fortaleza relativa, carry trade. Usar cuando el usuario pregunta por el euro/dólar, cambio de divisas, o impacto de forex en inversiones."
version: 1.0.0
---

# Forex Markets — Mercados de Divisas

Tipos de cambio y análisis de divisas vía `yfinance`.

## Cuando usar
- "cambio euro dólar", "a cómo está el EUR/USD"
- "el euro está fuerte o débil"
- "impacto del tipo de cambio en mis inversiones"
- "mejor momento para cambiar euros a dólares"
- "carry trade yen-dólar"

## Tickers
| Par | Ticker | Descripción |
|-----|--------|-------------|
| EUR/USD | EURUSD=X | Euro vs Dólar |
| GBP/USD | GBPUSD=X | Libra vs Dólar |
| USD/JPY | USDJPY=X | Dólar vs Yen |
| EUR/GBP | EURGBP=X | Euro vs Libra |
| USD/CHF | USDCHF=X | Dólar vs Franco Suizo |
| AUD/USD | AUDUSD=X | Dólar Australiano |
| USD/CAD | USDCAD=X | Dólar Canadiense |
| NZD/USD | NZDUSD=X | Dólar Neozelandés |
| EUR/JPY | EURJPY=X | Euro vs Yen |
| USD/MXN | USDMXN=X | Dólar vs Peso Mexicano |
| USD/BRL | USDBRL=X | Dólar vs Real Brasileño |

## Pasos

```python
import yfinance as yf

# Pares principales
pairs = {
    'EUR/USD': 'EURUSD=X',
    'GBP/USD': 'GBPUSD=X',
    'USD/JPY': 'USDJPY=X',
    'EUR/GBP': 'EURGBP=X',
}

for name, ticker in pairs.items():
    t = yf.Ticker(ticker)
    info = t.info
    h = t.history(period="1mo")
    current = h['Close'].iloc[-1] if not h.empty else 'N/D'
    ytd = (current / h['Close'].iloc[0] - 1) * 100 if not h.empty and len(h) > 1 else 0
    
    # Rango del mes
    low = h['Low'].min() if not h.empty else 0
    high = h['High'].max() if not h.empty else 0
    
    print(f"{name}: {current:.4f} (30d: {ytd:+.2f}%, rango: {low:.4f}-{high:.4f})")

# DXY (índice del dólar) como contexto
dxy = yf.Ticker("DX-Y.NYB")
dxy_hist = dxy.history(period="1mo")
if not dxy_hist.empty:
    dxy_current = dxy_hist['Close'].iloc[-1]
    dxy_ytd = (dxy_current / dxy_hist['Close'].iloc[0] - 1) * 100
    print(f"\nDXY (Índice Dólar): {dxy_current:.2f} (30d: {dxy_ytd:+.2f}%)")
```

## Formato de salida
```
💱 Mercado de Divisas | [Fecha]

🌍 Principales Pares
   EUR/USD: 1.XXXX  (30d: ±X.X%)
   GBP/USD: 1.XXXX  (30d: ±X.X%)
   USD/JPY: XXX.XX  (30d: ±X.X%)
   EUR/GBP: 0.XXXX  (30d: ±X.X%)

📊 Índice Dólar (DXY): XXX.XX  (30d: ±X.X%)
   → Dólar [fortaleciéndose/debilitándose]

🇪🇺 Euro-Países LATAM
   EUR/MXN: XX.XX
   EUR/BRL: X.XX

💡 Contexto para inversor español:
   • EUR/USD a 1.XX: cartera USA [gana/pierde] X% por forex
   • Si tienes acciones americanas sin cobertura: [impacto]
   • Empresas exportadoras españolas beneficiadas/perjudicadas: [análisis]
```

## Pitfalls
- `yfinance` para forex a veces devuelve datos retrasados 15 min
- El ticker es `EURUSD=X` (sin barra), no `EUR/USD`
- Los pares que no incluyen USD son "cruces" (cross rates)
- Para análisis fundamental de divisas (tipos de interés relativos, balanza comercial) usar web_search adicional
- Mencionar siempre el impacto para un inversor en euros