---
name: commodities
description: "Consulta precios de materias primas: oro, plata, petróleo, gas natural, cobre, materias primas agrícolas. Usar cuando el usuario pregunta por commodities, materias primas, o mercados de recursos naturales."
version: 1.0.0
---

# Commodities — Materias Primas

Precios de commodities vía `yfinance` usando ETFs y futuros como proxy.

## Cuando usar
- "precio del oro", "a cómo está el petróleo"
- "análisis del cobre", "materias primas esta semana"
- "comparativa de metales preciosos"
- "futuros del gas natural"

## Tickers de referencia

### Metales Preciosos
| Commodity | ETF/Futuro | Ticker |
|-----------|-----------|--------|
| Oro | Futuro | GC=F |
| Oro | ETF físico | GLD |
| Plata | Futuro | SI=F |
| Plata | ETF físico | SLV |
| Platino | Futuro | PL=F |
| Paladio | Futuro | PA=F |

### Energía
| Commodity | ETF/Futuro | Ticker |
|-----------|-----------|--------|
| Crudo WTI | Futuro | CL=F |
| Crudo Brent | Futuro | BZ=F |
| Gas Natural | Futuro | NG=F |
| Gasolina | Futuro | RB=F |

### Metales Industriales
| Commodity | Ticker |
|-----------|--------|
| Cobre | HG=F |
| Aluminio | ALI=F |
| Níquel | NICKEL=F |
| Zinc | ZINC=F |

### Agrícolas
| Commodity | Ticker |
|-----------|--------|
| Trigo | ZW=F |
| Maíz | ZC=F |
| Soja | ZS=F |
| Café | KC=F |
| Azúcar | SB=F |

## Pasos

```python
import yfinance as yf
import pandas as pd

commodities = {
    'Oro': 'GC=F',
    'Plata': 'SI=F',
    'Crudo WTI': 'CL=F',
    'Brent': 'BZ=F',
    'Gas Natural': 'NG=F',
    'Cobre': 'HG=F',
}

for name, ticker in commodities.items():
    t = yf.Ticker(ticker)
    info = t.info
    h = t.history(period="1mo")
    if not h.empty:
        current = h['Close'].iloc[-1]
        month_ret = (current / h['Close'].iloc[0] - 1) * 100
        print(f"{name}: {current:.2f} (30d: {month_ret:+.1f}%)")
```

## Formato de salida
```
🛢️ Materias Primas | [Fecha]

💰 Metales Preciosos
   Oro:      X,XXX $/oz  (30d: ±X.X%)
   Plata:    XX.XX $/oz  (30d: ±X.X%)
   Platino:  XXX $/oz    (30d: ±X.X%)

🛢️ Energía
   WTI:      XX.XX $/bbl (30d: ±X.X%)
   Brent:    XX.XX $/bbl (30d: ±X.X%)
   Gas Nat:  X.XX $/MMBtu (30d: ±X.X%)

🏗️ Metales Industriales
   Cobre:    X.XX $/lb   (30d: ±X.X%)

🌾 Agrícolas
   Trigo:    XXX $/bushel
   Maíz:     XXX $/bushel
```

## Pitfalls
- Futuros tienen fecha de expiración — el ticker genérico (GC=F) usa el contrato más líquido
- Precios en USD — convertir a EUR si el usuario lo espera
- Commodities agrícolas muy volátiles — contextualizar
- Los futuros pueden tener horarios distintos a las acciones

## Regla de oro
**NUNCA** muestres el output crudo de las herramientas (print de Python, volcados de diccionarios, resultados de terminal). Usa las tools para obtener datos en silencio y luego redacta TÚ la respuesta formateada. El usuario solo debe ver tu texto final, nunca `{''longName'': ''...''}`.
