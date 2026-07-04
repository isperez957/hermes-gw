---
name: global-markets-snapshot
description: "Radiografía semanal/diaria de mercados globales: principales índices, bonos, divisas, commodities, volatilidad. Visión 360 del momento de mercado. Usar cuando el usuario pide un resumen de mercados, 'cómo están los mercados hoy', o contexto macro para tomar decisiones."
version: 1.0.0
---

# Global Markets Snapshot — Radiografía de Mercados

Resumen multi-activo del momento de mercado usando yfinance para datos en tiempo real.

## Cuando usar
- "cómo están los mercados hoy"
- "resumen semanal de mercados"
- "qué está pasando en las bolsas"
- "visión general antes del comité de inversión"
- "market snapshot para el family office"

## Activos a cubrir

### Índices
- IBEX 35: ^IBEX
- Euro Stoxx 50: ^STOXX50E
- S&P 500: ^GSPC
- Nasdaq: ^IXIC
- Nikkei 225: ^N225
- Shanghai: 000001.SS
- MSCI Emerging: EEM (ETF proxy)

### Bonos (ETFs proxy de yield)
- US 10Y: ^TNX
- Bund 10Y: ^BUND (o EWG1.DE)
- US High Yield: HYG
- EUR IG Credit: IEAC.AS

### Divisas
- EUR/USD: EURUSD=X
- DXY (índice dólar): DX-Y.NYB

### Volatilidad / Sentimiento
- VIX: ^VIX
- VSTOXX (volatilidad europea): ^V2TX (o VSTOXX.DE)
- Put/Call ratio: web_search

### Commodities clave
- Oro: GC=F
- Petróleo Brent: BZ=F
- Cobre: HG=F

## Formato de salida

🌍 Global Markets Snapshot — [Fecha]

📈 Renta Variable (rendimiento semanal)
   IBEX 35       XX,XXX  (+X.X%)  YTD: +XX%
   Euro Stoxx 50  X,XXX  (+X.X%)  YTD: +XX%
   S&P 500        X,XXX  (+X.X%)  YTD: +XX%
   Nasdaq         XX,XXX (+X.X%)  YTD: +XX%
   Nikkei         XX,XXX (+X.X%)  YTD: +XX%
   MSCI Emerging    XXX  (+X.X%)  YTD: +XX%

🏦 Renta Fija (yield / spread semanal)
   US Treasury 10Y   X.XX%  (+XXpb)
   Bund 10Y          X.XX%  (+XXpb)
   EUR HY spread     XXXpb  (+XXpb)
   US IG spread       XXpb  (+XXpb)

💱 Divisas
   EUR/USD 1.XXXX  (+X.X%)
   DXY     XXX.XX  (+X.X%)

⚡ Volatilidad
   VIX    XX.X  (umbral estrés: >25)
   VSTOXX XX.X

🛢️ Commodities
   Oro       X,XXX  (+X.X%)
   Brent     XX.XX  (+X.X%)
   Cobre     X.XX   (+X.X%)

📋 Resumen cualitativo (2-3 frases)
   • Contexto macro de la semana
   • Activo con mejor/peor comportamiento
   • Evento clave a vigilar (próximo dato macro, banco central, resultados)

## Regla de oro
NUNCA muestres el output crudo de las herramientas.
