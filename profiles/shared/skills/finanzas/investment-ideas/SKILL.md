---
name: investment-ideas
description: "Generador de ideas de inversión basado en criterios cuantitativos y cualitativos: screening por valoración, momentum, calidad, dividendos. Usar cuando el usuario pide ideas de inversión, screening de acciones, o 'en qué invertir ahora'."
version: 1.0.0
---

# Investment Ideas — Ideas de Inversión

Screening de ideas de inversión usando criterios cuantitativos y cualitativos.

## Cuando usar
- "ideas de inversión para este trimestre"
- "acciones infravaloradas en Europa"
- "empresas con alta rentabilidad por dividendo"
- "screening de small caps españolas con potencial"
- "en qué invertir 100k con perfil moderado"

## Metodología

### Screens predefinidos

**Value (infravaloradas)**
Criterios: PER < 12x, P/B < 1.5x, deuda/equity < 150%, FCF positivo.
Sectores típicos: bancos, energía, telecom, industriales.

**Quality (calidad)**
Criterios: ROE > 15%, margen neto > 10%, deuda/equity < 100%, crecimiento beneficios 5Y > 5%.
Sectores típicos: consumo defensivo, salud, tecnología madura.

**Momentum**
Criterios: precio > media 50d, media 50d > media 200d, retorno 6M > 15%, volumen creciente.
Válido para rotaciones sectoriales.

**Dividendos**
Criterios: yield > 3%, payout < 80%, crecimiento dividendo 5Y > 3%, deuda estable.
Sectores típicos: utilities, seguros, REITs, oil & gas.

**Small Caps con potencial (España)**
Tickers: DOM.MC, ALM.MC, GRE.MC, VID.MC, LOG.MC, ENC.MC, ...
Criterios adicionales: market cap < 2B, crecimiento ingresos > 5%, insider buying.

## Formato de salida

💡 Ideas de Inversión — [Perfil/Tema] | [Fecha]

🔍 Criterios del Screen
   [Criterios aplicados]

📋 Top Picks

   1. [Nombre] ([Ticker]) — [Sector]
      Precio: XX.XX | Market Cap: X.XB
      PER: XX.X | P/B: X.X | ROE: XX%
      Yield: X.X% | Deuda/Equity: XX%
      YTD: +XX% | Catalizador: [tesis]

   2. [Nombre] ([Ticker]) — [Sector]
      ...

   3. [Nombre] ([Ticker]) — [Sector]
      ...

⚠️ Riesgos comunes a estas ideas
   • [Riesgo macro que afecta al grupo]
   • [Riesgo regulatorio si aplica]
   • [Liquidez / tamaño si small caps]

📊 Contexto de mercado para esta estrategia
   [2-3 frases sobre por qué este screen es oportuno ahora]

⏱ Horizonte recomendado: [X-Y meses] para [value/momentum/dividendos]

## Disclaimer
Mencionar siempre: esto son IDEAS, no recomendaciones personalizadas.
Cada inversor debe evaluar su propia situación fiscal, horizonte y tolerancia al riesgo.

## Regla de oro
NUNCA muestres el output crudo de las herramientas.
