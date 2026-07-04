---
name: sector-comparison
description: "Comparativa de empresas dentro de un mismo sector: valoración relativa, métricas clave, cuota de mercado. Usar cuando el usuario pregunta qué acción es mejor dentro de un sector, o quiere comparar competidores."
version: 1.0.0
---

# Sector Comparison — Comparativa Sectorial

Comparación de empresas del mismo sector usando `yfinance` para extraer métricas y presentarlas lado a lado.

## Cuando usar
- "compara Inditex y H&M"
- "¿cuál es mejor banco: BBVA o Santander?"
- "comparativa de eléctricas: Iberdrola vs Endesa vs Naturgy"
- "tech europeas vs americanas"
- "ranking de X en el sector Y"

## Pasos

### 1. Definir el universo comparable
Agrupar tickers por sector real. Ejemplos:
- **Banca española**: SAN.MC, BBVA.MC, CABK.MC, BKIA.MC, UNI.MC
- **Energía**: REP.MC, IBE.MC, NTGY.MC, ELE.MC
- **Retail/Moda**: ITX.MC (Inditex)
- **Telecos**: TEF.MC, CLNX.MC
- **Construcción**: ACS.MC, FER.MC
- **EEUU Tech**: AAPL, MSFT, GOOGL, META, AMZN

### 2. Extraer métricas comparables
```python
import yfinance as yf
import pandas as pd

tickers = ["SAN.MC", "BBVA.MC", "CABK.MC"]
data = []

for t in tickers:
    info = yf.Ticker(t).info
    data.append({
        'Ticker': t,
        'Nombre': info.get('longName', t),
        'Market Cap (B)': round(info.get('marketCap', 0) / 1e9, 1),
        'PER': info.get('trailingPE', 'N/D'),
        'P/B': info.get('priceToBook', 'N/D'),
        'ROE (%)': round(info.get('returnOnEquity', 0) * 100, 1) if info.get('returnOnEquity') else 'N/D',
        'Margen Neto (%)': round(info.get('profitMargins', 0) * 100, 1) if info.get('profitMargins') else 'N/D',
        'Div Yield (%)': round(info.get('dividendYield', 0) * 100, 2) if info.get('dividendYield') else 'N/D',
        'Deuda/Equity': info.get('debtToEquity', 'N/D'),
        'Precio': info.get('currentPrice', 'N/D'),
        'YTD (%)': round(info.get('ytdReturn', 0) * 100, 1) if info.get('ytdReturn') else 'N/D',
    })

df = pd.DataFrame(data)
```

### 3. Formato de salida
```
🏦 Comparativa: Banca Española

┌──────────┬────────┬───────┬──────┬──────┬──────┬──────────┬──────────┬──────────┐
│ Ticker   │ M.Cap  │ PER   │ P/B  │ ROE  │ Mg.N │ Div.Yield│ Deuda/Eq │ YTD      │
├──────────┼────────┼───────┼──────┼──────┼──────┼──────────┼──────────┼──────────┤
│ SAN.MC   │ 72.3B  │ 7.2x  │ 0.8x │ 11.2%│ 18.3%│ 3.8%     │ 210%     │ +12.4%   │
│ BBVA.MC  │ 58.1B  │ 6.8x  │ 1.1x │ 15.8%│ 22.1%│ 4.2%     │ 185%     │ +15.1%   │
│ CABK.MC  │ 32.5B  │ 8.1x  │ 0.9x │ 11.5%│ 16.7%│ 5.1%     │ 195%     │ +8.7%    │
└──────────┴────────┴───────┴──────┴──────┴──────┴──────────┴──────────┴──────────┘

🏆 Conclusiones:
• Mejor valoración (PER más bajo): BBVA (6.8x)
• Mayor rentabilidad (ROE): BBVA (15.8%)
• Mayor dividendo: CaixaBank (5.1%)
• Mayor crecimiento YTD: BBVA (+15.1%)
• Mejor relación calidad-precio: [conclusión]
```

### 4. Añadir contexto cualitativo
- Posición competitiva de cada una
- Tendencias del sector que afectan a todas
- Riesgos regulatorios comunes
- Si alguna destaca negativamente, explicar posible razón

## Pitfalls
- Comparar solo empresas del MISMO sector y geografía
- Market cap en moneda local; convertir si se mezclan EUR/USD
- Algunos campos pueden ser N/D para ciertas empresas — indicarlo
- No comparar bancos con tecnológicas; son métricas distintas
- Para sectores específicos añadir métricas propias (ej: CET1 para banca)

## Regla de oro
**NUNCA** muestres el output crudo de las herramientas (print de Python, volcados de diccionarios, resultados de terminal). Usa las tools para obtener datos en silencio y luego redacta TÚ la respuesta formateada. El usuario solo debe ver tu texto final, nunca `{''longName'': ''...''}`.
