---
name: company-financials
description: "Análisis profundo de estados financieros: balance, cuenta de resultados, cash flow, ratios. Usar cuando el usuario pide fundamentales detallados, análisis de balance, deuda, márgenes, o salud financiera de una empresa."
version: 1.0.0
---

# Company Financials — Análisis Fundamental

Análisis detallado de estados financieros usando `yfinance`.

## Cuando usar
- "analiza los fundamentales de X"
- "balance de X", "deuda de X", "márgenes de X"
- "cash flow de X", "salud financiera de X"
- "ratios de X": P/E, P/B, ROE, ROA, deuda/equity

## Tickers españoles
`.MC`: SAN.MC, BBVA.MC, ITX.MC, TEF.MC, REP.MC, IBE.MC, CABK.MC, ACS.MC, AENA.MC, FER.MC

## Pasos

### 1. Obtener datos
```python
import yfinance as yf
t = yf.Ticker("ITX.MC")
info = t.info
bs = t.balance_sheet      # balance
inc = t.financials        # cuenta de resultados
cf = t.cashflow           # cash flow
```

### 2. Presentar en formato ficha
```
📊 [Nombre] ([Ticker]) | [Sector] | [País]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 Valoración
   Market Cap: XX.XB [moneda]
   Enterprise Value: XX.XB
   PER (trailing): XX.X | Forward PER: XX.X
   P/B: X.X | P/S: X.X
   EV/EBITDA: XX.X

📈 Rentabilidad
   ROE: XX% | ROA: XX%
   Margen Bruto: XX% | Margen Operativo: XX% | Margen Neto: XX%

🏦 Balance
   Deuda Total: XX.XB
   Deuda/Equity: XX%
   Ratio Corriente: X.X
   Efectivo: XX.XB

💵 Flujo de Caja
   Free Cash Flow: XX.XB
   FCF Yield: XX%
   CapEx / Ventas: XX%

💸 Dividendo
   Dividend Yield: XX%
   Payout Ratio: XX%
   Crecimiento dividendo 5Y: XX%

📅 Precio
   Precio actual: XX.XX
   Máx 52s: XX.XX | Mín 52s: XX.XX
   Target analistas: XX.XX (potencial ±XX%)
```

### 3. Interpretación
Tras los datos, añade 2-3 frases de contexto:
- ¿Está cara/barata vs sector? (comparar PER, P/B con medias del sector)
- ¿Deuda preocupante o saludable?
- ¿FCF positivo/negativo? ¿Sostenible?
- Tendencia de márgenes

## Pitfalls
- Empresas pequeñas pueden no tener todos los campos
- Usar `.get()` con defaults: `info.get('trailingPE', 'N/D')`
- Datos en moneda local — especificar siempre
- Los quarterly reports pueden estar desactualizados
- Para empresas japonesas, datos pueden venir en JPY (especificar)

## Regla de oro
**NUNCA** muestres el output crudo de las herramientas (print de Python, volcados de diccionarios, resultados de terminal). Usa las tools para obtener datos en silencio y luego redacta TÚ la respuesta formateada. El usuario solo debe ver tu texto final, nunca `{''longName'': ''...''}`.
